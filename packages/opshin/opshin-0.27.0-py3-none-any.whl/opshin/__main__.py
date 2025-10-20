import inspect

import argparse
import io
import logging
import os
import tempfile
import uuid
from contextlib import redirect_stdout

import cbor2
import enum
import importlib
import json
import pathlib
import sys
import typing
import ast

import pycardano

import uplc
import uplc.ast
from uplc.cost_model import PlutusVersion

from . import (
    compiler,
    builder,
    prelude,
    __version__,
    __copyright__,
    Purpose,
    PlutusContract,
)
from .util import CompilerError, data_from_json, OPSHIN_LOG_HANDLER
from .prelude import ScriptContext
from .compiler_config import *
from uplc import cost_model


class Command(enum.Enum):
    compile_pluto = "compile_pluto"
    compile = "compile"
    eval = "eval"
    parse = "parse"
    eval_uplc = "eval_uplc"
    build = "build"
    lint = "lint"


def parse_uplc_param(param: str):
    if param.startswith("{"):
        try:
            return uplc.ast.data_from_json_dict(json.loads(param))
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid parameter for contract passed, expected JSON value, got {param}"
            ) from e
        except Exception as e:
            raise ValueError(
                f"Expected parameter for contract to be in valid Plutus data JSON format, got {param}"
            ) from e
    else:
        try:
            return uplc.ast.data_from_cbor(bytes.fromhex(param))
        except Exception as e:
            raise ValueError(
                "Expected hexadecimal CBOR representation of plutus datum but could not transform hex string to bytes."
            ) from e


def parse_plutus_param(annotation, param: str):
    try:
        if param.startswith("{"):
            try:
                param_dict = json.loads(param)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid parameter for contract passed, expected json value, got {param}"
                ) from e
            return plutus_data_from_json(annotation, param_dict)
        else:
            try:
                param_bytes = bytes.fromhex(param)
            except ValueError as e:
                raise ValueError(
                    "Expected hexadecimal CBOR representation of plutus datum but could not transform hex string to bytes."
                ) from e
            return plutus_data_from_cbor(annotation, param_bytes)
    except ValueError as e:
        raise ValueError(
            f"Could not parse parameter {param} as type {annotation}. Please provide the parameter either as JSON or CBOR (in hexadecimal notation). Detailed error: {e}"
        ) from e


def plutus_data_from_json(annotation: typing.Type, x: dict):
    try:
        if annotation == int:
            return int(x["int"])
        if annotation == bytes:
            return bytes.fromhex(x["bytes"])
        if annotation is None:
            return None
        if isinstance(annotation, typing._GenericAlias):
            # Annotation is a List or Dict
            if annotation._name == "List":
                annotation_ann = annotation.__dict__["__args__"][0]
                return [plutus_data_from_json(annotation_ann, k) for k in x["list"]]
            if annotation._name == "Dict":
                annotation_key, annotation_val = annotation.__dict__["__args__"]
                return {
                    plutus_data_from_json(
                        annotation_key, d["k"]
                    ): plutus_data_from_json(annotation_val, d["v"])
                    for d in x["map"]
                }
            if annotation.__origin__ == typing.Union:
                for ann in annotation.__dict__["__args__"]:
                    try:
                        return plutus_data_from_json(ann, x)
                    except (pycardano.DeserializeException, KeyError, ValueError):
                        pass
                raise ValueError(
                    f"Could not find matching type for {x} in {annotation}"
                )
            if annotation == pycardano.Datum:
                if "int" in x:
                    return int(x["int"])
                if "bytes" in x:
                    return bytes.fromhex(x["bytes"])
                if "constructor" in x:
                    return pycardano.RawCBOR(
                        uplc.ast.plutus_cbor_dumps(uplc.ast.data_from_json_dict(x))
                    )
                if "list" in x:
                    return [
                        plutus_data_from_json(pycardano.Datum, k) for k in x["list"]
                    ]
                if "map" in x:
                    return {
                        plutus_data_from_json(
                            pycardano.Datum, d["k"]
                        ): plutus_data_from_json(pycardano.Datum, d["v"])
                        for d in x["map"]
                    }
        if issubclass(annotation, pycardano.PlutusData):
            return annotation.from_dict(x)
    except (KeyError, ValueError, pycardano.DeserializeException):
        raise ValueError(
            f"Annotation {annotation} does not match provided plutus datum {json.dumps(x)}"
        )


