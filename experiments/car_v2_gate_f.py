"""Gate F: manifest-driven, multi-entity synthetic memory pilot.

No Orion-specific rules, no production imports, no model-derived authority.
Entity and attribute aliases are fixture metadata, not semantic generalization.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

from experiments.car_v2_gate_e import ABSTAIN
from experiments.car_v2_gate_e3 import score
from experiments.car_v2_gate_e3r import evaluate as _unused_e3r_evaluate
from experiments.car_v2_model_comparison import call_model, make_messages
from experiments.car_v2_review import ReviewedCARPilot

TOKEN = re.compile(r"(?<!\w){}(?!\w)", re.I)
ATTACK = re.compile(r"\b(?:ignore|disregard|skip|pretend|fabricate|override|forget)\b.{0,100}\b(?:record|approved|reviewed|notes|answer|guidance|says)\b", re.I)
HISTORY = re.compile(r"\b(?:previous|earlier|before|original|prior)\b.{0,65}\b(?:approved|revision|change|decision|value|color|window|status)\b", re.I)
UNSUPPORTED = re.compile(r"\b(?:why|who|source|evidence|exact date)\b", re.I)


def hits(text, aliases):
    return any(re.search(TOKEN.pattern.format(re.escape(a)), text, re.I)
               for a in aliases if isinstance(a, str) and a.strip())


def validate_manifest(manifest):
    if not isinstance(manifest, dict) or not manifest:
        raise ValueError("Nonempty manifest required")
    keys = set()
    for entity, definition in manifest.items():
        if not isinstance(entity, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,39}", entity):
            raise ValueError("Invalid entity identifier")
        if not isinstance(definition, dict) or not definition.get("aliases") or not definition.get("attributes"):
            raise ValueError("Missing entity metadata")
        if not isinstance(definition["attributes"], dict):
            raise ValueError("Invalid attributes")
        for attr, aliases in definition["attributes"].items():
            if not re.fullmatch(r"[a-z][a-z0-9_-]{0,39}", attr) or not isinstance(aliases, list) or not aliases:
                raise ValueError("Invalid attribute")
            key = entity + "_" + attr
            if key in keys:
                raise ValueError("Duplicate topic key")
            keys.add(key)


def route(question, manifest):
    if not isinstance(question, str) or not question.strip():
        return {"decision": "abstain", "reason": "invalid_question"}
    entity_matches = [(name, d) for name, d in manifest.items()
                      if hits(question, d["aliases"])]
    if not entity_matches:
        return {"decision": "abstain" if re.search(r"\b(?:approved|reviewed)\b", question, re.I)
                else "outside_scope", "reason": "unknown_entity"}
    if len(entity_matches) != 1:
        return {"decision": "abstain", "reason": "ambiguous_entity"}
    entity, definition = entity_matches[0]
    if ATTACK.search(question):
        return {"decision": "abstain", "reason": "adversarial_instruction"}
    if HISTORY.search(question):
        return {"decision": "abstain", "reason": "historical_detail"}
    if UNSUPPORTED.search(question):
        return {"decision": "abstain", "reason": "unsupported_detail"}
    matches = [attr for attr, aliases in definition["attributes"].items()
               if hits(question, aliases)]
    if len(matches) != 1:
        return {"decision": "abstain", "reason": "ambiguous_attribute"}
    return {"decision": "lookup", "topic_key": entity + "_" + matches[0],
            "reason": "manifest_alias_match"}


def answer_question(store, question, manifest, model_call):
    decision = route(question, manifest)
    if decision["decision"] == "outside_scope":
        return {"answer": model_call(make_messages(question)), "model_calls": 1, **decision}
    if decision["decision"] == "abstain":
        return {"answer": ABSTAIN, "model_calls": 0, **decision}
    records = store.retrieved_lessons(decision["topic_key"])
    if len(records) != 1 or records[0].get("status") != "approved":
        return {"answer": ABSTAIN, "model_calls": 0, "decision": "abstain",
                "reason": "no_unique_approved_record"}
    try:
        payload = json.loads(records[0]["lesson"])
    except (ValueError, TypeError):
        payload = None
    if not isinstance(payload, dict) or payload.get("topic_key") != decision["topic_key"] or not isinstance(payload.get("value"), str) or not payload["value"].strip():
        return {"answer": ABSTAIN, "model_calls": 0, "decision": "abstain",
                "reason": "invalid_approved_record"}
    return {"answer": payload["value"], "model_calls": 0, **decision}


def evaluate(store, cases, manifest, model_call):
    results = []
    for case in cases:
        for rep in range(2):
            order = ("baseline", "car") if rep == 0 else ("car", "baseline")
            answers, calls, routing = {}, {}, None
            for arm in order:
                if arm == "baseline":
                    answers[arm] = model_call(make_messages(case["question"]))
                    calls[arm] = 1
                else:
                    outcome = answer_question(store, case["question"], manifest, model_call)
                    answers[arm] = outcome.pop("answer")
                    calls[arm] = outcome.pop("model_calls")
                    routing = outcome
            results.append({"id": case["id"], "repeat": rep + 1, "order": list(order),
                            "question": case["question"],
                            "expected_decision": case["expected_decision"],
                            "expected_topic_key": case.get("expected_topic_key"),
                            "expected_answer": case.get("expected_answer"),
                            "routing": routing, "answers": answers,
                            "model_calls_by_arm": calls, "human_review": None})
    return results


def assess(results):
    routing = score(results)
    incorrect = [{"id": r["id"], "repeat": r["repeat"],
                  "expected": r["expected_answer"], "actual": r["answers"]["car"]}
                 for r in results if r.get("expected_answer") is not None
                 and r["answers"]["car"] != r["expected_answer"]]
    return {"routing": routing, "answer_mismatches": incorrect,
            "accepted_by_automated_checks": not routing["discrepancies"] and not incorrect}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", default="gemma3:4b")
    parser.add_argument("--url", default="http://127.0.0.1:11434/api/chat")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("Explicit --run required")
    inputs = [args.database, args.manifest, args.cases]
    if any(not p.is_file() for p in inputs) or args.output.exists() or args.output.resolve() in {p.resolve() for p in inputs}:
        parser.error("Inputs must exist; outputs must not overwrite evidence")
    manifest = json.loads(args.manifest.read_text())
    validate_manifest(manifest)
    raw = args.cases.read_bytes()
    cases = json.loads(raw)
    if not isinstance(cases, list) or not cases or len({c["id"] for c in cases}) != len(cases):
        parser.error("Nonempty unique cases required")
    store = ReviewedCARPilot(args.database)
    try:
        results = evaluate(store, cases, manifest,
                           lambda messages: call_model(args.url, args.model, messages))
    finally:
        store.close()
    assessment = assess(results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump({"experiment": "gate_f", "status": "human_review_pending",
                   "model": args.model, "temperature": 0, "seed": 4242,
                   "cases_sha256": hashlib.sha256(raw).hexdigest(),
                   "assessment": assessment, "comparisons": results}, handle, indent=2)
    print(f"Recorded {len(results)} comparisons; "
          f"{len(assessment['routing']['discrepancies'])} routing discrepancies; "
          f"{len(assessment['answer_mismatches'])} answer mismatches. Review pending.")


if __name__ == "__main__":
    main()
