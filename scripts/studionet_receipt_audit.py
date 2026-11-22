"""Read-only Studionet proof audit. Never sends or signs transactions."""
import json
import urllib.request
import pathlib
from datetime import datetime, timezone

RPC = "https://studio.genlayer.com/api"
TX = {
    "CharterCycle/propose": "0xc553d173b6f4758056fa4467909aa8ddf24399b92f5de18bf6232af7d14ec775",
    "CharterCycle/vote": "0x96185dadda625dfab9390fbcdb34104952e44683f4b167e182f93cc6b714f278",
    "QuestForge/create": "0xfd5ee42ce771a2438dc8905588306e4600793f8f6d19e87e2fbde47dfdb1c29e",
    "QuestForge/join": "0xb39b952d048fd0d3847bfb8a4e0ad4406b49cd11a87b7fe1da02e0a535cee2c9",
    "QuestForge/solve": "0x5e0ded8bbe753cdfdf571d3cf9870a814039f6af293f2582bfe2a9206327f8df",
    "QuestForge/scout": "0xf646b841e0f6ad070973527145f2117cc94ee41334f3a7be42286839fbcb423f",
}

def rpc(method, params):
    payload = json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":1}).encode()
    req = urllib.request.Request(RPC, data=payload,
        headers={"Content-Type":"application/json","User-Agent":"genlayer-readonly-proof-audit"})
    with urllib.request.urlopen(req, timeout=40) as response:
        doc = json.loads(response.read())
    if "error" in doc:
        raise RuntimeError(method + ": " + str(doc["error"]))
    return doc["result"]

def main():
    snapshot = {
       "timestamp_utc": datetime.now(timezone.utc).isoformat(),
       "network": "studionet",
       "rpc": RPC,
       "transactions": {}
    }
    chain = rpc("eth_chainId", [])
    snapshot["chain_id"] = int(chain, 16) if isinstance(chain,str) and chain.startswith("0x") else int(chain)
    print("STUDIONET_CHAIN_ID=" + str(snapshot["chain_id"]), flush=True)
    assert snapshot["chain_id"] == 61999, "Wrong network; stop"
    for label, h in TX.items():
        status = rpc("gen_getTransactionStatus", [{"txId": h}])
        receipt = rpc("gen_getTransactionReceipt", [{"txId": h}])
        detail = rpc("gen_getTransactionData", [{"txId": h}])
        data = {
            "tx_hash":h,
            "status":status.get("status"),
            "status_code":status.get("statusCode"),
            "receipt_status":receipt.get("statusName"),
            "receipt_result":receipt.get("resultName", receipt.get("result")),
            "leader_execution":receipt.get("txExecutionResultName", receipt.get("txExecutionResult")),
            "rounds":[{
                "round":r.get("round"),
                "votes_committed":r.get("votesCommitted"),
                "votes_revealed":r.get("votesRevealed"),
                "result":r.get("result"),
                "validators":len(r.get("roundValidators") or [])
            } for r in receipt.get("roundData",[])],
            "data_result":detail.get("resultName", detail.get("result")),
            "data_execution":detail.get("txExecutionResultName", detail.get("txExecutionResult")),
        }
        snapshot["transactions"][label] = data
        print("PROOF_" + label.replace("/","_").upper() + "=" + json.dumps(data,sort_keys=True),flush=True)
        assert str(data["status_code"]) in {"5","7"}, "Transaction is not accepted or finalized"
        assert str(data["data_result"]).lower() in ("majorityagree","1"), "No majority agreement"
        assert str(data["data_execution"]).lower() in ("finishedwithreturn","1"), "Leader execution not successful"
    file=pathlib.Path("studionet_status_audit.json")
    file.write_text(json.dumps(snapshot,indent=2,sort_keys=True)+"\n")
    print("ALL_SIX_CHAIN_RECEIPTS_VALIDATED; FINALITY_STATUS_IN_JSON", flush=True)

if __name__=="__main__":
    main()
