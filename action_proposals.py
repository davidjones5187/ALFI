"""A.L.F.I. 2.0 — supervised action proposals.

A proposal describes a possible action.
It does not authorize or execute that action.
"""

import json
import os
import urllib.request
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


def parse_model_action_proposal(response):
    """Validate model JSON without authorizing or executing actions."""
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

    required = {"action", "justification", "risks"}

    if set(data) != required:
        raise ValueError(
            "Model response must contain exactly: "
            "action, justification, risks."
        )

    return create_action_proposal(
        action=data["action"],
        justification=data["justification"],
        risks=data["risks"],
    )


def generate_model_action_proposal(
    objective,
    model=None,
    url="http" + "://" + "127.0.0.1:11434/api/chat",
    timeout=90,
):
    """Generate a proposal only; never authorize or execute it."""
    if not isinstance(objective, str) or not objective.strip():
        raise ValueError("A nonempty objective is required.")

    system_prompt = (
        "You are A.L.F.I.'s supervised action proposal assistant. "
        "Return only a JSON object with exactly three fields: "
        "action (string), justification (string), risks (nonempty list of strings). "
        "Propose one specific action relevant to the user's objective. "
        "Explain why the action is appropriate and identify real risks or limitations. "
        "Never claim an action has been performed, approved, or authorized. "
        "Do not assume access to files, memory, tools, or external systems. "
        "Do not invent observations, measurements, or completed work. "
        "If prerequisites are unavailable, propose obtaining them rather than "
        "pretending they have been satisfied."
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

    return parse_model_action_proposal(message.get("content"))
