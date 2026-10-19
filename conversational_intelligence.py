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
    r"^(?:actually\b|correction:|i meant\b|what i meant was\b|no,? i meant\b)",
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

# Increment 4: explicit, bounded feedback signals. No persistent writes.
DISSATISFACTION = re.compile(
    r"^(?:that's (?:not right|incorrect|wrong)|that is (?:incorrect|wrong)|"
    r"you're wrong|you are wrong|not quite|that's not what i (?:asked|meant)|"
    r"that (?:didn't|doesn't) answer my question)[.! ]*$", re.I
)

def feedback_intent(message):
    """Classify unambiguous feedback; leave substantive messages untouched."""
    message = message.strip()
    if not message or COMMAND.match(message):
        return "other"
    if CORRECTION.match(message):
        return "correction"
    if DISSATISFACTION.fullmatch(message):
        return "dissatisfaction"
    if SOCIAL_PRAISE.fullmatch(message):
        return "praise"
    if SOCIAL_THANKS.fullmatch(message):
        return "thanks"
    return "other"


def feedback_response(message):
    """Respond to standalone dissatisfaction without claiming learning."""
    if feedback_intent(message) == "dissatisfaction":
        return "Thanks for pointing that out. Which part should I correct?"
    return None


def quality_guidance(message):
    """Advisory model guidance, never a substitute for fact checking."""
    if feedback_intent(message) == "correction":
        return ("Use the user's correction for this conversation. Do not claim "
                "to retrain the model or permanently update memory. "
                "If unclear, ask one concise question.")
    return ("Answer the actual question directly. Avoid unsupported certainty, "
            "especially for technical or security claims. Distinguish established "
            "facts from potential applications and limitations. Do not repeat "
            "definitions unnecessarily.")


# Increment 5: bounded adaptive reasoning hints; no memory mutation.
BEGINNER = re.compile(r"\b(?:beginner|simple terms|plain english|new to|don't know much|explain simply)\b", re.I)
TECHNICAL = re.compile(r"\b(?:technical detail|technical explanation|advanced explanation|mathematical|implementation details)\b", re.I)
AMBIGUOUS = re.compile(r"^(?:what about (?:it|that|this)|why is (?:it|that) important|how does (?:it|that) work)[?.! ]*$", re.I)

def adaptive_guidance(message, history):
    """Provide limited style and epistemic guidance without rewriting history."""
    message = message.strip()
    if not message or COMMAND.match(message):
        return ""
    if BEGINNER.search(message):
        style = "Explain in everyday language, defining jargon and using one concrete example."
    elif TECHNICAL.search(message):
        style = "Give technical mechanisms and caveats appropriate to an advanced reader."
    else:
        style = "Use accessible language and define technical terms when first introduced."
    return (style + " Distinguish proven results from hypotheses or potential uses. "
            "Do not claim a universal speedup, perfect security, or certainty without evidence. "
            "If the question is underspecified, ask one focused clarifying question.")

def adaptive_clarification(message, history):
    """Only interrupt a narrow set of pronoun-only questions without context."""
    if not AMBIGUOUS.fullmatch(message.strip()):
        return None
    if resolve_followup(message, history) is not None:
        return None
    # Any substantive recent user question can establish a referent.
    for turn in reversed(history[-5:]):
        if isinstance(turn, dict) and isinstance(turn.get("user"), str):
            prior = turn["user"].strip()
            if prior and not COMMAND.match(prior) and not FOLLOWUP.fullmatch(prior):
                return None
    return "Which topic are you referring to?"


# Increment 6: bounded referent and precision guidance. Advisory only.
IMPORTANCE = re.compile(r"^why (?:is|are|was|were) (?:it|that|this|they) important[?.! ]*$", re.I)
QUANTUM = re.compile(r"\bquantum (?:comput(?:ing|ers?)|algorithm|advantage|optimization)\b", re.I)

def contextual_subject(message, history, max_turns=5):
    """Find the last explicit subject, never use assistant text as user intent."""
    if not IMPORTANCE.fullmatch(message.strip()):
        return None
    for turn in reversed(history[-max_turns:]):
        if not isinstance(turn, dict):
            continue
        prior = turn.get("user")
        if not isinstance(prior, str):
            continue
        prior = prior.strip()
        if (not prior or COMMAND.match(prior) or FOLLOWUP.fullmatch(prior)
                or IMPORTANCE.fullmatch(prior) or CORRECTION.match(prior)):
            continue
        if re.match(r"^(?:explain|describe|what is|what are|tell me about)\b", prior, re.I):
            return prior
    return None

