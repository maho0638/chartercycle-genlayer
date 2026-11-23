"""READ ONLY: inspect Studio's stored transaction for failed finalize and prior success."""
import pytest
import json
from gltest import get_gl_client
FAILED="0x1bb7bd94870c7c9beb7b1ae805ab9d158809d9698cecc0927a86c7af759fa5a8"
PASSED="0x64fecea121383944bfdb8bef4a28be741c97d47fc4fec7c2de1e3829d7487b3e"
CONTRACT="0x5506E19b990cD9839659855AEC2fcA7c761867e8"
PROPOSAL="live_timelock_lifecycle_v1"

def simplify(a):
    if not isinstance(a,dict):
        return a
    kept=("status","statusName","hash","from","to","from_address","to_address",
          "blockNumber","gasUsed","gas","gaslimit","error","result","execution_result",
          "tx_execution_result","type","nonce","value","transactionHash",
          "fee_metadata","consensus_result","consensus_data","data","input_data")
    obj={k:a.get(k) for k in kept if k in a}
    for key in ("data","consensus_data","input_data"):
        if key in obj:
            val=obj[key]
            if isinstance(val,dict):
                obj[key]={q:str(v)[:300] for q,v in val.items() if q in
                          ("result","consensus_results","status","votes","execution_result","error")}
            else:
                obj[key]=str(val)[:250]
    return obj

@pytest.mark.integration
def test_readonly_inspect_outer_failure_and_simulation(default_account):
    cli=get_gl_client()
    for label,h in [("FAILED",FAILED),("PASSED",PASSED)]:
        for method in ("eth_getTransactionByHash","eth_getTransactionReceipt","gen_getTransactionStatus"):
            try:
                response=cli.provider.make_request(method,[h])
                print("AUDIT_"+label+"_"+method+"="+json.dumps(simplify(response.get("result")),default=str,sort_keys=True)[:3500],flush=True)
            except Exception as exc:
                print("AUDIT_"+label+"_"+method+"_ERROR="+str(exc)[:400],flush=True)
    try:
        sim=cli.simulate_write_contract(address=CONTRACT,function_name="finalize",
                                        account=default_account,args=[PROPOSAL])
        print("AUDIT_SIMULATE_WRITE="+str(sim)[:2200],flush=True)
    except Exception as exc:
        print("AUDIT_SIMULATE_WRITE_UNAVAILABLE="+str(exc)[:500],flush=True)
    print("AUDIT_INSPECTION_NO_SIGNING",flush=True)
