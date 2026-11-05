import unittest

from conversational_intelligence import response_policy


class GroundedReasoningTests(unittest.TestCase):

    def test_policy_preserves_user_fact_provenance(self):
        policy = response_policy("What color is the fictional crystal?", [])
        self.assertIn("user-provided facts as premises", policy)
        self.assertIn("not independent verification", policy)

    def test_policy_requires_constraint_check(self):
        policy = response_policy("Would solar power work in a dark cave?", [])
        self.assertIn("physical, numerical, and environmental constraints", policy)

    def test_policy_requires_decisive_reason(self):
        policy = response_policy("Would this solution work?", [])
        self.assertIn("decisive constraint", policy)

    def test_policy_distinguishes_inference(self):
        policy = response_policy("What can we conclude?", [])
        self.assertIn("inferences, and assumptions", policy)

    def test_existing_format_policy_remains(self):
        policy = response_policy('Respond with exactly one word.', [])
        self.assertIn("STRICT FORMAT", policy)


if __name__ == "__main__":
    unittest.main()
