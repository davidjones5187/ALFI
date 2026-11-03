"""Declarative autonomy boundaries; no action execution."""

from dataclasses import dataclass

POLICY_VERSION = "1.0"

INDEPENDENT = "independent"
REQUIRES_AUTHORIZATION = "requires_authorization"
PROHIBITED = "prohibited"

_BOUNDARIES = {
    "reason": INDEPENDENT,
    "analyze": INDEPENDENT,
    "question_assumptions": INDEPENDENT,
    "generate_proposal": INDEPENDENT,
    "assess_information": INDEPENDENT,
    "retrieve_authorized_information": INDEPENDENT,
    "modify_memory": REQUIRES_AUTHORIZATION,
    "read_new_local_file": REQUIRES_AUTHORIZATION,
    "modify_project_file": REQUIRES_AUTHORIZATION,
    "execute_external_tool": REQUIRES_AUTHORIZATION,
    "send_communication": REQUIRES_AUTHORIZATION,
    "financial_transaction": REQUIRES_AUTHORIZATION,
    "change_governing_permissions": PROHIBITED,
    "bypass_authorization": PROHIBITED,
    "conceal_action": PROHIBITED,
    "fabricate_execution_result": PROHIBITED,
}


@dataclass(frozen=True)
class AutonomyDecision:
    activity: str
    decision: str
    policy_version: str = POLICY_VERSION


def assess_autonomy(activity):
    """Classify an activity without authorizing or executing it."""
    if not isinstance(activity, str) or not activity.strip():
        raise ValueError("Activity must be nonempty text.")

    normalized = activity.strip().lower()
    return AutonomyDecision(
        activity=normalized,
        decision=_BOUNDARIES.get(
            normalized,
            REQUIRES_AUTHORIZATION,
        ),
    )