def plutus_data_from_cbor(annotation: typing.Type, x: bytes):
    try:
        if annotation in (int, bytes):
            res = cbor2.loads(x)
            if not isinstance(res, annotation):
                raise ValueError(
                    f"Expected {annotation} but got {type(x)} from {x.hex()}"
                )
            return res
        if annotation is None:
            if not x == cbor2.dumps(None):
                raise ValueError(f"Expected None but got {x.hex()}")
            return None
        if isinstance(annotation, typing._GenericAlias):
            # Annotation is a List or Dict
            if annotation.__origin__ == list:
                annotation_ann = annotation.__dict__["__args__"][0]
                return [
                    plutus_data_from_cbor(annotation_ann, cbor2.dumps(k))
                    for k in cbor2.loads(x)
                ]
            if annotation.__origin__ == dict:
                annotation_key, annotation_val = annotation.__dict__["__args__"]
                return {
                    plutus_data_from_cbor(
                        annotation_key, cbor2.dumps(k)
                    ): plutus_data_from_cbor(annotation_val, cbor2.dumps(v))
                    for k, v in cbor2.loads(x).items()
                }
            if annotation.__origin__ == typing.Union:
                for ann in annotation.__dict__["__args__"]:
                    try:
                        return plutus_data_from_cbor(ann, x)
                    except (pycardano.DeserializeException, ValueError):
                        pass
                raise ValueError(
                    f"Could not find matching type for {x.hex()} in {annotation}"
                )
        if issubclass(annotation, pycardano.PlutusData):
            return annotation.from_cbor(x)
    except (KeyError, ValueError, pycardano.DeserializeException):
        raise ValueError(
            f"Annotation {annotation} does not match provided plutus datum {x.hex()}"
        )


def check_params(
    command: Command,
    validator_args: typing.List[typing.Tuple[str, typing.Type]],
    return_type: typing.Type,
    validator_params: typing.List,
    parameters: int,
):
    num_onchain_params = 1
    onchain_params = validator_args[-num_onchain_params:]
    param_types = validator_args[:-num_onchain_params]
    if return_type is not None:
        print(
            f"Warning: validator returns {return_type}, but it is recommended to return None. In PlutusV3, validators that do not return None always fail. This is most likely not what you want."
        )

    required_onchain_parameters = 1
    assert (
        len(onchain_params) == required_onchain_parameters
    ), f"""\
The validator must expect {required_onchain_parameters} parameters at evaluation (on-chain), but was specified to have {len(onchain_params)}.
Make sure the validator expects exactly the script context (ScriptContext)."""

    if command in (Command.eval, Command.eval_uplc):
        assert len(validator_params) == len(param_types) + len(
            onchain_params
        ), f"The validator expects {len(param_types) + len(onchain_params)} parameters for evaluation, but only got {len(validator_params)}."
    else:
        assert (
            len(param_types) - len(validator_params) == parameters
        ), f"""\
The validator is specified to expect {len(param_types)-len(validator_params)} parameters for parameterization ({','.join(x[0] for x in param_types)}, of which {len(validator_params)} are bound by additional arguments), but the command line arguments indicate {parameters} parameters (default is 0).
Note that PlutusV3 validatators expect only the ScriptContext as on-chain parameter, so non-parameterized contracts should have only 1 parameter ({onchain_params[0][0]}).
Make sure the number of parameters passed matches the number of parameters expected by the validator.
Either remove extra parameters or specify them by passing `--parameters {len(param_types)-len(validator_params)}`.
"""
    assert (
        onchain_params[-1][1] == ScriptContext
    ), f"Last parameter of the validator ({onchain_params[-1][0]}) has to be of type ScriptContext, but is {onchain_params[-1][1].__name__}."
    return onchain_params, param_types


