"""A.L.F.I. 2.0 — explicitly supplied task context.

Context is supplied by the caller, not independently verified.
This module performs no file, memory, or network access.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ContextFact:
    statement: str
    source: str


@dataclass(frozen=True)
class VerifiedContext:
    facts: Tuple[ContextFact, ...]


def create_verified_context(facts):
    """Validate caller-supplied facts without claiming corroboration."""
    if not isinstance(facts, (list, tuple)):
        raise ValueError("Facts must be a list or tuple.")

    if not facts:
        raise ValueError("At least one fact is required.")

    validated = []

    for fact in facts:
        if not isinstance(fact, dict):
            raise ValueError("Each fact must be a dictionary.")

        if set(fact) != {"statement", "source"}:
            raise ValueError(
                "Each fact must contain exactly statement and source."
            )

        statement = fact["statement"]
        source = fact["source"]

        if not isinstance(statement, str) or not statement.strip():
            raise ValueError("Fact statement must be nonempty text.")

        if not isinstance(source, str) or not source.strip():
            raise ValueError("Fact source must be nonempty text.")

        validated.append(
            ContextFact(
                statement=statement.strip(),
                source=source.strip(),
            )
        )

    return VerifiedContext(facts=tuple(validated))
