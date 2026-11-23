"""Single controlled Studionet finalize submission with EVM receipt diagnostics.

Uses official genlayer-py pinned by requirements.txt. Does not redeploy or
alter the governance rules. One transaction only, and only if VOTING+quorum+time.
"""
import json
import time
import pytest
from gltest import get_gl_client, get_contract_factory
from genlayer_py.contracts import actions

CONTRACT="0x5506E19b990cD9839659855AEC2fcA7c761867e8"
PROPOSAL="live_timelock_lifecycle_v1"
CLOSES=1795462930
READY_AT=1795549330

@pytest.mark.integration
def test_finalize_once_with_diagnostics(default_account, monkeypatch):
    cli=get_gl_client()
    contract=get_contract_factory("CharterCycle").build_contract(CONTRACT,account=default_account)
    p=json.loads(contract.get_proposal(args=[PROPOSAL]).call())
    ch=json.loads(contract.get_charter().call())
    assert p["id"]==PROPOSAL and p["base_version"]==1
    assert int(p["yes"])==2 and int(p["no"])==0
    assert int(p["closes"])==CLOSES
    assert int(ch["version"])==1
    assert cli.w3.eth.chain_id==61999
    assert int(cli.w3.eth.get_block("latest")["timestamp"])>=CLOSES
    print("FIX_CONTRACT="+CONTRACT,flush=True)
    print("FIX_STATUS_BEFORE="+p["status"],flush=True)
    if p["status"] in ("TIMELOCK","ENACTED"):
        print("FIX_NO_SEND_ALREADY_FINALIZED",flush=True)
        return
    assert p["status"]=="VOTING"

    original_prepare=actions._prepare_transaction
    def prepared_with_headroom(*args,**kwargs):
        tx=original_prepare(*args,**kwargs)
        estimate=int(tx["gas"],16) if isinstance(tx["gas"],str) else int(tx["gas"])
        new_gas=max(estimate*2,estimate+250000)
        assert 0<estimate<new_gas<=3000000
        tx["gas"]=hex(new_gas)
        print("FIX_SDK_ESTIMATE="+str(estimate),flush=True)
        print("FIX_OUTER_GAS_LIMIT="+str(new_gas),flush=True)
        return tx
    monkeypatch.setattr(actions,"_prepare_transaction",prepared_with_headroom)

    original_request=cli.provider.make_request
    record={}
    def capture_request(method,params):
        result=original_request(method,params)
        if method=="eth_sendRawTransaction":
            record["outer"]=result.get("result")
            print("FIX_OUTER_EVM_HASH="+str(record["outer"]),flush=True)
        return result
    monkeypatch.setattr(cli.provider,"make_request",capture_request)

    try:
        # One signed submission, no retry here. The SDK waits for EVM receipt.
        inner=cli.write_contract(address=CONTRACT,function_name="finalize",
            account=default_account,consensus_max_rotations=4,args=[PROPOSAL])
        record["inner"]=inner
        print("FIX_GENLAYER_TX_HASH="+str(inner),flush=True)
    except Exception as error:
        print("FIX_SUBMISSION_ERROR="+str(error)[:500],flush=True)
        outer=record.get("outer")
        if outer:
            for method in ("eth_getTransactionReceipt","eth_getTransactionByHash","gen_getTransactionStatus"):
                try:
                    rsp=original_request(method,[outer])
                    body=rsp.get("result")
                    if isinstance(body,dict):
                        body={k:body.get(k) for k in ("status","gasUsed","cumulativeGasUsed",
                            "gas","hash","transactionHash","from","to","type","blockNumber") if k in body}
                    print("FIX_DIAG_"+method+"="+str(body)[:1300],flush=True)
                except Exception as cause:
                    print("FIX_DIAG_"+method+"_ERR="+str(cause)[:300],flush=True)
        raise

    assert isinstance(inner,str) and inner.startswith("0x")
    status=""
    for attempt in range(45):
        rsp=original_request("gen_getTransactionStatus",[inner])
        status=str(rsp.get("result"))
        if status in ("FINALIZED","ACCEPTED"):
            break
        time.sleep(2)
    print("FIX_CONSENSUS_STATUS="+status,flush=True)
    assert status in ("ACCEPTED","FINALIZED"),"Consensus not yet accepted; inspect inner tx"
    after=json.loads(contract.get_proposal(args=[PROPOSAL]).call())
    print("FIX_FINAL_PROPOSAL="+json.dumps({k:after.get(k) for k in ("status","yes","no","ready_at")}),flush=True)
    assert after["status"]=="TIMELOCK"
    assert int(after["ready_at"])==READY_AT
    print("FIX_FINALIZE_SUCCESS",flush=True)
