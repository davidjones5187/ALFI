"""A.L.F.I. 2.0 — supervised planning foundation.

Plans are proposals. Creating a plan never executes its steps.
"""

import json
import os
import urllib.request
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

    for field_name, values in (
        ("assumptions", assumptions),
        ("uncertainties", uncertainties),
    ):
        if not isinstance(values, (list, tuple)):
            raise ValueError(f"{field_name} must be a list or tuple.")
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError(f"{field_name} must contain nonempty strings.")

    return Plan(
        objective=objective.strip(),
        steps=tuple(validated_steps),
        assumptions=tuple(value.strip() for value in assumptions),
        uncertainties=tuple(value.strip() for value in uncertainties),
    )


def parse_model_plan(objective, response):
    """Validate a model's JSON proposal without executing any actions."""
    if not isinstance(response, str):
        raise ValueError("Model response must be a JSON string.")

    def reject_duplicate_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON field: {key}")
            result[key] = value
        return result

    try:
        data = json.loads(
            response,
            object_pairs_hook=reject_duplicate_keys,
        )
    except json.JSONDecodeError as exc:
        raise ValueError("Model response is not valid JSON.") from exc

    if not isinstance(data, dict):
        raise ValueError("Model response must be a JSON object.")

    allowed_fields = {"steps", "assumptions", "uncertainties"}
    if set(data) - allowed_fields:
        raise ValueError("Model response contains unsupported fields.")

    if "steps" not in data or not isinstance(data["steps"], list):
        raise ValueError("Model response requires a list of steps.")

    return create_plan(
        objective=objective,
        steps=data["steps"],
        assumptions=data.get("assumptions", []),
        uncertainties=data.get("uncertainties", []),
    )


def generate_model_plan(
    objective,
    model=None,
    url="http://127.0.0.1:11434/api/chat",
    timeout=90,
):
    """Request a proposed plan from Ollama without executing actions."""
    if not isinstance(objective, str) or not objective.strip():
        raise ValueError("A plan requires a nonempty objective.")

    system_prompt = (
        "You are A.L.F.I.'s supervised planning assistant. "
        "Return only a JSON object with these fields: "
        "steps (a nonempty list of strings), "
        "assumptions (a list of strings), "
        "uncertainties (a list of strings). "
        "Do not include approval, execution, status, or objective fields. "
        "Propose actions only. Never claim that actions were performed. "
        "Do not assume access to files, memory, tools, or external systems."
    )

    payload = json.dumps({
        "model": model or os.environ.get("ALFI_OLLAMA_MODEL") or "gemma3:4b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": objective.strip()},
        ],
        "stream": False,
        "format": "json",
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        result = json.load(response)

    if not isinstance(result, dict):
        raise ValueError("Ollama returned an invalid response.")

    message = result.get("message")
    if not isinstance(message, dict):
        raise ValueError("Ollama response is missing its message.")

    content = message.get("content")
    return parse_model_plan(objective, content)
