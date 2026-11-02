"""Deterministic recognition of explicit statement uncertainty."""

from dataclasses import dataclass
import re


_PATTERNS = (
    ("not sure", re.compile(r"\b(?:i(?:'|’)m|i am)\s+not\s+sure\b", re.I)),
    ("i think", re.compile(r"\bi\s+think\b", re.I)),
    ("i believe", re.compile(r"\bi\s+believe\b", re.I)),
    ("maybe", re.compile(r"\bmaybe\b", re.I)),
    ("perhaps", re.compile(r"\bperhaps\b", re.I)),
    ("possibly", re.compile(r"\bpossibly\b", re.I)),
    ("might", re.compile(r"\bmight\b", re.I)),
)


@dataclass(frozen=True)
class StatementUncertainty:
    detected: bool
    expression: str | None


def assess_statement_uncertainty(message):
    """Detect explicit qualifiers; do not infer truth or verification."""
    if not isinstance(message, str):
        raise ValueError("Message must be a string.")

    if not message.strip():
        raise ValueError("Message must not be empty.")

    matches = []

    for expression, pattern in _PATTERNS:
        match = pattern.search(message)
        if match:
            matches.append((match.start(), expression))

    if not matches:
        return StatementUncertainty(
            detected=False,
            expression=None,
        )

    _, expression = min(matches, key=lambda item: item[0])

    return StatementUncertainty(
        detected=True,
        expression=expression,
    )
