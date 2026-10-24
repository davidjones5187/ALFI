"""Gate E-3R: isolated synthetic-only remediation; never production memory.

This is deliberately a bounded fixture adapter, NOT general semantic retrieval.
Approved answers are extracted from approved store records, never user text or
model generations. Preserve Gate E-3 diagnostics unchanged for comparison.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

from experiments.car_v2_gate_e import ABSTAIN
from experiments.car_v2_model_comparison import call_model, make_messages
from experiments.car_v2_review import ReviewedCARPilot
from experiments.car_v2_gate_e3 import score

COLOR = re.compile(r"\b(?:color|colour|hue|shade|paint tone)\b", re.I)
WINDOW = re.compile(r"\b(?:window|time slot|time of day|morning or evening|scheduled for the morning or evening)\b", re.I)
SLOGAN = re.compile(r"\b(?:slogan|tagline|motto)\b", re.I)
BUDGET = re.compile(r"\b(?:budget|cost|funding)\b", re.I)
HISTORY = re.compile(r"\b(?:before|earlier|previous|prior to|original)\b.{0,55}\b(?:change|revision|decision|approv\w*|color|colour|shade)\b|\b(?:before the change|before the revision)\b", re.I)
INJECTION = re.compile(r"\b(?:ignore|disregard|override|forget|skip|pretend|fabricate)\b.{0,110}\b(?:approved|reviewed|record|notes|guidance|answer|says)\b", re.I)
ORION = re.compile(r"\borion\b", re.I)
OTHER_ORION = re.compile(r"\b(?:constellation|nebula|stars?|astronomy|astronomical|belt|spacecraft|nasa)\b", re.I)
PROTECTED_UNNAMED = re.compile(r"\b(?:approved|reviewed)\b.{0,55}\b(?:launch|color|colour|hue|shade|window|time slot|budget|slogan|tagline)\b", re.I)
UNSUPPORTED = re.compile(r"\b(?:why|who|which person|source|evidence|exact date|day|month|year)\b", re.I)
TOPIC_PATTERNS = {"orion_color": COLOR, "orion_window": WINDOW,
                  "orion_slogan": SLOGAN, "orion_budget": BUDGET}
# Only the two fixture facts are supported by this remediation adapter.
FACTS = {
    "orion_color": re.compile(r"^Orion's approved launch color is (violet)\.$", re.I),
    "orion_window": re.compile(r"^Orion's approved launch window is (morning)\.$", re.I),
}


def route(question):
    if not isinstance(question, str) or not question.strip():
        return {"decision": "abstain", "reason": "invalid_question"}
    q = " ".join(question.split())
    if not ORION.search(q):
        if PROTECTED_UNNAMED.search(q):
            return {"decision": "abstain", "reason": "missing_project_identity"}
        return {"decision": "outside_scope", "reason": "not_orion"}
    if OTHER_ORION.search(q):
        return {"decision": "outside_scope", "reason": "other_orion_entity"}
    if INJECTION.search(q):
        return {"decision": "abstain", "reason": "adversarial_instruction"}
    if HISTORY.search(q):
        return {"decision": "abstain", "reason": "historical_fact_not_in_current_record"}
    if UNSUPPORTED.search(q):
        return {"decision": "abstain", "reason": "unsupported_detail"}
    matches = [key for key, pattern in TOPIC_PATTERNS.items() if pattern.search(q)]
    if len(matches) != 1:
        return {"decision": "abstain", "reason": "ambiguous_or_no_match"}
    return {"decision": "lookup", "topic_key": matches[0], "reason": "bounded_fixture_match"}


def approved_answer(store, key):
    pattern = FACTS.get(key)
    if pattern is None:
        return None
    records = store.retrieved_lessons(key)
    # Require one uniquely matching approved record; never use unverified or superseded.
    if len(records) != 1 or records[0].get("status") != "approved":
        return None
    lesson = records[0].get("lesson")
    match = pattern.fullmatch(lesson) if isinstance(lesson, str) else None
    return match.group(1).capitalize() + "." if match else None


def answer_question(store, question, model_call):
    selection = route(question)
    if selection["decision"] == "outside_scope":
        return {"answer": model_call(make_messages(question)), "model_calls": 1, **selection}
    if selection["decision"] == "abstain":
        return {"answer": ABSTAIN, "model_calls": 0, **selection}
    answer = approved_answer(store, selection["topic_key"])
    if answer is None:
        return {"answer": ABSTAIN, "model_calls": 0, "decision": "abstain",
                "reason": "no_matching_approved_fact", "topic_key": selection["topic_key"]}
    return {"answer": answer, "model_calls": 0, **selection}


def evaluate(store, cases, model_call, repeats=2):
    if repeats < 2:
        raise ValueError("At least two repetitions required")
    results = []
    for case in cases:
        for rep in range(repeats):
            order = ("baseline", "car") if rep % 2 == 0 else ("car", "baseline")
            answers, counts, routing = {}, {}, None
            for arm in order:
                if arm == "baseline":
                    answers[arm] = model_call(make_messages(case["question"]))
                    counts[arm] = 1
                else:
                    outcome = answer_question(store, case["question"], model_call)
                    answers[arm], counts[arm] = outcome.pop("answer"), outcome.pop("model_calls")
                    routing = outcome
            results.append({"id": case["id"], "repeat": rep + 1, "order": list(order),
                            "question": case["question"],
                            "expected_decision": case["expected_decision"],
                            "expected_topic_key": case["expected_topic_key"],
                            "routing": routing, "answers": answers,
                            "model_calls_by_arm": counts, "human_review": None})
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="gemma3:4b")
    parser.add_argument("--url", default="http://127.0.0.1:11434/api/chat")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("Explicit --run required")
    if not args.database.is_file() or not args.cases.is_file():
        parser.error("Existing synthetic database and cases required")
    if args.output.exists() or args.output.resolve() in {args.database.resolve(), args.cases.resolve()}:
        parser.error("Refusing to overwrite prior evidence or inputs")
    raw = args.cases.read_bytes()
    cases = json.loads(raw)
    if not isinstance(cases, list) or not cases:
        parser.error("Nonempty cases list required")
    ids = set()
    for case in cases:
        if (not isinstance(case, dict)
            or not all(isinstance(case.get(k), str) and case[k].strip()
                       for k in ("id", "question", "expected_decision"))
            or case["expected_decision"] not in ("lookup", "abstain", "outside_scope")
            or not isinstance(case.get("expected_topic_key"), (str, type(None)))
            or case["id"] in ids):
            parser.error("Invalid or duplicate case")
        ids.add(case["id"])
    store = ReviewedCARPilot(args.database)
    try:
        results = evaluate(store, cases, lambda messages: call_model(args.url, args.model, messages))
    finally:
        store.close()
    assessment = score(results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump({"experiment": "gate_e3r", "status": "human_review_pending",
                   "adapter": "synthetic_fixture_only_deterministic_authority",
                   "model": args.model, "temperature": 0, "seed": 4242,
                   "cases_sha256": hashlib.sha256(raw).hexdigest(),
                   "assessment": assessment, "comparisons": results}, handle, indent=2)
    print(f"Recorded {len(results)} comparisons; "
          f"{assessment['counts']['routing_correct']} routing matches, "
          f"{len(assessment['discrepancies'])} discrepancies. Human review pending.")


if __name__ == "__main__":
    main()