def perform_command(args):
    # generate the compiler config
    compiler_config = DEFAULT_CONFIG
    compiler_config = compiler_config.update(OPT_CONFIGS[args.opt_level])
    overrides = {}
    for k in ARGPARSE_ARGS.keys():
        if getattr(args, k) is not None:
            overrides[k] = getattr(args, k)
    compiler_config = compiler_config.update(CompilationConfig(**overrides))
    # configure logging
    if args.verbose:
        OPSHIN_LOG_HANDLER.setLevel(logging.DEBUG)
    lib = args.lib
    number_parameters = args.parameters

    # execute the command
    command = Command(args.command)
    input_file = args.input_file if args.input_file != "-" else sys.stdin
    # read and import the contract
    with open(input_file, "r") as f:
        source_code = f.read()
    with tempfile.TemporaryDirectory(prefix="build") as tmpdir:
        tmp_input_file = pathlib.Path(tmpdir).joinpath(f"__tmp_opshin{uuid.uuid4()}.py")
        with tmp_input_file.open("w") as fp:
            fp.write(source_code)
        sys.path.append(str(pathlib.Path(tmp_input_file).parent.absolute()))
        try:
            sc = importlib.import_module(pathlib.Path(tmp_input_file).stem)
        except Exception as e:
            # replace the traceback with an error pointing to the input file
            raise SyntaxError(
                f"Could not import the input file as python module. Make sure the input file is valid python code. Error: {e}",
            ) from e
        sys.path.pop()
    # load the passed parameters if not a lib
    try:
        argspec = inspect.signature(sc.validator if lib is None else getattr(sc, lib))
    except AttributeError:
        raise AssertionError(
            f"Contract has no function called '{'validator' if lib is None else lib}'. Make sure the compiled contract contains one function called 'validator'."
        )
    annotations = [
        (x.name, x.annotation or prelude.Anything) for x in argspec.parameters.values()
    ]
    return_annotation = (
        argspec.return_annotation
        if argspec.return_annotation is not argspec.empty
        else prelude.Anything
    )
    parsed_params = []
    uplc_params = []
    for i, (c, a) in enumerate(zip(annotations, args.args)):
        try:
            uplc_param = parse_uplc_param(a)
        except ValueError as e:
            raise ValueError(
                f"Could not parse parameter {i} ('{a}') as UPLC data. Please provide the parameter either as JSON or CBOR (in hexadecimal notation). Detailed error: {e}"
            ) from None
        uplc_params.append(uplc_param)
        try:
            param = parse_plutus_param(c[1], a)
        except ValueError as e:
            raise ValueError(
                f"Could not parse parameter {i} ('{a}') as type {c[1]}. Please provide the parameter either as JSON or CBOR (in hexadecimal notation). Detailed error: {e}"
            ) from None
        parsed_params.append(param)
    if lib is None:
        onchain_params, param_types = check_params(
            command,
            annotations,
            return_annotation,
            parsed_params,
            number_parameters,
        )
        assert (
            onchain_params
        ), "The validator function must have at least one on-chain parameter. You can also add `_:None`."

    py_ret = Command.eval
    if command == Command.eval:
        print("Python execution started")
        with redirect_stdout(open(os.devnull, "w")):
            try:
                py_ret = sc.validator(*parsed_params)
            except Exception as e:
                py_ret = e
        command = Command.eval_uplc

    source_ast = compiler.parse(source_code, filename=input_file)

    if command == Command.parse:
        print("Parsed successfully.")
        return

    try:
        code = compiler.compile(
            source_ast,
            filename=input_file,
            validator_function_name="validator" if lib is None else lib,
            # do not remove dead code when compiling a library - none of the code will be used
            config=compiler_config,
        )
    except CompilerError as c:
        # Generate nice error message from compiler error
        if not isinstance(c.node, ast.Module):
            source_seg = ast.get_source_segment(source_code, c.node)
            start_line = c.node.lineno - 1
            end_line = start_line + len(source_seg.splitlines())
            source_lines = "\n".join(source_code.splitlines()[start_line:end_line])
            pos_in_line = source_lines.find(source_seg)
        else:
            start_line = 0
            pos_in_line = 0
            source_lines = source_code.splitlines()[0]

        overwrite_syntaxerror = (
            len("SyntaxError: ") * "\b" if command != Command.lint else ""
        )
        err = SyntaxError(
            f"""\
{overwrite_syntaxerror}{c.orig_err.__class__.__name__}: {c.orig_err}
Note that opshin errors may be overly restrictive as they aim to prevent code with unintended consequences.
""",
            (
                args.input_file,
                start_line + 1,
                pos_in_line,
                source_lines,
            ),
            # we remove chaining so that users to not see the internal trace back,
        )
        err.orig_err = c.orig_err
        raise err

    if command == Command.compile_pluto:
        print(code.dumps())
        return
    code = pluthon.compile(code, config=compiler_config)

    # apply parameters from the command line to the contract (instantiates parameterized contract!)
    code = code.term
    # UPLC lambdas may only take one argument at a time, so we evaluate by repeatedly applying
    for d in uplc_params:
        code = uplc.ast.Apply(code, d)
    code = uplc.ast.Program((1, 0, 0), code)

    if command == Command.compile:
        print(code.dumps())
        return

    if command == Command.build:
        if lib is not None:
            raise ValueError(
                "Cannot build a library. Please remove the --lib flag when building a contract."
            )
        if args.output_directory == "":
            if args.input_file == "-":
                print(
                    "Please supply an output directory if no input file is specified."
                )
                exit(-1)
            target_dir = pathlib.Path("build") / pathlib.Path(input_file).stem
        else:
            target_dir = pathlib.Path(args.output_directory)
        built_code = builder._build(code)
        script_arts = PlutusContract(
            built_code,
            datum_type=onchain_params[0] if len(onchain_params) == 3 else None,
            redeemer_type=onchain_params[1 if len(onchain_params) == 3 else 0],
            parameter_types=param_types,
            purpose=(Purpose.any,),
            title=pathlib.Path(input_file).stem,
        )
        script_arts.dump(target_dir)

        print(f"Wrote script artifacts to {target_dir}/")
        return
    if command == Command.eval_uplc:
        print("UPLC execution started")
        assert isinstance(code, uplc.ast.Program)
        raw_ret = uplc.eval(
            code,
            cek_machine_cost_model=cost_model.default_cek_machine_cost_model_plutus_v3(),
            builtin_cost_model=cost_model.default_builtin_cost_model_plutus_v3(),
        )
        print("------LOGS--------")
        if raw_ret.logs:
            for log in raw_ret.logs:
                print(" > " + log)
        else:
            print("No logs")
        print("------COST--------")
        print(f"CPU: {raw_ret.cost.cpu} | MEM: {raw_ret.cost.memory}")
        if isinstance(raw_ret.result, Exception):
            print("----EXCEPTION-----")
            ret = raw_ret.result
        else:
            print("-----SUCCESS------")
            ret = uplc.dumps(raw_ret.result)
        print(str(ret), end="")
        if not isinstance(py_ret, Command):
            print(" (Python: " + str(py_ret) + ")", end="")
        print()


