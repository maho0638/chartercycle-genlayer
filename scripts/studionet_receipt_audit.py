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
    "CharterCycle/quorum_propose": "0x64fecea121383944bfdb8bef4a28be741c97d47fc4fec7c2de1e3829d7487b3e",
    "CharterCycle/quorum_vote1": "0x2e556010a7feab3cdad4dca3dd72e18b037bf4674914bb64e8f919d172cc83c9",
    "CharterCycle/quorum_vote2": "0x005d0f9ae1f6f70dd299caebfac4135253dcd6f8f467cb42b15aca053769297a",
    "FullWin/create": "0xfff83a152548ccf22e0e4a17fbd6452c3394be6042390239d38094a640e9b598",
    "FullWin/join": "0x5aba39db722200f2d40cfabf102bb39321d8847de25ecfac4d229d84258b44c1",
    "FullWin/solve0": "0xd663a74e5a85c93f684fced68999ff113bc52504a21013e38fadfea48716ba6f",
    "FullWin/solve1": "0xdfc2c495bdc586cbf4b2e8223fbe17eade9d629af6f9e39582c7cb48c2eb4fc8",
    "FullWin/scout2": "0xc0fbe93160f3b7efb262d02b470bd7c2182f68c87af986d19e519fd1c0bcf389",
    "FullWin/scout3": "0x709dab247c7ba0d99b4069d3344da8501ca76ef521f772bed15601aac666e5cf",
    "FullWin/solve4": "0xfc8fca8c6d656fa44dc50182bb7d55da87dd8f39611b3b0f7fd29845e24ce27b",
}

def rpc(method, params):
    payload = json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":1}).encode()
    req = urllib.request.Request(RPC, data=payload,
        headers={"Content-Type":"application/json","User-Agent":"genlayer-readonly-proof-audit"})
    with urllib.request.urlopen(req, timeout=40) as response:
        doc = json.loads(response.read())
    if "error" in doc:
        raise RuntimeError(method + ": " + str(doc["error"])[:320])
    return doc["result"]

def network_query(method, h):
    # Studionet currently exposes a legacy JSON-RPC transport that accepts
    # a bare tx hash, whereas the newer documented node accepts {txId}.
    errors=[]
    for params in ([h], [{"txId":h}]):
        try:
            return rpc(method,params)
        except Exception as error:
            errors.append(str(error))
    raise RuntimeError(method + " failed for "+h+": "+"; ".join(errors))

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
        status = network_query("gen_getTransactionStatus", h)
        data={"tx_hash":h,"raw_status":status}
        for method,field in (("gen_getTransactionReceipt","receipt"),
                             ("gen_getTransactionData","tx_data")):
            try:
                result=network_query(method,h)
                if isinstance(result,dict):
                    data[field]={
                        k:result.get(k) for k in
                        ("status","statusName","result","resultName",
                         "txExecutionResult","txExecutionResultName")
                        if k in result
                    }
                    if field == "receipt":
                        data["rounds"] = [
                          {"round": x.get("round"), "votes_committed":x.get("votesCommitted"),
                           "votes_revealed":x.get("votesRevealed"), "result":x.get("result"),
                           "validators":len(x.get("roundValidators") or [])}
                          for x in result.get("roundData",[]) if isinstance(x,dict)
                        ]
                else:
                    data[field]=str(result)[:300]
            except Exception as error:
                data[field+"_unavailable"]=str(error)[:320]
        if label in ("CharterCycle/propose", "CharterCycle/quorum_propose", "QuestForge/solve") or label.startswith("FullWin/solve"):
            try:
                transaction=rpc("eth_getTransactionByHash",[h])
                if isinstance(transaction,dict):
                    consensus=transaction.get("consensus_data") or {}
                    votes=consensus.get("votes") or {}
                    if isinstance(votes,dict):
                        counts={}
                        for vote in votes.values():
                            key=str(vote).lower()
                            counts[key]=counts.get(key,0)+1
                        data["validator_vote_counts"]=counts
                        data["validator_vote_total"]=len(votes)
                    data["consensus_round"]=str(transaction.get("status",""))
                    data["consensus_history_rounds"]=len(
                        (transaction.get("consensus_history") or {}).get("consensus_results") or []
                    )
                    data["vote_source"]="eth_getTransactionByHash / consensus_data.votes"
            except Exception as error:
                data["validator_votes_unavailable"]=str(error)[:300]
        snapshot["transactions"][label]=data
        print("PROOF_"+label.replace("/","_").upper()+"="+json.dumps(data,sort_keys=True),flush=True)
        status_name=status.get("status", status.get("statusName")) if isinstance(status,dict) else status
        status_num=status.get("statusCode",status.get("status")) if isinstance(status,dict) else None
        if str(status_name).lower() not in ("accepted","finalized") and str(status_num) not in ("5","7"):
            raise RuntimeError("Not accepted/finalized: "+label+" "+str(status))
    file=pathlib.Path("studionet_status_audit.json")
    file.write_text(json.dumps(snapshot,indent=2,sort_keys=True)+"\\n")
    print("ALL_RECORDED_RECEIPT_STATUSES_CONFIRMED; FINALITY_IS_REPORTED_EXACTLY", flush=True)

if __name__ == "__main__":
    main()
