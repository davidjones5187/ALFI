import unittest
from unittest.mock import patch

from autonomy_boundaries import AutonomyDecision, PROHIBITED
from first_ai import memory_policy_allows


class MemoryAuthorizationTests(unittest.TestCase):
    def test_unconfirmed_memory_change_denied(self):
        self.assertFalse(memory_policy_allows())

    def test_confirmed_memory_change_allowed(self):
        self.assertTrue(memory_policy_allows(authorized=True))

    def test_prohibited_policy_overrides_confirmation(self):
        with patch(
            "first_ai.assess_autonomy",
            return_value=AutonomyDecision("modify_memory", PROHIBITED),
        ):
            self.assertFalse(memory_policy_allows(authorized=True))


if __name__ == "__main__":
    unittest.main()
