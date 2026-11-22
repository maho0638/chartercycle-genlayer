import json
import pathlib
import unittest
from sdk_stub import install_and_load, FakeUserError, FakeConsensusError

PATH = pathlib.Path(__file__).resolve().parents[2] / 'contracts' / 'charter_cycle.py'
A = '0x' + '11' * 20
B = '0x' + '22' * 20
C = '0x' + '33' * 20
D = '0x' + '44' * 20
X = '0x' + '55' * 20
ORIGINAL = 'Members approve rule changes, keep accurate public records, and share responsibility for transparent decisions.'
REPLACEMENT = 'Members publish their approved changes in clear language and preserve transparent public records for all votes.'
OTHER = 'Members jointly maintain an accessible archive of every ratified rule and the results of voting.'

class CharterCycleTests(unittest.TestCase):
    def setUp(self):
        self.sdk, self.mod = install_and_load('charter_cycle_local', str(PATH))
        self.sdk.message.sender_address = A
        self.clock = [1000]
        self.contract = self.mod.CharterCycle(ORIGINAL, json.dumps([A, B, C]))
        self.contract._now = lambda: self.clock[0]

    def reply(self, status='COMPATIBLE', validator=None):
        if validator is None: validator = status
        self.sdk.nondet.answers.extend([{'verdict': status}, {'verdict': validator}])

    def propose(self, ident='rule_01', text=REPLACEMENT, status='COMPATIBLE'):
        self.reply(status)
        self.contract.propose(ident, text, 'Explain the revised record-keeping policy.')
        return json.loads(self.contract.get_proposal(ident))

    def test_genesis_membership_and_initial_version(self):
        ch = json.loads(self.contract.get_charter())
        self.assertEqual(ch['version'], 1)
        self.assertEqual(ch['members'], 3)
        self.assertTrue(self.contract.is_member(A.upper().replace('0X','0x')))
        self.assertFalse(self.contract.is_member(X))

    def test_reject_duplicate_genesis_address_mixed_case(self):
        with self.assertRaises(FakeUserError):
            self.mod.CharterCycle(ORIGINAL, json.dumps([A, A.upper().replace('0X','0x'), B]))

    def test_reject_deployer_outside_genesis(self):
        with self.assertRaises(FakeUserError):
            self.mod.CharterCycle(ORIGINAL, json.dumps([B, C, D]))

    def test_reject_single_member_or_corrupt_json(self):
        with self.assertRaises(FakeUserError):
            self.mod.CharterCycle(ORIGINAL, '["oops"]')
        with self.assertRaises(FakeUserError):
            self.mod.CharterCycle(ORIGINAL, '{invalid')

    def test_nonmember_cannot_propose(self):
        self.sdk.message.sender_address = X
        with self.assertRaises(FakeUserError):
            self.contract.propose('rule_01', REPLACEMENT, 'Detailed explanation of proposed rule')
        self.assertEqual(int(self.contract.get_proposal_count()), 0)

    def test_lifecycle_threshold_timelock_and_enact(self):
        self.propose()
        self.contract.vote('rule_01', True)
        self.sdk.message.sender_address = B
        self.contract.vote('rule_01', True)
        with self.assertRaises(FakeUserError):
            self.contract.vote('rule_01', True)
        with self.assertRaises(FakeUserError):
            self.contract.finalize('rule_01')
        self.clock[0] = 1000 + self.mod.VOTING_SECONDS
        self.contract.finalize('rule_01')
        self.assertEqual(json.loads(self.contract.get_proposal('rule_01'))['status'], 'TIMELOCK')
        with self.assertRaises(FakeUserError):
            self.contract.enact('rule_01')
        self.clock[0] += self.mod.TIMELOCK_SECONDS
        self.contract.enact('rule_01')
        ch = json.loads(self.contract.get_charter())
        self.assertEqual(ch['version'], 2)
        self.assertEqual(ch['text'], REPLACEMENT)
        with self.assertRaises(FakeUserError):
            self.contract.enact('rule_01')

    def test_vote_rejection_without_two_thirds(self):
        self.propose()
        self.contract.vote('rule_01', True)
        self.sdk.message.sender_address = B
        self.contract.vote('rule_01', False)
        self.clock[0] += self.mod.VOTING_SECONDS
        self.contract.finalize('rule_01')
        self.assertEqual(json.loads(self.contract.get_proposal('rule_01'))['status'], 'REJECTED')
        self.assertEqual(json.loads(self.contract.get_charter())['version'], 1)

    def test_conflict_is_not_voteable(self):
        p = self.propose(status='CONFLICT')
        self.assertEqual(p['status'], 'BLOCKED')
        with self.assertRaises(FakeUserError): self.contract.vote('rule_01', True)

    def test_malformed_ai_response_is_never_approval(self):
        p = self.propose(status='INVALID')
        self.assertEqual(p['review'], 'UNDETERMINED')
        self.assertEqual(p['status'], 'BLOCKED')

    def test_leader_validator_disagreement_preserves_state(self):
        self.reply('COMPATIBLE', 'CONFLICT')
        with self.assertRaises(FakeConsensusError):
            self.contract.propose('rule_01', REPLACEMENT, 'A new proposal to improve archive access')
        self.assertEqual(self.contract.get_proposal_count(), 0)
        self.assertEqual(self.contract.get_proposal('rule_01'), '')

    def test_concurrent_proposals_stale_version_cannot_overwrite(self):
        self.propose('rule_01', REPLACEMENT)
        self.propose('rule_02', OTHER)
        self.contract.vote('rule_01', True)
        self.contract.vote('rule_02', True)
        self.sdk.message.sender_address = B
        self.contract.vote('rule_01', True)
        self.contract.vote('rule_02', True)
        self.clock[0] += self.mod.VOTING_SECONDS
        self.contract.finalize('rule_01')
        self.contract.finalize('rule_02')
        self.clock[0] += self.mod.TIMELOCK_SECONDS
        self.contract.enact('rule_01')
        with self.assertRaises(FakeUserError):
            self.contract.enact('rule_02')
        self.assertEqual(json.loads(self.contract.get_charter())['text'], REPLACEMENT)

    def test_no_vote_after_deadline_or_wrong_type(self):
        self.propose()
        with self.assertRaises(FakeUserError): self.contract.vote('rule_01', 1)
        self.clock[0] += self.mod.VOTING_SECONDS
        with self.assertRaises(FakeUserError): self.contract.vote('rule_01', True)

    def test_reject_duplicate_proposal(self):
        self.propose()
        with self.assertRaises(FakeUserError):
            self.contract.propose('rule_01', OTHER, 'Rationale for duplicate proposal')

    def test_immutability_of_constitution_snapshot(self):
        p = self.propose()
        self.assertEqual(p['candidate_hash'], self.mod._digest(REPLACEMENT))
        self.assertEqual(json.loads(self.contract.get_charter())['version'], 1)


    def test_four_member_two_thirds_requires_three_yes(self):
        self.contract = self.mod.CharterCycle(ORIGINAL, json.dumps([A, B, C, D]))
        self.contract._now = lambda: self.clock[0]
        self.propose()
        self.contract.vote('rule_01', True)
        self.sdk.message.sender_address = B
        self.contract.vote('rule_01', True)
        self.clock[0] += self.mod.VOTING_SECONDS
        self.contract.finalize('rule_01')
        self.assertEqual(json.loads(self.contract.get_proposal('rule_01'))['status'], 'REJECTED')

    def test_old_proposal_cannot_take_new_votes(self):
        self.propose('rule_01', REPLACEMENT)
        self.propose('rule_02', OTHER)
        self.contract.vote('rule_01', True)
        self.sdk.message.sender_address = B
        self.contract.vote('rule_01', True)
        self.clock[0] += self.mod.VOTING_SECONDS
        self.contract.finalize('rule_01')
        self.clock[0] += self.mod.TIMELOCK_SECONDS
        self.contract.enact('rule_01')
        with self.assertRaises(FakeUserError):
            self.contract.vote('rule_02', True)

    def test_non_member_cannot_vote(self):
        self.propose()
        self.sdk.message.sender_address = X
        with self.assertRaises(FakeUserError):
            self.contract.vote('rule_01', True)

    def test_immutable_address_validation(self):
        with self.assertRaises(FakeUserError):
            self.contract.is_member('0x' + 'g' * 40)
        with self.assertRaises(FakeUserError):
            self.contract.is_member('0x' + '0' * 40)

if __name__ == '__main__':
    unittest.main()
