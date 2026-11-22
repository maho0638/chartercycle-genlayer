"""Live quorum initialization for a real 24h vote + 24h execution delay.

Uses fresh temporary accounts IN ONE RUN, because gltest's default accounts
are randomly generated per process. Later finalize/enact are permissionless.
"""
import json
from datetime import datetime,timezone
import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded

BASE="Founding members maintain an open public archive of ratified community decisions and transparent voting records."
UPDATED="Founding members maintain an open public archive of ratified community decisions and transparent voting records. Adopt an additional regular monthly publication of decision summaries for improved accessibility."
ID="live_timelock_lifecycle_v1"

def transact(fn,args):
    receipt=fn(args=args).transact(wait_interval=10000,wait_retries=120,consensus_max_rotations=4)
    assert tx_execution_succeeded(receipt)
    tx=receipt.get("hash") or receipt.get("transaction_hash") if isinstance(receipt,dict) else str(getattr(receipt,"hash",""))
    assert str(tx).startswith("0x") and len(str(tx))==66
    return str(tx)

@pytest.mark.integration
def test_live_proposal_approved_quorum_before_wait(default_account,accounts):
    assert len(accounts)>=3
    members=[str(a.address) for a in accounts[:3]]
    assert str(default_account.address).lower()==members[0].lower(), "Deployer not first genesis member"
    assert len(set(m.lower() for m in members))==3
    c=get_contract_factory("CharterCycle").deploy(args=[BASE,json.dumps(members)],account=default_account,consensus_max_rotations=4)
    print("TIMELOCK_CONTRACT="+str(c.address),flush=True)
    t=transact(c.connect(account=accounts[0]).propose,[ID,UPDATED,
          "A monthly public summary helps founding members audit the accessible archive."])
    print("TIMELOCK_PROPOSE_TX="+t,flush=True)
    p=json.loads(c.get_proposal(args=[ID]).call())
    print("TIMELOCK_REVIEW="+p["review"],flush=True)
    assert p["review"]=="COMPATIBLE" and p["status"]=="VOTING", "Real AI did not approve amendment"
    for i in range(2):
        h=transact(c.connect(account=accounts[i]).vote,[ID,True])
        print("TIMELOCK_VOTE_"+str(i+1)+"_TX="+h,flush=True)
    p=json.loads(c.get_proposal(args=[ID]).call())
    assert p["yes"]==2 and p["no"]==0
    assert p["status"]=="VOTING"
    assert int(p["closes"])==int(p["opened"])+86400
    assert int(p["base_version"])==1
    ready=int(p["closes"])+86400
    print("TIMELOCK_OPENED="+str(p["opened"]),flush=True)
    print("TIMELOCK_CLOSES="+str(p["closes"]),flush=True)
    print("TIMELOCK_READY_AT="+str(ready),flush=True)
    print("TIMELOCK_CLOSES_UTC="+datetime.fromtimestamp(int(p["closes"]),tz=timezone.utc).isoformat(),flush=True)
    print("TIMELOCK_READY_UTC="+datetime.fromtimestamp(ready,tz=timezone.utc).isoformat(),flush=True)
    print("TIMELOCK_STATUS=VOTING_YES_2_OF_3_FINALIZED_READBACK_PASS",flush=True)
