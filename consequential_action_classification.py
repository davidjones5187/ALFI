"""Conservative, advisory classification of explicit consequential requests."""

from dataclasses import dataclass
import re


_ACTION = (
    r"(?:delete|remove|erase|overwrite|replace|send|email|"
    r"publish|post|transfer|pay)"
)

_REQUEST = re.compile(
    rf"^(?:please\s+)?{_ACTION}\b",
    re.IGNORECASE,
)

_DISCUSSION = re.compile(
    rf"^(?:should|could|would)\s+(?:i|we)\s+{_ACTION}\b",
    re.IGNORECASE,
)

_ORDINARY = re.compile(
    r"^(?:hello|hi|thanks|thank you)[.!?]*$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ActionClassification:
    category: str
    situation: str
    requires_approval: bool
    reason: str


def classify_consequential_action(message):
    """Classify supported patterns; never authorize or execute an action."""
    if not isinstance(message, str) or not message.strip():
        raise ValueError("Message must be nonempty text.")

    normalized = message.strip()

    # Inspect explicit sentence openings, not arbitrary verb occurrences.
    sentences = re.split(r"(?<=[.!?])\s+", normalized)

    if any(_REQUEST.search(sentence) for sentence in sentences):
        return ActionClassification(
            "action_request",
            "consequential_action",
            True,
            "Explicit supported consequential-action request.",
        )

    if _DISCUSSION.search(normalized):
        return ActionClassification(
            "action_discussion",
            "consequential_action",
            False,
            "Discussion of a supported consequential action.",
        )

    if _ORDINARY.fullmatch(normalized):
        return ActionClassification(
            "ordinary",
            "ordinary",
            False,
            "Recognized ordinary conversational expression.",
        )

    return ActionClassification(
        "unknown",
        "ordinary",
        False,
        "Unsupported or ambiguous intent; no authorization inferred.",
    )
