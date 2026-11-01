"""A.L.F.I. 2.0 — supervised proposal assessment gate.

Assessment determines whether proposal generation may be attempted.
It never authorizes or executes a proposed action.
"""

from dataclasses import dataclass

from context_assessment import ContextAssessment, assess_context
from action_proposals import generate_model_action_proposal
from verified_context import VerifiedContext


@dataclass(frozen=True)
class ProposalReadiness:
    assessment: ContextAssessment
    ready: bool


def assess_proposal_readiness(required_fields, supplied_items):
    """Evaluate explicitly structured prerequisites before generation."""
    assessment = assess_context(required_fields, supplied_items)

    return ProposalReadiness(
        assessment=assessment,
        ready=(
            not assessment.missing
            and not assessment.conflicts
        ),
    )


def generate_assessed_proposal(
    objective,
    required_fields,
    supplied_items,
    context=None,
    **generator_options,
):
    """Generate only when structured prerequisites are satisfied.

    Returns (readiness, proposal). A blocked assessment returns None
    for the proposal and never calls the model.
    """
    if not isinstance(objective, str) or not objective.strip():
        raise ValueError("A nonempty objective is required.")

    if context is not None and not isinstance(context, VerifiedContext):
        raise ValueError("Context must be a VerifiedContext instance.")

    readiness = assess_proposal_readiness(
        required_fields,
        supplied_items,
    )

    if not readiness.ready:
        return readiness, None

    proposal = generate_model_action_proposal(
        objective,
        context=context,
        **generator_options,
    )

    return readiness, proposal
