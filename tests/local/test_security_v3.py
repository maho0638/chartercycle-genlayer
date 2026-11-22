"""Security and quorum-boundary cases in FAKE SDK; NOT GenVM verification."""
import json
import pathlib
import unittest
from sdk_stub import FakeUserError, install_and_load

P = pathlib.Path(__file__).resolve().parents[2] / 'contracts/charter_cycle.py'
A='0x'+'11'*20
B='0x'+'22'*20
C='0x'+'33'*20
BASE='Members keep clear public records, document each rule change, and maintain transparent democratic votes.'
NEXT='Members keep a transparent archive and publish the full voting record after every constitutional amendment.'

class SecurityV3(unittest.TestCase):
    def setUp(self):
        self.sdk,self.mod=install_and_load('charter_v3',str(P))
        self.sdk.message.sender_address=A
        self.clock=[1000]

    def deploy(self,members):
        c=self.mod.CharterCycle(BASE,json.dumps(members))
        c._now=lambda:self.clock[0]
        return c

    def propose(self,c,n):
        self.sdk.nondet.answers.extend([{'verdict':'COMPATIBLE'}]*2)
        c.propose('p_0001',NEXT,'A sufficiently detailed rationale for keeping records.')

    def test_quorum_boundary_for_every_supported_member_count(self):
        # Both sides of the exact ceil(2n/3) boundary for n=3..15.
        for count in range(3,16):
            ids=['0x'+f'{i:040x}' for i in range(1,count+1)]
            for success in (False,True):
                self.sdk.message.sender_address=ids[0]
                c=self.deploy(ids)
                self.propose(c,count)
                yes=(2*count+2)//3-(0 if success else 1)
                for identity in ids[:yes]:
                    self.sdk.message.sender_address=identity
                    c.vote('p_0001',True)
                self.clock[0]+=self.mod.VOTING_SECONDS
                c.finalize('p_0001')
                actual=json.loads(c.get_proposal('p_0001'))['status']
                self.assertEqual(actual,'TIMELOCK' if success else 'REJECTED', (count,yes))
                self.clock[0]+=1

    def test_unicode_bidi_and_zero_width_rejected_before_consensus(self):
        for malicious in ('\u202e','\u2066','\u200b','\ufeff','\u200d'):
            c=self.deploy([A,B,C])
            self.sdk.message.sender_address=A
            with self.assertRaises(FakeUserError):
                c.propose('p_0001', NEXT+malicious, 'Clear and detailed public rationale for the proposed change')
            self.assertEqual(c.get_proposal_count(),0)
            self.assertEqual(len(self.sdk.nondet.answers),0)

    def test_negative_changes_do_not_create_state(self):
        c=self.deploy([A,B,C])
        for candidate in ('',BASE,'short','x'*2401):
            with self.assertRaises(FakeUserError):
                c.propose('p_0001',candidate,'Transparent and detailed rationale text')
        self.assertEqual(c.get_proposal_count(),0)

    def test_mixed_case_founder_is_same_identity(self):
        c=self.deploy([A,B,C])
        self.assertTrue(c.is_member(A.upper().replace('0X','0x')))
        self.propose(c,3)
        c.vote('p_0001',True)
        self.sdk.message.sender_address=A.upper().replace('0X','0x')
        with self.assertRaises(FakeUserError):
            c.vote('p_0001',False)
        self.assertEqual(json.loads(c.get_proposal('p_0001'))['yes'],1)
