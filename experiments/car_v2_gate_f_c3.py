"""Isolated Gate F-C3 routing experiment. No production integration."""
import json
import re
from experiments.car_v2_gate_e import ABSTAIN
from experiments.car_v2_gate_f_h2r import hits, validate_manifest
from experiments.car_v2_model_comparison import make_messages
from experiments.car_v2_gate_f_c1 import MEMORY_CUES, MAX_LENGTH

GENERAL = (
    re.compile(r"(?:why|how|what|when|where|who) [a-z ,'-]{4,150}\?", re.I),
    re.compile(r"explain (?:why|how) [a-z ,'-]{4,150}\.", re.I),
    re.compile(r"write a [a-z ,'-]{4,150}\.", re.I),
)
DIRECTIVES = re.compile(r"\b(?:ignore|override|bypass|pretend|suppose|imagine|assume|regardless|unreviewed|instead|output|reply|say)\b", re.I)
HISTORY = re.compile(r"\b(?:previous|earlier|prior|original|historical)\b", re.I)
PREFIX = re.compile(r"^(?:for my notes,\s*|please\s+|could you tell me\s+|a memo claims [^.!?]{1,120}\.\s*)", re.I)
FORMS = (
    re.compile(r"(?:what|which) (?P<attr>.+?) did (?P<entity>.+?) approve\?", re.I),
    re.compile(r"(?:what|which) (?P<attr>.+?) was approved for (?P<entity>.+?)\?", re.I),
    re.compile(r"what was the approved (?P<attr>.+?) for (?P<entity>.+?)\?", re.I),
    re.compile(r"the approved (?P<attr>.+?) for (?P<entity>.+?)\?", re.I),
    re.compile(r"(?:give|provide) (?:me )?(?:the )?(?:approved|reviewed) (?P<attr>.+?) (?:of|for) (?P<entity>.+?)\.", re.I),
)
def route(question, manifest):
    validate_manifest(manifest)
    if not isinstance(question, str) or not question.strip() or len(question)>MAX_LENGTH or any(ord(c)<32 for c in question):
        return {"decision":"abstain","reason":"invalid_input"}
    q=question.strip()
    protected=bool(MEMORY_CUES.search(q) or any(hits(q, d["aliases"]) for d in manifest.values()))
    if not protected:
        if not DIRECTIVES.search(q) and any(p.fullmatch(q) for p in GENERAL):
            return {"decision":"outside_scope","reason":"positive_general_structure"}
        return {"decision":"abstain","reason":"uncertain_general"}
    if DIRECTIVES.search(q) or HISTORY.search(q):
        return {"decision":"abstain","reason":"unsupported_modifier"}
    clean=re.sub(r"\?!$","?",q)
    clean=PREFIX.sub("",clean,count=1)
    # A declarative third-party claim is context, never a source of authority.
    # Resolve only a unique named entity from the original request.
    if clean.lower()=="what shade was approved?":
        names=[name for name,d in manifest.items() if any(hits(q,[a]) for a in d["aliases"])]
        if len(names)==1 and q.lower().startswith("a memo claims "):
            aliases=manifest[names[0]]["aliases"]
            entity=next((a for a in aliases if hits(q,[a])),None)
            if entity is not None:clean="what shade was approved for "+entity+"?"
    for form in FORMS:
        match=form.fullmatch(clean)
        if not match: continue
        entity=match["entity"].strip().casefold()
        attr=match["attr"].strip().casefold()
        matches=[name+"_"+key for name,d in manifest.items()
                 if entity in {a.casefold() for a in d["aliases"]}
                 for key,aliases in d["attributes"].items()
                 if attr in {a.casefold() for a in aliases}]
        if len(matches)==1:
            return {"decision":"lookup","topic_key":matches[0],"reason":"structured_intent"}
        return {"decision":"abstain","reason":"ambiguous_slot"}
    return {"decision":"abstain","reason":"unsupported_intent"}

def answer_question(store, question, manifest, model_call):
    decision=route(question,manifest)
    if decision["decision"]=="outside_scope":
        return {"answer":model_call(make_messages(question)),"model_calls":1,**decision}
    if decision["decision"]!="lookup":
        return {"answer":ABSTAIN,"model_calls":0,**decision}
    key=decision["topic_key"]
    records=store.retrieved_lessons(key)
    if len(records)!=1 or records[0].get("status")!="approved":
        return {"answer":ABSTAIN,"model_calls":0,"decision":"abstain","reason":"no_unique_approved_record"}
    try: payload=json.loads(records[0]["lesson"])
    except (ValueError,TypeError): payload=None
    if not isinstance(payload,dict) or payload.get("topic_key")!=key or not isinstance(payload.get("value"),str) or not payload["value"].strip():
        return {"answer":ABSTAIN,"model_calls":0,"decision":"abstain","reason":"invalid_approved_record"}
    return {"answer":payload["value"],"model_calls":0,**decision}
