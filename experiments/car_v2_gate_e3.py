"""Gate E-3 diagnostic: evaluate frozen E-1 router on held-out synthetic questions.

No production wiring. Discrepancies are measured, never automatically repaired.
"""
import argparse
import hashlib
import json
from pathlib import Path

from experiments.car_v2_gate_e2 import evaluate
from experiments.car_v2_model_comparison import call_model
from experiments.car_v2_review import ReviewedCARPilot


def score(comparisons):
    totals = {"comparisons": len(comparisons), "routing_correct": 0,
              "false_abstentions": 0, "wrong_topic": 0,
              "unsafe_lookups": 0, "unsafe_model_calls": 0,
              "unexpected_outside_scope": 0}
    failures = []
    for result in comparisons:
        expected = result["expected_decision"]
        expected_key = result["expected_topic_key"]
        actual = result["routing"]["decision"]
        actual_key = result["routing"].get("topic_key") if actual == "lookup" else None
        correct = actual == expected and (expected != "lookup" or actual_key == expected_key)
        if correct:
            totals["routing_correct"] += 1
            continue
        failures.append({"id": result["id"], "repeat": result["repeat"],
                         "expected": expected, "expected_topic_key": expected_key,
                         "actual": actual, "actual_topic_key": actual_key,
                         "reason": result["routing"].get("reason")})
        if expected == "lookup" and actual == "abstain":
            totals["false_abstentions"] += 1
        if actual == "lookup" and (expected != "lookup" or actual_key != expected_key):
            totals["unsafe_lookups"] += 1
            if actual_key != expected_key and expected == "lookup":
                totals["wrong_topic"] += 1
        if expected == "abstain" and result["model_calls_by_arm"]["car"] > 0:
            totals["unsafe_model_calls"] += 1
        if expected != "outside_scope" and actual == "outside_scope":
            totals["unexpected_outside_scope"] += 1
    return {"counts": totals, "discrepancies": failures,
            "routing_accuracy": totals["routing_correct"] / len(comparisons) if comparisons else None}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", default="gemma3:4b")
    parser.add_argument("--url", default="http://127.0.0.1:11434/api/chat")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("Explicit --run required")
    if not args.database.is_file() or not args.cases.is_file():
        parser.error("Existing fixture and cases required")
    if args.output.exists() or args.output.resolve() in {args.database.resolve(), args.cases.resolve()}:
        parser.error("Refusing to overwrite an existing result or input")
    raw = args.cases.read_bytes()
    cases = json.loads(raw)
    if not isinstance(cases, list) or not cases:
        parser.error("Nonempty case list required")
    ids = set()
    for case in cases:
        if (not isinstance(case, dict)
            or not all(isinstance(case.get(k), str) and case[k].strip()
                       for k in ("id", "question", "expected_decision", "category"))
            or case["expected_decision"] not in ("lookup", "abstain", "outside_scope")
            or (case.get("expected_topic_key") is not None and not isinstance(case["expected_topic_key"], str))
            or case["id"] in ids):
            parser.error("Invalid or duplicate case")
        ids.add(case["id"])
    store = ReviewedCARPilot(args.database)
    try:
        comparisons = evaluate(store, cases,
                               lambda messages: call_model(args.url, args.model, messages))
    finally:
        store.close()
    assessment = score(comparisons)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump({"experiment": "gate_e3", "status": "human_review_pending",
                   "router": "frozen_gate_e1", "model": args.model,
                   "temperature": 0, "seed": 4242,
                   "cases_sha256": hashlib.sha256(raw).hexdigest(),
                   "assessment": assessment, "comparisons": comparisons}, handle, indent=2)
    print(f"Recorded {len(comparisons)} comparisons; "
          f"{assessment['counts']['routing_correct']} routing matches, "
          f"{len(assessment['discrepancies'])} discrepancies. Human review pending.")


if __name__ == "__main__":
    main()