def parse_args():
    a = argparse.ArgumentParser(
        description="An evaluator and compiler from python into UPLC. Translate imperative programs into functional quasi-assembly. Flags allow setting fine-grained compiler options. All flags can be turned off via -fno-<flag>."
    )
    a.add_argument(
        "command",
        type=str,
        choices=Command.__members__.keys(),
        help="The command to execute on the input file.",
    )
    a.add_argument(
        "input_file", type=str, help="The input program to parse. Set to - for stdin."
    )
    a.add_argument(
        "--lib",
        const="validator",
        default=None,
        nargs="?",
        type=str,
        help="Indicates that the input file should compile to a generic function, reusable by other contracts (not a smart contract itself). Discards corresponding typechecks. An optional name of the function to export can be given, by default it is validator. Use -fwrap_input and -fwrap_output to control whether the function expects or returns PlutusData (otherwise BuiltIn).",
    )
    a.add_argument(
        "-o",
        "--output-directory",
        default="",
        type=str,
        help="The output directory for artefacts of the build command. Defaults to the filename of the compiled contract. of the compiled contract.",
    )
    a.add_argument(
        "args",
        nargs="*",
        default=[],
        help="Input parameters for the validator (parameterizes the contract for compile/build, passes the values for eval/eval_uplc). Either json or CBOR notation.",
    )
    a.add_argument(
        "--output-format-json",
        action="store_true",
        help="Changes the output of the Linter to a json format.",
    )
    a.add_argument(
        "--parameters",
        type=int,
        default=0,
        help="Number of parameters that the contract supports. If not specified, 0 is assumed (i.e., the contract only expects the ScriptContext).",
    )
    a.add_argument(
        "--version",
        action="version",
        version=f"opshin {__version__} {__copyright__}",
    )
    a.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    a.add_argument(
        "--recursion-limit",
        default=max(sys.getrecursionlimit(), 4000),
        help="Modify the recursion limit (necessary for larger UPLC programs)",
        type=int,
    )
    for k, v in ARGPARSE_ARGS.items():
        alts = v.pop("__alts__", [])
        type = v.pop("type", None)
        if type is None:
            a.add_argument(
                f"-f{k.replace('_', '-')}",
                *alts,
                **v,
                action="store_true",
                dest=k,
                default=None,
            )
            a.add_argument(
                f"-fno-{k.replace('_', '-')}",
                action="store_false",
                help=argparse.SUPPRESS,
                dest=k,
                default=None,
            )
        else:
            a.add_argument(
                f"-f{k.replace('_', '-')}",
                *alts,
                **v,
                type=type,
                dest=k,
                default=None,
            )

    a.add_argument(
        f"-O",
        type=int,
        help=f"Optimization level from 0 (no optimization) to 3 (aggressive optimization). Defaults to 1.",
        default=2,
        choices=range(len(OPT_CONFIGS)),
        dest="opt_level",
    )
    return a.parse_args()


