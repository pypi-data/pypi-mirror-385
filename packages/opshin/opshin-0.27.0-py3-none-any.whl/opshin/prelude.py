from opshin.ledger.api_v3 import *


@dataclass(unsafe_hash=True)
class Nothing(PlutusData):
    """
    Nothing, can be used to signify non-importance of a parameter to a function

    Example value: Nothing()
    """

    # The maximum constructor ID for simple cbor types, chosen to minimize probability of collision while keeping the corresponding cbor small
    CONSTR_ID = 6


@dataclass(unsafe_hash=True)
class Token(PlutusData):
    """
    A token, represented by policy id and token name
    """

    CONSTR_ID = 0
    policy_id: PolicyId
    token_name: TokenName


# Used to indicate that this contract does not expect a redeemer
NoRedeemer = Nothing

### Optimized methods for handling tokens at addresses


def all_tokens_unlocked_from_address(
    txins: List[TxInInfo], address: Address, token: Token
) -> int:
    """Returns how many tokens of specified type are unlocked from given address"""
    return sum(
        [
            txi.resolved.value.get(token.policy_id, {b"": 0}).get(token.token_name, 0)
            for txi in txins
            if txi.resolved.address == address
        ]
    )


def all_tokens_locked_at_address_with_datum(
    txouts: List[TxOut], address: Address, token: Token, output_datum: OutputDatum
) -> int:
    """Returns how many tokens of specified type are locked at then given address with the specified datum"""
    return sum(
        [
            txo.value.get(token.policy_id, {b"": 0}).get(token.token_name, 0)
            for txo in txouts
            if txo.address == address and txo.datum == output_datum
        ]
    )


def all_tokens_locked_at_address(
    txouts: List[TxOut], address: Address, token: Token
) -> int:
    """Returns how many tokens of specified type are locked at the given address"""
    return sum(
        [
            txo.value.get(token.policy_id, {b"": 0}).get(token.token_name, 0)
            for txo in txouts
            if txo.address == address
        ]
    )


def resolve_spent_utxo(inputs: List[TxInInfo], purpose: Spending) -> TxOut:
    """Returns the UTxO whose spending should be validated"""
    return [txi.resolved for txi in inputs if txi.out_ref == purpose.tx_out_ref][0]


def resolve_datum_unsafe(txout: TxOut, tx_info: TxInfo) -> BuiltinData:
    """
    Returns the datum attached to a given transaction output, independent of whether it was inlined or embedded.
    Raises an exception if no datum was attached.
    """
    attached_datum = txout.datum
    if isinstance(attached_datum, SomeOutputDatumHash):
        res = tx_info.datums[attached_datum.datum_hash]
    elif isinstance(attached_datum, SomeOutputDatum):
        res = attached_datum.datum
    else:
        # no datum attached
        assert False, "No datum was attached to the given transaction output"
    return res


def resolve_datum(
    txout: TxOut, tx_info: TxInfo
) -> Union[SomeOutputDatum, NoOutputDatum]:
    """
    Returns SomeOutputDatum with the datum attached to a given transaction output,
    independent of whether it was inlined or embedded, if there was an attached datum.
    Otherwise it returns NoOutputDatum.
    """
    attached_datum = txout.datum
    if isinstance(attached_datum, SomeOutputDatumHash):
        res: Union[SomeOutputDatum, NoOutputDatum] = SomeOutputDatum(
            tx_info.datums[attached_datum.datum_hash]
        )
    else:
        res: Union[SomeOutputDatum, NoOutputDatum] = attached_datum
    return res


def own_spent_utxo(txins: List[TxInInfo], p: Spending) -> TxOut:
    # This throws an assertion error if the txout was not found
    for txi in txins:
        if txi.out_ref == p.tx_out_ref:
            return txi.resolved
    assert (
        False
    ), "The UTxO being spent from this script address was not found in the transaction inputs"
    return txi.resolved


def own_policy_id(own_spent_utxo: TxOut) -> PolicyId:
    """
    obtain the policy id for which this contract can validate minting/burning
    """
    cred = own_spent_utxo.address.payment_credential
    if isinstance(cred, ScriptCredential):
        policy_id = cred.credential_hash
    # This throws a name error if the credential is not a ScriptCredential instance
    return policy_id


def own_address(own_policy_id: PolicyId) -> Address:
    """
    Computes the spending script address corresponding to the given policy ID
    """
    return Address(ScriptCredential(own_policy_id), NoStakingCredential())


def token_present_in_inputs(token: Token, inputs: List[TxInInfo]):
    """
    Returns whether the given token is spent in one of the inputs of the transaction
    """
    return any(
        [
            x.resolved.value.get(token.policy_id, {b"": 0}).get(token.token_name, 0) > 0
            for x in inputs
        ]
    )


def own_datum(context: ScriptContext) -> Union[SomeOutputDatum, NoOutputDatum]:
    """
    Returns the datum attached to the UTxO being spent from this script address.
    Returns NoOutputDatum if no datum was attached.
    """
    purpose = context.purpose
    assert isinstance(purpose, Spending)
    own_utxo = own_spent_utxo(context.transaction.inputs, purpose)
    datum = resolve_datum(own_utxo, context.transaction)
    return datum


def own_datum_unsafe(context: ScriptContext) -> Anything:
    """
    Returns the datum attached to the UTxO being spent from this script address.
    Raises an exception if no datum was attached.
    """
    purpose: Spending = context.purpose
    own_utxo = own_spent_utxo(context.transaction.inputs, purpose)
    datum = resolve_datum_unsafe(own_utxo, context.transaction)
    return datum
