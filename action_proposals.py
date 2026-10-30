"""A.L.F.I. 2.0 — supervised action proposals.

A proposal describes a possible action.
It does not authorize or execute that action.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ActionProposal:
    action: str
    justification: str
    risks: Tuple[str, ...]
    requires_approval: bool = True
    status: str = "proposed"


def create_action_proposal(action, justification, risks):
    """Validate and return an immutable, unapproved proposal."""

    if not isinstance(action, str) or not action.strip():
        raise ValueError("An action description is required.")

    if (
        not isinstance(justification, str)
        or not justification.strip()
    ):
        raise ValueError("A justification is required.")

    if not isinstance(risks, (list, tuple)):
        raise ValueError("Risks must be a list or tuple.")

    if not risks:
        raise ValueError(
            "At least one risk or limitation is required."
        )

    if any(
        not isinstance(risk, str) or not risk.strip()
        for risk in risks
    ):
        raise ValueError("Each risk must be nonempty text.")

    return ActionProposal(
        action=action.strip(),
        justification=justification.strip(),
        risks=tuple(risk.strip() for risk in risks),
    )
