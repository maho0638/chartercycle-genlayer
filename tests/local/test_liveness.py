"""Regression cases for governance liveness; uses fake GenLayer SDK."""
import json
from pathlib import Path
import pytest
from sdk_stub import install_and_load, FakeUserError

A='0x'+'11'*20
B='0x'+'22'*20
C='0x'+'33'*20
BASE='Genesis members keep public archives and provide transparent votes for carefully reviewed constitutional amendments.'
NEXT='Genesis members will publish comprehensive and transparent voting records and archive all ratified amendments.'
SECOND='The community will archive ratified constitutions and publish readable summaries of each successful vote.'

@pytest.fixture
def ctx():
    sdk,mod=install_and_load('charter_liveness',str(Path(__file__).resolve().parents[2]/'contracts/charter_cycle.py'))
    sdk.message.sender_address=A
    c=mod.CharterCycle(BASE,json.dumps([A,B,C]))
    clock=[10_000]
    c._now=lambda:clock[0]
    return sdk,mod,c,clock

def propose(ctx,name,txt=NEXT,verdict='COMPATIBLE'):
    sdk,mod,c,clock=ctx
    sdk.nondet.answers += [{'verdict':verdict}]*2
    c.propose(name,txt,'A careful explanation of the archival policy adjustment.')

def test_periodic_quota_recovers_capacity_without_reusing_ids(ctx):
    sdk,mod,c,t=ctx
    propose(ctx,'amend_one')
    propose(ctx,'amend_two',SECOND)
    with pytest.raises(FakeUserError,match='rate limit'):
        c.propose('amend_three',NEXT,'Clear rationale about archives and transparent records')
    assert c.get_proposal_count()==2
    t[0]+=mod.PROPOSAL_PERIOD_SECONDS
    propose(ctx,'amend_three')
    assert c.get_proposal_count()==3
    assert json.loads(c.get_proposal('amend_one'))['candidate_hash']!= ''

def test_blocked_proposals_are_not_permanent_global_shutdown(ctx):
    sdk,mod,c,t=ctx
    propose(ctx,'reject_one',verdict='CONFLICT')
    propose(ctx,'reject_two',verdict='UNDETERMINED')
    assert json.loads(c.get_proposal('reject_two'))['status']=='BLOCKED'
    t[0]+=mod.PROPOSAL_PERIOD_SECONDS
    propose(ctx,'recover_one')
    assert json.loads(c.get_proposal('recover_one'))['status']=='VOTING'

def test_permissionless_archive_clears_approved_competing_proposal(ctx):
    sdk,mod,c,t=ctx
    propose(ctx,'amend_one')
    propose(ctx,'amend_two',SECOND)
    for member in [A,B]:
        sdk.message.sender_address=member
        c.vote('amend_one',True)
        c.vote('amend_two',True)
    t[0]+=mod.VOTING_SECONDS
    c.finalize('amend_one')
    c.finalize('amend_two')
    t[0]+=mod.TIMELOCK_SECONDS
    c.enact('amend_one')
    sdk.message.sender_address='0x'+'44'*20
    c.archive_obsolete('amend_two')
    assert json.loads(c.get_proposal('amend_two'))['status']=='STALE'
    assert c.get_proposal_count()==2
    with pytest.raises(FakeUserError,match='Proposal not approved'):
        c.enact('amend_two')
    with pytest.raises(FakeUserError,match='already terminal'):
        c.archive_obsolete('amend_two')

def test_old_open_proposal_can_be_archived_before_closure(ctx):
    sdk,mod,c,t=ctx
    propose(ctx,'amend_one')
    propose(ctx,'amend_two',SECOND)
    for member in [A,B]:
        sdk.message.sender_address=member
        c.vote('amend_one',True)
    t[0]+=mod.VOTING_SECONDS
    c.finalize('amend_one')
    t[0]+=mod.TIMELOCK_SECONDS
    c.enact('amend_one')
    c.archive_obsolete('amend_two')
    assert json.loads(c.get_proposal('amend_two'))['status']=='STALE'
    with pytest.raises(FakeUserError,match='Proposal not open'):
        c.vote('amend_two',True)

def test_healthy_timelock_is_not_archivable(ctx):
    sdk,mod,c,t=ctx
    propose(ctx,'amend_one')
    for member in [A,B]:
        sdk.message.sender_address=member
        c.vote('amend_one',True)
    t[0]+=mod.VOTING_SECONDS
    c.finalize('amend_one')
    with pytest.raises(FakeUserError,match='not obsolete'):
        c.archive_obsolete('amend_one')
