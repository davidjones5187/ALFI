"""Supervised response recommendations for explicit uncertainty."""

from dataclasses import dataclass

from statement_uncertainty import assess_statement_uncertainty


_SITUATIONS = {
    "ordinary",
    "missing_information",
    "consequential_action",
}


@dataclass(frozen=True)
class UncertaintyResponse:
    uncertainty_detected: bool
    expression: str | None
    recommendation: str
    guidance: str


def recommend_uncertainty_response(message, situation):
    """Recommend response behavior without verifying facts or acting."""
    if not isinstance(situation, str) or situation not in _SITUATIONS:
        raise ValueError("Unsupported situation.")

    assessment = assess_statement_uncertainty(message)

    if situation == "missing_information":
        recommendation = "clarify"
        guidance = (
            "Ask for the specific missing information. "
            "Do not invent an answer."
        )
    elif situation == "consequential_action" and assessment.detected:
        recommendation = "verify"
        guidance = (
            "Recommend verifying the uncertain assumption "
            "before considering the action. "
            "Do not execute an action."
        )
    elif assessment.detected:
        recommendation = "acknowledge"
        guidance = (
            "Acknowledge the stated uncertainty without "
            "claiming independent verification."
        )
    else:
        recommendation = "respond"
        guidance = (
            "Respond normally. Absence of an explicit uncertainty "
            "expression does not establish factual certainty."
        )

    return UncertaintyResponse(
        uncertainty_detected=assessment.detected,
        expression=assessment.expression,
        recommendation=recommendation,
        guidance=guidance,
    )
