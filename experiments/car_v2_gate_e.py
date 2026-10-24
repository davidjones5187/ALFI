"""Gate E-1: conservative question-to-topic routing, synthetic Orion only.

Offline, opt-in, no model calls, no production imports. Topic keys are NOT inputs.
"""
import re

ABSTAIN = "No approved CAR record sufficiently answers this question."
TOPICS = {
    "orion_color": ("color", "colour", "hue"),
    "orion_window": ("window", "time of day", "morning or evening"),
    "orion_slogan": ("slogan", "tagline", "motto"),
    "orion_budget": ("budget", "cost", "funding"),
}
ALIASES = {"shade": "color", "launch hue": "hue"}
OVERRIDE = re.compile(r"\b(ignore|disregard|override|forget)\b.{0,90}\b(instruction|record|review|approved|previous|guidance)\b", re.I)
REVISION = re.compile(r"\b(before|prior to|original|previous|old|earlier)\b.{0,40}\b(revision|change|decision|color|hue)\b", re.I)


def route(question):
    if not isinstance(question, str) or not question.strip():
        return {"decision": "abstain", "reason": "invalid_question"}
    q = " ".join(question.lower().split())
    if not re.search(r"\borion\b", q):
        return {"decision": "outside_scope", "reason": "not_orion"}
    if OVERRIDE.search(q):
        return {"decision": "abstain", "reason": "adversarial_instruction"}
    if REVISION.search(q):
        return {"decision": "abstain", "reason": "historical_fact_not_in_current_record"}
    if re.search(r"\b(why|who|which person|source|evidence|exact date|day|month|year)\b", q):
        return {"decision": "abstain", "reason": "unsupported_detail"}
    matches = []
    for key, words in TOPICS.items():
        if any(re.search(r"\b" + re.escape(word) + r"\b", q) for word in words):
            matches.append(key)
    if len(matches) != 1:
        return {"decision": "abstain", "reason": "ambiguous_or_no_match"}
    return {"decision": "lookup", "topic_key": matches[0], "reason": "single_topic_match"}


def answer_question(store, question, model_call):
    """Fail closed for CAR lookups; ordinary questions pass through unchanged."""
    from experiments.car_v2_context import build_car_context
    from experiments.car_v2_model_comparison import make_messages
    selection = route(question)
    if selection["decision"] == "outside_scope":
        return {"answer": model_call(make_messages(question, "")), "model_calls": 1, **selection}
    if selection["decision"] == "abstain":
        return {"answer": ABSTAIN, "model_calls": 0, **selection}
    context = build_car_context(store, selection["topic_key"], enabled=True)
    if not context:
        return {"answer": ABSTAIN, "model_calls": 0, "decision": "abstain",
                "reason": "no_approved_record", "topic_key": selection["topic_key"]}
    return {"answer": model_call(make_messages(question, context)), "model_calls": 1, **selection}
