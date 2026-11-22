"""Unmocked hosted Studionet proof: deploy + semantic consensus + write/read state."""
import json
import hashlib
import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded

BASE = (
    "The founding DAO publishes transparent meeting minutes and an accessible "
    "archive of decisions for every active community member."
)
REPLACEMENT = (
    "The founding DAO publishes public meeting minutes within seven days of a vote "
    "and preserves a searchable archive of ratified decisions. Genesis voters, "
    "quorum, voting periods and execution delays remain governed by the immutable "
    "rules implemented by this contract."
)

def receipt_hash(receipt):
    if isinstance(receipt, dict):
        return str(receipt.get("hash") or receipt.get("transaction_hash") or "")
    return str(getattr(receipt, "hash", ""))


@pytest.mark.integration
def test_chartercycle_live_consensus(default_account, accounts):
    assert len(accounts) >= 3, "Live Studio must provide three distinct accounts"
    founders = [str(a.address) for a in accounts[:3]]
    assert len(set(x.lower() for x in founders)) == 3
    assert len(REPLACEMENT) >= 60
    factory = get_contract_factory("CharterCycle")
    contract = factory.deploy(
        args=[BASE, json.dumps(founders)],
        account=default_account,
        consensus_max_rotations=4,
    )
    print("CHARTERCYCLE_CONTRACT=" + str(contract.address), flush=True)
    charter = json.loads(contract.get_charter().call())
    assert int(charter["version"]) == 1
    assert int(charter["members"]) == 3
    assert charter["sha256"] == hashlib.sha256(BASE.encode("utf-8")).hexdigest()
    assert contract.is_member(args=[founders[1]]).call() is True

    proposer = contract.connect(account=default_account)
    tx = proposer.propose(
        args=["live_archive_v1", REPLACEMENT,
              "Public archival deadlines will make governance records easier to inspect."]
    ).transact(
        consensus_max_rotations=4,
        wait_interval=10000,
        wait_retries=100,
    )
    assert tx_execution_succeeded(tx), "Semantic proposal failed live consensus"
    print("CHARTERCYCLE_PROPOSE_TX=" + receipt_hash(tx), flush=True)
    state = json.loads(contract.get_proposal(args=["live_archive_v1"]).call())
    print("CHARTERCYCLE_REVIEW=" + str(state["review"]), flush=True)
    print("CHARTERCYCLE_STATUS=" + str(state["status"]), flush=True)
    assert state["review"] in ("COMPATIBLE", "CONFLICT", "UNDETERMINED")
    assert state["candidate_hash"] == hashlib.sha256(REPLACEMENT.encode()).hexdigest()
    assert state["status"] == ("VOTING" if state["review"] == "COMPATIBLE" else "BLOCKED")

    if state["status"] == "VOTING":
        vote_tx = proposer.vote(args=["live_archive_v1", True]).transact(
            wait_interval=10000, wait_retries=80
        )
        assert tx_execution_succeeded(vote_tx)
        print("CHARTERCYCLE_VOTE_TX=" + receipt_hash(vote_tx), flush=True)
        after = json.loads(contract.get_proposal(args=["live_archive_v1"]).call())
        assert int(after["yes"]) == 1
    print("CHARTERCYCLE_LIVE_PROOF=FINALIZED_READ_ASSERTIONS_PASS", flush=True)
