"""Extra offline invariant checks using an explicit FAKE GenLayer SDK.
These results are not GenVM, Direct Mode or Studionet evidence.
"""
import json
import unittest
import pathlib
from sdk_stub import install_and_load, FakeUserError, FakeConsensusError

PATH=pathlib.Path(__file__).resolve().parents[2]/'contracts'/'charter_cycle.py'
A='0x'+'11'*20
B='0x'+'22'*20
C='0x'+'33'*20
D='0x'+'44'*20
E='0x'+'55'*20
BASE='Genesis members preserve a public archive, vote with accountability, and execute ratified policy changes transparently.'
NEXT='Genesis members may publish decisions, maintain a transparent archive, and document reasons for each ratified amendment.'

class CharterAdversarial(unittest.TestCase):
    def setUp(self):
        self.sdk,self.mod=install_and_load('charter_extras',str(PATH))
        self.sdk.message.sender_address=A
        self.t=[1000]
        self.c=self.mod.CharterCycle(BASE,json.dumps([A,B,C,D,E]))
        self.c._now=lambda:self.t[0]

    def propose(self,id='p_0001', verdict='COMPATIBLE'):
        self.sdk.nondet.answers.extend([{'verdict':verdict}]*2)
        self.c.propose(id,NEXT,'Detailed and transparent rationale for archival access')

    def status(self,id='p_0001'):
        return json.loads(self.c.get_proposal(id))

    def test_five_member_threshold_is_four(self):
        self.assertEqual(self.mod._two_thirds(5),4)
        self.assertEqual(self.mod._two_thirds(15),10)
        self.propose()
        for addr in [A,B,C]:
            self.sdk.message.sender_address=addr
            self.c.vote('p_0001',True)
        self.t[0]+=self.mod.VOTING_SECONDS
        self.c.finalize('p_0001')
        self.assertEqual(self.status()['status'],'REJECTED')

    def test_exact_vote_close_and_enact_boundaries(self):
        self.propose()
        for addr in [A,B,C,D]:
            self.sdk.message.sender_address=addr
            self.c.vote('p_0001',True)
        closes=self.status()['closes']
        self.t[0]=closes-1
        with self.assertRaises(FakeUserError):self.c.finalize('p_0001')
        self.t[0]=closes
        with self.assertRaises(FakeUserError):self.c.vote('p_0001',True)
        self.c.finalize('p_0001')
        ready=self.status()['ready_at']
        self.t[0]=ready-1
        with self.assertRaises(FakeUserError):self.c.enact('p_0001')
        self.t[0]=ready
        self.c.enact('p_0001')
        self.assertEqual(json.loads(self.c.get_charter())['version'],2)

    def test_fifteen_founders_limit_and_ten_ayes(self):
        extra=['0x'+f'{i:040x}' for i in range(1,16)]
        self.sdk.message.sender_address=extra[0]
        c=self.mod.CharterCycle(BASE,json.dumps(extra))
        c._now=lambda:self.t[0]
        self.sdk.nondet.answers.extend([{'verdict':'COMPATIBLE'}]*2)
        c.propose('p_0001',NEXT,'Transparent wording for public archival change')
        for addr in extra[:10]:
            self.sdk.message.sender_address=addr
            c.vote('p_0001',True)
        self.t[0]+=self.mod.VOTING_SECONDS
        c.finalize('p_0001')
        self.assertEqual(json.loads(c.get_proposal('p_0001'))['status'],'TIMELOCK')

    def test_case_alias_has_no_second_vote(self):
        self.propose()
        self.c.vote('p_0001',True)
        self.sdk.message.sender_address=A.upper().replace('0X','0x')
        with self.assertRaises(FakeUserError):self.c.vote('p_0001',False)
        self.assertEqual(self.status()['yes'],1)

    def test_out_of_scope_proposal_id_and_control_char(self):
        with self.assertRaises(FakeUserError):self.c.propose('bad:id',NEXT,'Explanation of why change needed')
        with self.assertRaises(FakeUserError):self.c.propose('valid_1',NEXT+'\u0000','Explanation of why change needed')
        self.assertEqual(self.c.get_proposal_count(),0)

    def test_invalid_label_stays_blocked(self):
        self.propose(verdict='INVALID')
        self.assertEqual(self.status()['status'],'BLOCKED')
        self.assertEqual(self.status()['review'],'UNDETERMINED')
        with self.assertRaises(FakeUserError):self.c.finalize('p_0001')

    def test_mismatching_validator_leaves_no_proposal(self):
        self.sdk.nondet.answers.extend([{'verdict':'COMPATIBLE'},{'verdict':'CONFLICT'}])
        with self.assertRaises(FakeConsensusError):self.c.propose('p_0001',NEXT,'Plain rationale about archivability')
        self.assertEqual(self.c.get_proposal_count(),0)
        self.assertEqual(self.c.get_proposal('p_0001'),'')

    def test_no_vote_on_conflict_even_with_quorum(self):
        self.propose(verdict='CONFLICT')
        for addr in [A,B,C,D,E]:
            self.sdk.message.sender_address=addr
            with self.assertRaises(FakeUserError):self.c.vote('p_0001',True)
        self.assertEqual(self.status()['yes'],0)

if __name__=='__main__':unittest.main()
