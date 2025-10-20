import typing
from ast import *
from copy import copy

from ordered_set import OrderedSet

from .rewrite_forbidden_overwrites import FORBIDDEN_NAMES
from ..type_inference import INITIAL_SCOPE
from ..util import CompilingNodeTransformer, CompilingNodeVisitor

"""
Rewrites all variable names to point to the definition in the nearest enclosing scope
"""


class ShallowNameDefCollector(CompilingNodeVisitor):
    step = "Collecting defined variable names"

    def __init__(self):
        self.vars = OrderedSet()

    def visit_Name(self, node: Name) -> None:
        if isinstance(node.ctx, Store):
            self.vars.add(node.id)

    def visit_ClassDef(self, node: ClassDef):
        self.vars.add(node.name)
        # methods will be put in global scope so add them now
        for attribute in node.body:
            if isinstance(attribute, FunctionDef):
                self.vars.add(attribute.name)
        # ignore the content (i.e. attribute names) of class definitions

    def visit_FunctionDef(self, node: FunctionDef):
        self.vars.add(node.name)
        # ignore the recursive stuff


class RewriteScoping(CompilingNodeTransformer):
    step = "Rewrite all variables to inambiguously point to the definition in the nearest enclosing scope"
    latest_scope_id: int
    scopes: typing.List[typing.Tuple[OrderedSet, int]]
    current_Self: typing.Tuple[str, str]

    def variable_scope_id(self, name: str) -> int:
        """find the id of the scope in which this variable is defined (closest to its usage)"""
        name = name
        for scope, scope_id in reversed(self.scopes):
            if name in scope:
                return scope_id
        raise NameError(
            f"free variable '{name}' referenced before assignment in enclosing scope"
        )

    def enter_scope(self):
        self.scopes.append((OrderedSet(), self.latest_scope_id))
        self.latest_scope_id += 1

    def exit_scope(self):
        self.scopes.pop()

    def set_variable_scope(self, name: str):
        self.scopes[-1][0].add(name)

    def map_name(self, name: str):
        scope_id = self.variable_scope_id(name)
        if scope_id == -1:
            # do not rewrite Dict, Union, etc
            return name
        return f"{name}_{scope_id}"

    def visit_Module(self, node: Module) -> Module:
        self.latest_scope_id = 0
        self.scopes = [(OrderedSet(INITIAL_SCOPE.keys() | FORBIDDEN_NAMES), -1)]
        node_cp = copy(node)
        self.enter_scope()
        # vars defined in this scope
        shallow_node_def_collector = ShallowNameDefCollector()
        for s in node.body:
            shallow_node_def_collector.visit(s)
        vars_def = shallow_node_def_collector.vars
        for var_name in vars_def:
            self.set_variable_scope(var_name)
        node_cp.body = [self.visit(s) for s in node.body]
        return node_cp

    def visit_Name(self, node: Name) -> Name:
        nc = copy(node)
        # setting is handled in either enclosing module or function
        if node.id == "Self":
            assert node.idSelf == self.current_Self[1]
            nc.idSelf_new = self.current_Self[0]
        nc.id = self.map_name(node.id)
        return nc

    def visit_ClassDef(self, node: ClassDef) -> ClassDef:
        cp_node = RecordScoper.scope(node, self)
        for i, attribute in enumerate(cp_node.body):
            if isinstance(attribute, FunctionDef):
                self.current_Self = (cp_node.name, cp_node.orig_name)
                cp_node.body[i] = self.visit_FunctionDef(attribute, method=True)
        return cp_node

    def visit_FunctionDef(self, node: FunctionDef, method: bool = False) -> FunctionDef:
        node_cp = copy(node)
        # setting is handled in either enclosing module or function
        node_cp.name = self.map_name(node.name) if not method else node.name
        self.enter_scope()
        node_cp.args = copy(node.args)
        node_cp.args.args = []
        # args are defined in this scope
        for a in node.args.args:
            a_cp = copy(a)
            self.set_variable_scope(a.arg)
            a_cp.arg = self.map_name(a.arg)
            a_cp.annotation = self.visit(a.annotation)
            node_cp.args.args.append(a_cp)
        node_cp.returns = self.visit(node.returns)
        # vars defined in this scope
        shallow_node_def_collector = ShallowNameDefCollector()
        for s in node.body:
            shallow_node_def_collector.visit(s)
        vars_def = shallow_node_def_collector.vars
        for var_name in vars_def:
            self.set_variable_scope(var_name)
        # map all vars and recurse
        node_cp.body = [self.visit(s) for s in node.body]
        self.exit_scope()
        return node_cp

    def visit_NoneType(self, node: None) -> None:
        return node


class RecordScoper(NodeTransformer):
    _scoper: RewriteScoping

    def __init__(self, scoper: RewriteScoping):
        self._scoper = scoper

    @classmethod
    def scope(cls, c: ClassDef, scoper: RewriteScoping) -> ClassDef:
        f = cls(scoper)
        return f.visit(c)

    def visit_ClassDef(self, c: ClassDef) -> ClassDef:
        node_cp = copy(c)
        node_cp.name = self._scoper.map_name(node_cp.name)
        return self.generic_visit(node_cp)

    def visit_AnnAssign(self, node: AnnAssign) -> AnnAssign:
        assert isinstance(
            node.target, Name
        ), "Record elements must have named attributes"
        node_cp = copy(node)
        node_cp.annotation = self._scoper.visit(node_cp.annotation)
        return node_cp
