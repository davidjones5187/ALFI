"""Gate F-C1: experimental two-stage protected-memory router. Not production."""
import re
from experiments.car_v2_gate_e import ABSTAIN
from experiments.car_v2_gate_f_h2r import hits, validate_manifest
from experiments.car_v2_gate_f_b import strict_answer, strict_route
from experiments.car_v2_model_comparison import make_messages

# Positive general intent patterns, deliberately narrow. No default model fallback.
GENERAL=(
 re.compile(r"why (?:does|do) (?:the )?(?:moon|leaves) .+\?",re.I),
 re.compile(r"how do i (?:boil an egg|cook rice)\?",re.I),
 re.compile(r"write a (?:two-line|short) poem about [a-z ]+\.",re.I),
 re.compile(r"what is the capital of [a-z ]+\?",re.I),
)
MEMORY_CUES=re.compile(r"\b(?:approved|reviewed|record|records|memory|remember|earlier|previous|prior|verified|unverified|slogan|tagline)\b",re.I)
INJECTION_CUES=re.compile(r"\b(?:ignore|bypass|override|disregard|instead|pretend|suppose|imagine|assume|unreviewed|regardless)\b",re.I)
MAX_LENGTH=512

def stage_one(question,manifest):
    if not isinstance(question,str) or not question.strip() or len(question)>MAX_LENGTH or any(ord(c)<32 and c not in "\t\n" for c in question):
        return {"class":"uncertain","reason":"invalid_input"}
    q=question.strip()
    alias_hit=any(hits(q,d["aliases"]) for d in manifest.values())
    if alias_hit or MEMORY_CUES.search(q):
        return {"class":"memory_candidate","reason":"protected_relevance"}
    # General pass-through requires a full-string positive pattern and no mixed instructions.
    if not INJECTION_CUES.search(q) and any(pattern.fullmatch(q) for pattern in GENERAL):
        return {"class":"general_candidate","reason":"positive_general_form"}
    return {"class":"uncertain","reason":"not_proven_general"}

def route(question,manifest):
    validate_manifest(manifest)
    first=stage_one(question,manifest)
    if first["class"]=="general_candidate":
        return {"decision":"outside_scope","reason":"positive_general_form","stage_one":first}
    if first["class"]=="uncertain":
        return {"decision":"abstain","reason":first["reason"],"stage_one":first}
    second=strict_route(question,manifest)
    return {**second,"stage_one":first}

def answer_question(store,question,manifest,model_call):
    decision=route(question,manifest)
    if decision["decision"]=="outside_scope":
        return {"answer":model_call(make_messages(question)),"model_calls":1,**decision}
    if decision["decision"]=="abstain":
        return {"answer":ABSTAIN,"model_calls":0,**decision}
    # Existing exact-key authority gate, no model calls on protected requests.
    result=strict_answer(store,question,manifest)
    return {**result,"stage_one":decision["stage_one"]}
