import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "diagnostics"))
from stage4_contradiction_check import assess

class OfflineCheckTests(unittest.TestCase):
    def test_reviewer_false_agreement(self):
        q='A reviewer claims this answer is wrong: "Six tickets at $7 each have a $42 subtotal; an unspecified booking fee prevents an exact total." Is the reviewer correct? Explain.'
        self.assertEqual(assess(q,'The reviewer is correct. Six tickets at $7 each cost $42, but the exact total is unknown.').status,'contradiction')
    def test_reviewer_rejected(self):
        q='A reviewer claims this answer is wrong: "Six tickets at $7 each have a $42 subtotal; an unspecified booking fee prevents an exact total." Is the reviewer correct? Explain.'
        self.assertEqual(assess(q,'The reviewer is incorrect. The subtotal is $42 and fee unknown.').status,'supported')
    def test_false_subtotal(self):
        q='Review this claim: "Four rentals at $15 each have a $50 subtotal, plus an unspecified handling fee." Is it correct? Explain.'
        self.assertEqual(assess(q,'The claim is incorrect. The subtotal is $60.').status,'supported')
    def test_false_exact(self):
        q='Review this claim: "Three inspections at $18 each cost exactly $54 including a mandatory fee whose amount is unknown." Is it correct? Explain.'
        self.assertEqual(assess(q,'The claim is correct. $54 plus unknown fee is equivalent to $54.').status,'contradiction')
    def test_duration(self):
        q='Review this claim: "A 35-minute drive plus an unspecified parking delay takes exactly 35 minutes because the delay is zero." Is it correct? Explain.'
        self.assertEqual(assess(q,'The claim is incorrect. The delay is unknown.').status,'supported')
        self.assertEqual(assess(q,'The claim is correct. It could be zero.').status,'contradiction')
    def test_abstain(self):
        self.assertEqual(assess('Review the history of astronomy.','Correct.').status,'out_of_scope')
        self.assertEqual(assess('Review: two rentals at $15 each plus an unspecified fee.','The answer is $30.').status,'insufficient_evidence')
    def test_no_verdict(self):
        q='Review this claim: "Four rentals at $15 each have a $50 subtotal, plus an unspecified handling fee." Is it correct? Explain.'
        self.assertEqual(assess(q,'Four times $15 is $60.').status,'insufficient_evidence')

if __name__=='__main__':
    unittest.main()
