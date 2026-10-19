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

# Small, deterministic social acknowledgments. No memory writes or model claims.
SOCIAL_THANKS = re.compile(r"^(?:thanks(?: a lot)?|thank you(?: very much)?|appreciate it)[.! ]*$", re.I)
SOCIAL_PRAISE = re.compile(r"^(?:great job|good job|well done|nice work|that's helpful|that was helpful|you did great)[.! ]*$", re.I)

def natural_acknowledgment(message):
    """Handle clear social feedback without invoking a lengthy explanation."""
    message = message.strip()
    if SOCIAL_THANKS.fullmatch(message):
        return "You're welcome!"
    if SOCIAL_PRAISE.fullmatch(message):
        return "Thanks! Glad that helped."
    return None


# Phase 2: conservative intent detection and conversational safeguards.
CORRECTION = re.compile(
    r"^(?:actually\\b|correction:|i meant\\b|what i meant was\\b|no,? i meant\\b)",
    re.I,
)
ACKNOWLEDGMENT = re.compile(
    r"^(?:thanks(?: a lot)?|thank you(?: very much)?|appreciate it|"
    r"great job|good job|well done|nice work|that's helpful|"
    r"that was helpful|you did great)[.! ]*$", re.I,
)

def conversational_intent(message):
    """Classify only clear signals; never guess at a substantive question."""
    message = message.strip()
    if not message or COMMAND.match(message):
        return "other"
    if CORRECTION.match(message):
        return "correction"
    if ACKNOWLEDGMENT.fullmatch(message):
        return "acknowledgment"
    if FOLLOWUP.fullmatch(message):
        return "followup"
    return "other"


def clarification_needed(message, history):
    """Ask for context rather than fabricate a referent."""
    if conversational_intent(message) != "followup":
        return None
    if resolve_followup(message, history) is None:
        return "What topic would you like me to explain?"
    return None


def conversation_guidance(message, history):
    """Additional model guidance; no memory writes or history mutations."""
    intent = conversational_intent(message)
    if intent == "correction":
        return ("The user is correcting a previous statement. Acknowledge the "
                "correction without claiming permanent memory was changed. "
                "Ask for clarification if the corrected referent is unclear.")
    if intent == "followup":
        return ("Use only the resolved conversational subject. Do not revive "
                "unrelated older topics.")
    return ("Answer the current message without assuming it refers to an "
            "earlier subject. Avoid repeating social acknowledgments.")
