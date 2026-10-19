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

# Guidance is deliberately advisory: the local language model still generates
# the answer. These rules never change memory or rewrite a new topic.
DETAIL = re.compile(r"\b(?:in detail|step.by.step|thoroughly|comprehensive|deep dive|elaborate)\b", re.I)
BRIEF = re.compile(r"\b(?:briefly|short answer|in one sentence|summari[sz]e|keep it short)\b", re.I)

def response_guidance(message, history):
    """Produce bounded response instructions without modifying user input."""
    resolved = resolve_followup(message, history)
    if DETAIL.search(message):
        depth = "The user requests detail: explain thoroughly with useful structure."
    elif BRIEF.search(message):
        depth = "The user requests brevity: answer in one or two sentences."
    elif resolved:
        depth = "This is a follow-up: respond in 2-4 sentences unless more is needed."
    else:
        depth = "Be concise by default; add detail only when useful."
    if resolved:
        continuity = ("Build on the prior explanation without repeating its definition "
                      "or introductory paragraphs. For 'more', add NEW relevant insight.")
    else:
        continuity = ("Treat the current question on its own terms. If it introduces "
                      "a different subject, answer that subject without dragging in "
                      "the previous topic. Do not erase history.")
    return depth + " " + continuity
