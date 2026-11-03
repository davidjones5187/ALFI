import unittest

from autonomy_boundaries import (
    POLICY_VERSION,
    INDEPENDENT,
    REQUIRES_AUTHORIZATION,
    PROHIBITED,
    assess_autonomy,
)


class AutonomyBoundaryTests(unittest.TestCase):
    def test_policy_version(self):
        self.assertEqual(POLICY_VERSION, "1.0")

    def test_independent_reasoning(self):
        for activity in (
            "reason",
            "analyze",
            "question_assumptions",
            "generate_proposal",
            "assess_information",
            "retrieve_authorized_information",
        ):
            with self.subTest(activity=activity):
                self.assertEqual(
                    assess_autonomy(activity).decision,
                    INDEPENDENT,
                )

    def test_consequential_actions_require_authorization(self):
        for activity in (
            "modify_memory",
            "read_new_local_file",
            "modify_project_file",
            "execute_external_tool",
            "send_communication",
            "financial_transaction",
        ):
            with self.subTest(activity=activity):
                self.assertEqual(
                    assess_autonomy(activity).decision,
                    REQUIRES_AUTHORIZATION,
                )

    def test_prohibited_activities(self):
        for activity in (
            "change_governing_permissions",
            "bypass_authorization",
            "conceal_action",
            "fabricate_execution_result",
        ):
            with self.subTest(activity=activity):
                self.assertEqual(
                    assess_autonomy(activity).decision,
                    PROHIBITED,
                )

    def test_unknown_activity_is_not_independent(self):
        self.assertEqual(
            assess_autonomy("unknown_operation").decision,
            REQUIRES_AUTHORIZATION,
        )

    def test_invalid_activity_rejected(self):
        for value in ("", "  ", None, 42):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    assess_autonomy(value)

    def test_normalization(self):
        result = assess_autonomy("  GENERATE_PROPOSAL  ")
        self.assertEqual(result.activity, "generate_proposal")
        self.assertEqual(result.decision, INDEPENDENT)


if __name__ == "__main__":
    unittest.main()