def main():
    args = parse_args()
    sys.setrecursionlimit(args.recursion_limit)
    if Command(args.command) != Command.lint:
        OPSHIN_LOG_HANDLER.setFormatter(
            logging.Formatter(
                f"%(levelname)s for {args.input_file}:%(lineno)d %(message)s"
            )
        )
        perform_command(args)
    else:
        OPSHIN_LOG_HANDLER.stream = sys.stdout
        if args.output_format_json:
            OPSHIN_LOG_HANDLER.setFormatter(
                logging.Formatter(
                    '{"line":%(lineno)d,"column":%(col_offset)d,"error_class":"%(levelname)s","message":"%(message)s"}'
                )
            )
        else:
            OPSHIN_LOG_HANDLER.setFormatter(
                logging.Formatter(
                    args.input_file
                    + ":%(lineno)d:%(col_offset)d:%(levelname)s: %(message)s"
                )
            )

        try:
            perform_command(args)
        except Exception as e:
            error_class_name = e.__class__.__name__
            message = str(e)
            if isinstance(e, SyntaxError):
                start_line = e.lineno
                pos_in_line = e.offset
                if hasattr(e, "orig_err"):
                    error_class_name = e.orig_err.__class__.__name__
                    message = str(e.orig_err)
            else:
                start_line = 1
                pos_in_line = 1
            if args.output_format_json:
                print(
                    convert_linter_to_json(
                        line=start_line,
                        column=pos_in_line,
                        error_class=error_class_name,
                        message=message,
                    )
                )
            else:
                print(
                    f"{args.input_file}:{start_line}:{pos_in_line}: {error_class_name}: {message}"
                )


def convert_linter_to_json(
    line: int,
    column: int,
    error_class: str,
    message: str,
):
    # output in lists
    return json.dumps(
        [
            {
                "line": line,
                "column": column,
                "error_class": error_class,
                "message": message,
            }
        ]
    )


if __name__ == "__main__":
    main()
