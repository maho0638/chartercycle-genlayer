"""READ-ONLY diagnosis of EVM submission failure for existing Studionet finalize.

Does NOT sign, send, mutate, deploy or pay gas. Never prints private account keys.
"""
import json
import pytest
from gltest import get_gl_client, get_contract_factory
from genlayer_py.contracts import actions
from genlayer_py.abi import calldata
from genlayer_py.abi.transactions import serialize
from genlayer_py.contracts.utils import make_calldata_object

CONTRACT="0x5506E19b990cD9839659855AEC2fcA7c761867e8"
PROPOSAL="live_timelock_lifecycle_v1"

@pytest.mark.integration
def test_read_only_finalize_evm_diagnostic(default_account):
    cli=get_gl_client()
    c=get_contract_factory("CharterCycle").build_contract(CONTRACT,account=default_account)
    p=json.loads(c.get_proposal(args=[PROPOSAL]).call())
    charter=json.loads(c.get_charter().call())
    print("DIAG_CONTRACT="+CONTRACT,flush=True)
    print("DIAG_PROPOSAL="+json.dumps({key:p.get(key) for key in ("status","yes","no","closes","ready_at","base_version")},sort_keys=True),flush=True)
    print("DIAG_CHARTER_VERSION="+str(charter.get("version")),flush=True)
    print("DIAG_ACCOUNT="+str(default_account.address),flush=True)
    print("DIAG_BALANCE_WEI="+str(cli.w3.eth.get_balance(default_account.address)),flush=True)
    print("DIAG_CHAIN_ID="+str(cli.w3.eth.chain_id),flush=True)
    print("DIAG_BLOCK_TIMESTAMP="+str(cli.w3.eth.get_block("latest")["timestamp"]),flush=True)
    cli.initialize_consensus_smart_contract()
    payload=serialize([calldata.encode(make_calldata_object(method="finalize",args=[PROPOSAL],kwargs=None)),False])
    encoded=actions._encode_add_transaction_data(self=cli,sender_account=default_account,
        recipient=CONTRACT,consensus_max_rotations=4,data=payload)
    args={"from":default_account.address,"to":cli.chain.consensus_main_contract["address"],
          "data":encoded,"value":"0x0"}
    for method,params in (
        ("eth_call",[args,"latest"]),
        ("eth_estimateGas",[args]),
    ):
        try:
            result=cli.provider.make_request(method,params)
            print("DIAG_"+method.upper()+"="+str(result)[:1200],flush=True)
        except Exception as error:
            print("DIAG_"+method.upper()+"_ERROR="+str(error)[:1200],flush=True)
    try:
        prepared=actions._prepare_transaction(self=cli,sender=default_account.address,
            recipient=cli.chain.consensus_main_contract["address"],data=encoded)
        print("DIAG_SDK_GAS="+str(prepared.get("gas")),flush=True)
        print("DIAG_SDK_FEES="+str({k:prepared.get(k) for k in ("maxFeePerGas","maxPriorityFeePerGas")}),flush=True)
    except Exception as error:
        print("DIAG_PREPARE_ERROR="+str(error)[:1000],flush=True)
    assert p["status"] in ("VOTING","TIMELOCK","ENACTED"), "unexpected onchain proposal state"
    print("DIAG_DONE_READ_ONLY",flush=True)
