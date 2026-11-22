"""OFFICIAL GenLayer direct-mode suite; requires genlayer-test, not the local fake."""
import json


def addr(wallet):
    return '0x' + wallet.hex()


BASE = 'Members maintain transparent votes and publish an understandable public archive of ratified policies.'
NEXT = 'Members maintain a transparent public archive and publish all successful amendments and voting counts.'


def test_charter_cycle_real_direct_lifecycle(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    direct_vm.sender = direct_alice
    c = direct_deploy('contracts/charter_cycle.py', BASE, json.dumps([
        addr(direct_alice), addr(direct_bob), addr(direct_charlie)
    ]))
    assert json.loads(c.get_charter())['version'] == 1
    direct_vm.mock_llm(r'(?s).*proposed DAO charter.*', json.dumps({'verdict':'COMPATIBLE'}))
    c.propose('proposal_1', NEXT, 'This amendment improves public record transparency.')
    p = json.loads(c.get_proposal('proposal_1'))
    assert p['status'] == 'VOTING'
    assert direct_vm.run_validator() is True
    c.vote('proposal_1', True)
    direct_vm.sender = direct_bob
    c.vote('proposal_1', True)
    with direct_vm.expect_revert('Already voted'):
        c.vote('proposal_1', True)
    assert json.loads(c.get_proposal('proposal_1'))['yes'] == 2


def test_charter_cycle_validator_mismatch(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    direct_vm.sender = direct_alice
    c = direct_deploy('contracts/charter_cycle.py', BASE, json.dumps([
        addr(direct_alice), addr(direct_bob), addr(direct_charlie)
    ]))
    direct_vm.mock_llm(r'(?s).*proposed DAO charter.*', json.dumps({'verdict': 'COMPATIBLE'}))
    c.propose('proposal_2', NEXT, 'This amendment improves public record transparency.')
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r'(?s).*proposed DAO charter.*', json.dumps({'verdict': 'CONFLICT'}))
    assert direct_vm.run_validator() is False


def test_charter_cycle_real_direct_timelock_enact(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    """Real SDK fixture test; must pass before release (not run in this environment)."""
    direct_vm.warp('2026-11-01T00:00:00Z')
    direct_vm.sender = direct_alice
    c = direct_deploy('contracts/charter_cycle.py', BASE, json.dumps([
        addr(direct_alice), addr(direct_bob), addr(direct_charlie)
    ]))
    direct_vm.mock_llm(r'(?s).*proposed DAO charter.*', json.dumps({'verdict':'COMPATIBLE'}))
    c.propose('proposal_3', NEXT, 'This amendment improves public record transparency.')
    c.vote('proposal_3', True)
    direct_vm.sender = direct_bob
    c.vote('proposal_3', True)
    direct_vm.warp('2026-11-02T00:00:00Z')
    c.finalize('proposal_3')
    assert json.loads(c.get_proposal('proposal_3'))['status'] == 'TIMELOCK'
    with direct_vm.expect_revert('Timelock active'):
        c.enact('proposal_3')
    direct_vm.warp('2026-11-03T00:00:00Z')
    c.enact('proposal_3')
    assert json.loads(c.get_charter())['version'] == 2
    with direct_vm.expect_revert('Proposal not approved'):
        c.enact('proposal_3')


def test_charter_cycle_real_direct_unqualified_vote_rejected(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, direct_accounts):
    direct_vm.sender = direct_alice
    c = direct_deploy('contracts/charter_cycle.py', BASE, json.dumps([
        addr(direct_alice), addr(direct_bob), addr(direct_charlie)
    ]))
    direct_vm.mock_llm(r'(?s).*proposed DAO charter.*', json.dumps({'verdict':'COMPATIBLE'}))
    c.propose('proposal_4', NEXT, 'This amendment improves public record transparency.')
    outsider = next(w for w in direct_accounts if w not in (direct_alice, direct_bob, direct_charlie))
    direct_vm.sender = outsider
    with direct_vm.expect_revert('Not a genesis member'):
        c.vote('proposal_4', True)
    assert json.loads(c.get_proposal('proposal_4'))['yes'] == 0


def test_charter_cycle_real_direct_fail_closed(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    direct_vm.sender = direct_alice
    c = direct_deploy('contracts/charter_cycle.py', BASE, json.dumps([
        addr(direct_alice), addr(direct_bob), addr(direct_charlie)
    ]))
    direct_vm.mock_llm(r'(?s).*proposed DAO charter.*', json.dumps({'verdict':'UNDETERMINED'}))
    c.propose('proposal_5', NEXT, 'This amendment improves public record transparency.')
    assert json.loads(c.get_proposal('proposal_5'))['status'] == 'BLOCKED'
    with direct_vm.expect_revert('Proposal not open'):
        c.vote('proposal_5', True)


def test_charter_periodic_creation_capacity_recovers(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    """Actual GenLayer SDK storage model: rate cap renews next period."""
    direct_vm.warp('2026-11-01T00:00:00Z')
    direct_vm.sender = direct_alice
    c = direct_deploy('contracts/charter_cycle.py', BASE, json.dumps([
        addr(direct_alice), addr(direct_bob), addr(direct_charlie)
    ]))
    direct_vm.mock_llm(r'(?s).*proposed DAO charter.*', json.dumps({'verdict': 'COMPATIBLE'}))
    c.propose('weekly_a', NEXT, 'The public archive should remain transparent and accessible.')
    c.propose('weekly_b', NEXT, 'The public archive should remain transparent and accessible.')
    with direct_vm.expect_revert('Founder proposal rate limit exceeded'):
        c.propose('weekly_c', NEXT, 'The public archive should remain transparent and accessible.')
    direct_vm.warp('2026-11-09T00:00:00Z')
    c.propose('weekly_c', NEXT, 'The public archive should remain transparent and accessible.')
    assert c.get_proposal_count() == 3


def test_charter_mark_approved_alternative_stale(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    direct_vm.warp('2026-11-01T00:00:00Z')
    direct_vm.sender = direct_alice
    c = direct_deploy('contracts/charter_cycle.py', BASE, json.dumps([
        addr(direct_alice), addr(direct_bob), addr(direct_charlie)
    ]))
    direct_vm.mock_llm(r'(?s).*proposed DAO charter.*', json.dumps({'verdict': 'COMPATIBLE'}))
    c.propose('competing_a', NEXT, 'A better transparent archive for all existing founders.')
    c.propose('competing_b', NEXT, 'A second candidate with different wording and clear records.')
    for sender in [direct_alice, direct_bob]:
        direct_vm.sender = sender
        c.vote('competing_a', True)
        c.vote('competing_b', True)
    direct_vm.warp('2026-11-02T00:00:00Z')
    c.finalize('competing_a')
    c.finalize('competing_b')
    direct_vm.warp('2026-11-03T00:00:00Z')
    c.enact('competing_a')
    direct_vm.sender = direct_charlie
    c.archive_obsolete('competing_b')
    assert json.loads(c.get_proposal('competing_b'))['status'] == 'STALE'
    with direct_vm.expect_revert('Proposal not approved'):
        c.enact('competing_b')
