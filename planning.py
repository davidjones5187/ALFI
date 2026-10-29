"""A.L.F.I. 2.0 — supervised planning foundation.

Plans are proposals. Creating a plan never executes its steps.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class PlanStep:
    number: int
    description: str
    dependencies: Tuple[int, ...] = ()
    requires_approval: bool = True


@dataclass(frozen=True)
class Plan:
    objective: str
    steps: Tuple[PlanStep, ...]
    assumptions: Tuple[str, ...] = ()
    uncertainties: Tuple[str, ...] = ()
    status: str = "proposed"


def create_plan(objective, steps, assumptions=(), uncertainties=()):
    """Validate and construct a proposed plan without executing it."""
    if not isinstance(objective, str) or not objective.strip():
        raise ValueError("A plan requires a nonempty objective.")

    validated_steps = []
    for number, item in enumerate(steps, start=1):
        if not isinstance(item, str) or not item.strip():
            raise ValueError("Each plan step must be nonempty.")
        validated_steps.append(
            PlanStep(number=number, description=item.strip())
        )

    if not validated_steps:
        raise ValueError("A plan requires at least one step.")

    return Plan(
        objective=objective.strip(),
        steps=tuple(validated_steps),
        assumptions=tuple(assumptions),
        uncertainties=tuple(uncertainties),
    )