def precision_guidance(message, history):
    """Provide model instructions without making factual verification claims."""
    subject = contextual_subject(message, history)
    if subject:
        return ("The user asks why the preceding SUBJECT matters, not whether your "
                "previous answer was too long. Explain the significance and a concrete "
                "application directly. The subject is: " + subject)
    if IMPORTANCE.fullmatch(message.strip()):
        return "The referent is unknown. Ask which subject the user means."
    if QUANTUM.search(message):
        return ("Quantum speedups are algorithm- and task-specific; do not imply "
                "universal advantage or established practical speedups for general "
                "optimization or machine learning. Qualify unverified benchmarks.")
    return ("Use precise technical terminology. Do not generalize a specialized "
            "training objective, such as reconstruction loss, to all neural networks.")

def length_guidance(message):
    """Explicit user brevity takes precedence over technical complexity."""
    if BRIEF.search(message):
        return "HARD STYLE REQUEST: answer in at most two short sentences; no list."
    if DETAIL.search(message) or TECHNICAL.search(message):
        return ("Explain mechanisms accurately with a compact structure. "
                "Avoid exhaustive lists unless explicitly requested.")
    return "Answer directly, preferably in a short paragraph."


# Increment 7: response control is advisory and never changes stored memory.
REPHRASE = re.compile(r"^(?:actually\b|i meant\b|no,? i meant\b|what i meant was\b)", re.I)

def increment7_guidance(message, history):
    """Prioritize explicit brevity, avoid redundant corrections, and qualify claims."""
    message = message.strip()
    if not message or COMMAND.match(message):
        return ""
    rules = []
    if BRIEF.search(message):
        rules.append("PRIORITY: respond in no more than two short sentences, without headings, lists or preamble.")
    elif DETAIL.search(message) or TECHNICAL.search(message):
        rules.append("Give a focused technical explanation, avoiding an encyclopedia-style catalog.")
    else:
        rules.append("Answer the question first, then at most one short supporting paragraph.")
    if REPHRASE.match(message):
        rules.append("This is a conversational correction: address ONLY the corrected scope, do not restart the prior explanation, and do not claim memory was saved.")
    elif history and isinstance(history[-1], dict) and isinstance(history[-1].get("assistant"), str):
        rules.append("Do not restate points already given in the previous answer unless essential to the new question.")
    rules.append("Do not promise universal quantum advantage, unbreakable encryption, or established speedups for generic optimization or machine learning. Backpropagation computes gradients; an optimizer updates parameters. Express uncertainty when evidence is limited.")
    return " ".join(rules)

# Increment 8: one bounded response policy, with no persistent side effects.
def response_policy(message, history):
    """Consolidate conversational instructions without mutating history."""
    if not message.strip() or COMMAND.match(message.strip()):
        return ""
    parts = [
        "Answer the current question directly and accurately.",
        "Do not invent memories, verification, or model learning.",
        "Distinguish established results from hypothetical applications.",
    ]
    if BRIEF.search(message):
        parts.append("STRICT LENGTH: one or two short sentences, no lists or headings.")
    elif DETAIL.search(message) or TECHNICAL.search(message):
        parts.append("Provide focused technical mechanisms and necessary caveats.")
    else:
        parts.append("Prefer one short paragraph.")
    if CORRECTION.match(message):
        parts.append("Address ONLY the user's corrected scope; do not restart the earlier explanation or claim memory was saved.")
    elif resolve_followup(message, history) or contextual_subject(message, history):
        parts.append("Build on the established subject without repeating the prior answer.")
    else:
        parts.append("Do not import unrelated topics from history.")
    parts.append(precision_guidance(message, history))
    return " ".join(parts)


def response_needs_revision(message, answer):
    """Flag length violations; never truncate facts or rewrite user data."""
    if not BRIEF.search(message) or not isinstance(answer, str):
        return False
    text = answer.strip()
    if not text:
        return False
    sentences = re.split(r"(?<=[.!?])\\s+", text)
    return len(sentences) > 2 or len(text.split()) > 65 or bool(re.search(r"(?m)^\\s*(?:[-*] |\\d+[.)] )", text))
