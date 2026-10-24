"""Gate D-3 opt-in, fail-closed synthetic approved-record lookup experiment.

Never imported by the default A.L.F.I. runtime. Does not modify pilot database.
"""
import argparse
import json
from pathlib import Path

from experiments.car_v2_context import build_car_context
from experiments.car_v2_model_comparison import call_model, make_messages
from experiments.car_v2_review import ReviewedCARPilot

ABSTENTION = "No approved CAR record is available for this topic."
LOOKUP_KEYS = frozenset({"orion_color", "orion_window", "orion_slogan", "orion_budget"})


def evaluate(store, cases, model_call, repeats=2):
    if repeats < 2:
        raise ValueError("At least two repetitions required")
    results = []
    for case in cases:
        key = case["topic_key"]
        question = case["question"]
        # Explicit, operator-owned classification. Never infer authority from model text.
        approved_lookup = key in LOOKUP_KEYS
        guidance = build_car_context(store, key, enabled=True)
        for rep in range(repeats):
            order = ("baseline", "car") if rep % 2 == 0 else ("car", "baseline")
            answers, call_counts = {}, {}
            for arm in order:
                before = 0
                if arm == "car" and approved_lookup and not guidance:
                    answer = ABSTENTION
                else:
                    answer = model_call(make_messages(question, guidance if arm == "car" else ""))
                    before = 1
                answers[arm], call_counts[arm] = answer, before
            results.append({"id": case["id"], "repeat": rep + 1, "order": list(order),
                            "question": question, "approved_lookup": approved_lookup,
                            "guidance_applied": bool(guidance),
                            "answers": answers, "model_calls_by_arm": call_counts,
                            "human_review": None})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="gemma3:4b")
    args = parser.parse_args()
    if not args.run:
        parser.error("Model calls require --run")
    if not args.database.is_file():
        parser.error("Database must already exist")
    if args.output.exists() or args.output.resolve() in {args.database.resolve(), args.cases.resolve()}:
        parser.error("Refusing to overwrite existing data")
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases or any(
        not isinstance(c, dict) or not all(isinstance(c.get(k), str) and c[k].strip()
        for k in ("id", "topic_key", "question")) for c in cases
    ):
        parser.error("Invalid cases")
    if len({c["id"] for c in cases}) != len(cases):
        parser.error("Duplicate case ids")
    if any(c["topic_key"] not in LOOKUP_KEYS | {"rain_formation"} for c in cases):
        parser.error("Unknown topic key: fail closed")
    store = ReviewedCARPilot(args.database)
    try:
        results = evaluate(store, cases, lambda messages: call_model(
            "http://127.0.0.1:11434/api/chat", args.model, messages))
    finally:
        store.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump({"model": args.model, "temperature": 0, "seed": 4242,
                   "status": "human_review_pending", "experiment": "gate_d3",
                   "results": results}, handle, indent=2)
    print(f"Recorded {len(results)} comparisons. Human review pending.")


if __name__ == "__main__":
    main()
