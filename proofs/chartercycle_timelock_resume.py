"""Permissionless finalization/enactment for the already-validated 2-of-3 Studionet proposal.

No new contract deployment. No new LLM questions. Source address and dates are
pinned to the 2026-11-22 real live quorum proof; fee-bearing calls only when due.
"""
import json
from datetime import datetime,timezone
import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded

CONTRACT="0x5506E19b990cD9839659855AEC2fcA7c761867e8"
PROPOSAL="live_timelock_lifecycle_v1"
CLOSES=1795462930
READY=1795549330

def send(method):
    receipt=method(args=[PROPOSAL]).transact(wait_interval=10000,wait_retries=100)
    assert tx_execution_succeeded(receipt)
    h=receipt.get("hash") or receipt.get("transaction_hash") if isinstance(receipt,dict) else str(getattr(receipt,"hash",""))
    assert str(h).startswith("0x") and len(str(h))==66
    print("TIMELOCK_RESUME_TX="+str(h),flush=True)
    return str(h)

@pytest.mark.integration
def test_complete_due_timelock_stages(default_account):
    factory=get_contract_factory("CharterCycle")
    c=factory.build_contract(CONTRACT,account=default_account)
    p=json.loads(c.get_proposal(args=[PROPOSAL]).call())
    assert p["id"]==PROPOSAL
    assert p["base_version"]==1
    assert int(p["yes"])==2 and int(p["no"])==0
    assert p["closes"]==CLOSES
    print("TIMELOCK_RESUME_CONTRACT="+CONTRACT,flush=True)
    print("TIMELOCK_RESUME_OPENED="+str(p["opened"]),flush=True)
    print("TIMELOCK_RESUME_STATUS_BEFORE="+str(p["status"]),flush=True)
    now=int(datetime.now(timezone.utc).timestamp())
    assert now>=CLOSES, "Voting not closed; do not spend gas"
    if p["status"]=="VOTING":
        send(c.finalize)
        p=json.loads(c.get_proposal(args=[PROPOSAL]).call())
        assert p["status"]=="TIMELOCK" and int(p["ready_at"])==READY
        print("TIMELOCK_RESUME_FINALIZED=TIMELOCK",flush=True)
    assert p["status"] in ("TIMELOCK","ENACTED")
    if now>=READY and p["status"]=="TIMELOCK":
        send(c.enact)
        p=json.loads(c.get_proposal(args=[PROPOSAL]).call())
        assert p["status"]=="ENACTED"
        ch=json.loads(c.get_charter().call())
        assert int(ch["version"])==2
        assert ch["sha256"]==p["candidate_hash"]
        print("TIMELOCK_RESUME_ENACTED=VERSION_2",flush=True)
    else:
        print("TIMELOCK_RESUME_WAIT_READY_UTC="+datetime.fromtimestamp(READY,timezone.utc).isoformat(),flush=True)
    print("TIMELOCK_RESUME_STATUS_AFTER="+p["status"],flush=True)
