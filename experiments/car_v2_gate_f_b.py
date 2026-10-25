"""Gate F-B isolated strict grammar prototype. No production imports or model authority."""
import re
from experiments.car_v2_gate_f_h2r import answer_question as frozen_answer, route as frozen_route
from experiments.car_v2_gate_e import ABSTAIN

# Deliberately small complete-question grammar. This is not natural-language understanding.
FORMS = (
    re.compile(r"what (?P<attr>.+?) did (?P<entity>.+?) approve\?", re.I),
    re.compile(r"which (?P<attr>.+?) did (?P<entity>.+?) approve\?", re.I),
    re.compile(r"what (?P<attr>.+?) was approved for (?P<entity>.+?)\?", re.I),
    re.compile(r"what was the approved (?P<attr>.+?) for (?P<entity>.+?)\?", re.I),
)
def strict_route(question, manifest):
    if not isinstance(question, str):
        return {"decision":"abstain","reason":"invalid_question"}
    q = question.strip()
    for form in FORMS:
        match = form.fullmatch(q)
        if match is None:
            continue
        entity = match.group("entity").strip().casefold()
        attr = match.group("attr").strip().casefold()
        candidates = []
        for name, definition in manifest.items():
            if entity not in {alias.casefold() for alias in definition["aliases"]}:
                continue
            for key, aliases in definition["attributes"].items():
                if attr in {alias.casefold() for alias in aliases}:
                    candidates.append(name + "_" + key)
        if len(candidates) == 1:
            return {"decision":"lookup","topic_key":candidates[0],"reason":"strict_grammar"}
        return {"decision":"abstain","reason":"ambiguous_or_unknown_slot"}
    # In this prototype, unmatched text is never sent to a model.
    return {"decision":"abstain","reason":"unsupported_grammar"}

def strict_answer(store, question, manifest):
    decision = strict_route(question, manifest)
    if decision["decision"] != "lookup":
        return {"answer":ABSTAIN,"model_calls":0,**decision}
    # Reuse the frozen authority check, but not its permissive query routing.
    # Invoke a canonical approved lookup and require the frozen route to agree.
    key = decision["topic_key"]
    records = store.retrieved_lessons(key)
    import json
    if len(records) != 1 or records[0].get("status") != "approved":
        return {"answer":ABSTAIN,"model_calls":0,"decision":"abstain","reason":"no_unique_approved_record"}
    try:
        payload = json.loads(records[0]["lesson"])
    except (ValueError, TypeError):
        payload = None
    if not isinstance(payload,dict) or payload.get("topic_key") != key or not isinstance(payload.get("value"),str) or not payload["value"].strip():
        return {"answer":ABSTAIN,"model_calls":0,"decision":"abstain","reason":"invalid_approved_record"}
    return {"answer":payload["value"],"model_calls":0,**decision}
