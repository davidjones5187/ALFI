"""A.L.F.I. operational self-model — initial implementation."""

from copy import deepcopy

IDENTITY = {
    "name": "A.L.F.I.",
    "designation": "Artificial Lifeform — First Iteration",
    "version": "1.6-dev",
}

CAPABILITIES = (
    "conversation",
    "taught_knowledge",
    "structured_memory",
    "conversation_history",
    "file_inspection",
    "guided_document_qa",
    "guided_summarization",
)

AUTONOMY = {
    "planning": {"available": False, "enabled": False, "target": True},
    "initiative": {"available": False, "enabled": False, "target": True},
    "tool_execution": "supervised",
}


def operational_snapshot(model_name, use_ollama=True):
    """Return a description of configured capabilities without side effects."""
    return {
        "identity": deepcopy(IDENTITY),
        "runtime": {
            "model": model_name if use_ollama else None,
            "inference": "ollama" if use_ollama else "disabled",
        },
        "capabilities": list(CAPABILITIES),
        "autonomy": deepcopy(AUTONOMY),
    }
