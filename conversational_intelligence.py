"""Bounded, conservative contextual follow-up resolution for A.L.F.I. 1.6."""
import re

FOLLOWUP = re.compile(
    r"^(?:give (?:me )?(?:an? |another )?example(?: of (?:that|it))?|"
    r"(?:can you )?explain (?:that|it)(?: again)?|"
    r"(?:tell me )?more(?: about (?:that|it))?|"
    r"what (?:about|does) (?:that|it)(?: mean)?|"
    r"how does (?:that|it) work|why (?:is|does) (?:that|it)\b.*|"
    r"what else (?:can you tell me|do you know)(?: about (?:that|it))?)\??[.!]?$",
    re.IGNORECASE,
)
COMMAND = re.compile(r"^/")

def resolve_followup(message, history, max_turns=5):
    """Return a standalone question only for explicit, unambiguous follow-ups.

    Do not resolve commands, substantive new questions, or earlier follow-ups
    that cannot be traced to a concrete subject.
    """
    message = message.strip()
    if not message or COMMAND.match(message) or not FOLLOWUP.fullmatch(message):
        return None
    for turn in reversed(history[-max_turns:]):
        if not isinstance(turn, dict):
            continue
        prior = turn.get("user")
        if not isinstance(prior, str) or not prior.strip() or COMMAND.match(prior.strip()):
            continue
        if FOLLOWUP.fullmatch(prior.strip()):
            continue
        return f"{message} The subject is: {prior.strip()}"
    return None
