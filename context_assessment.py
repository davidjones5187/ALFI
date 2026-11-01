"""A.L.F.I. 2.0 — deterministic information assessment.

Caller-supplied information is not independently corroborated.
No memory, network, file inspection, or action execution is performed.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class InformationItem:
    field: str
    value: str
    source: str


@dataclass(frozen=True)
class InformationConflict:
    field: str
    entries: Tuple[InformationItem, ...]


@dataclass(frozen=True)
class ContextAssessment:
    missing: Tuple[str, ...]
    conflicts: Tuple[InformationConflict, ...]
    status: str


def assess_context(required_fields, supplied_items):
    """Identify missing fields and explicit value disagreements."""
    if not isinstance(required_fields, (list, tuple)):
        raise ValueError("Required fields must be a list or tuple.")

    if not isinstance(supplied_items, (list, tuple)):
        raise ValueError("Supplied items must be a list or tuple.")

    required = []

    for field in required_fields:
        if not isinstance(field, str) or not field.strip():
            raise ValueError("Required fields must be nonempty strings.")

        normalized = field.strip()

        if normalized not in required:
            required.append(normalized)

    items = []

    for item in supplied_items:
        if not isinstance(item, dict):
            raise ValueError("Each supplied item must be a dictionary.")

        if set(item) != {"field", "value", "source"}:
            raise ValueError(
                "Each item requires exactly field, value, and source."
            )

        values = (item["field"], item["value"], item["source"])

        if any(
            not isinstance(value, str) or not value.strip()
            for value in values
        ):
            raise ValueError("Item fields must be nonempty strings.")

        items.append(
            InformationItem(*(value.strip() for value in values))
        )

    grouped = {}

    for item in items:
        grouped.setdefault(item.field, []).append(item)

    missing = tuple(
        field for field in required
        if field not in grouped
    )

    conflicts = []

    for field, entries in grouped.items():
        distinct_values = {entry.value for entry in entries}

        if len(distinct_values) > 1:
            conflicts.append(
                InformationConflict(
                    field=field,
                    entries=tuple(entries),
                )
            )

    if conflicts:
        status = "conflicting"
    elif missing:
        status = "incomplete"
    else:
        status = "complete"

    return ContextAssessment(
        missing=missing,
        conflicts=tuple(conflicts),
        status=status,
    )
