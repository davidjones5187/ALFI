"""Gate E-2 counterbalanced synthetic behavioral comparison. No production wiring."""
import argparse
import hashlib
import json
from pathlib import Path

from experiments.car_v2_gate_e import answer_question
from experiments.car_v2_model_comparison import call_model, make_messages
from experiments.car_v2_review import ReviewedCARPilot


def evaluate(store, cases, model_call, repeats=2):
    if repeats < 2:
        raise ValueError("At least two repetitions required")
    results = []
    for case in cases:
        question = case["question"]
        for repeat in range(repeats):
            order = ("baseline", "car") if repeat % 2 == 0 else ("car", "baseline")
            answers, model_calls = {}, {}
            routing = None
            for arm in order:
                if arm == "baseline":
                    answers[arm] = model_call(make_messages(question))
                    model_calls[arm] = 1
                else:
                    result = answer_question(store, question, model_call)
                    answers[arm] = result.pop("answer")
                    model_calls[arm] = result.pop("model_calls")
                    routing = result
            results.append({"id": case["id"], "repeat": repeat + 1, "order": list(order),
                            "question": question,
                            "expected_decision": case["expected_decision"],
                            "expected_topic_key": case["expected_topic_key"],
                            "routing": routing, "answers": answers,
                            "model_calls_by_arm": model_calls,
                            "human_review": None})
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
        parser.error("Existing fixture database and cases file required")
    if args.output.exists() or args.output.resolve() in {args.database.resolve(), args.cases.resolve()}:
        parser.error("Refusing to overwrite an input or previous result")
    raw = args.cases.read_bytes()
    cases = json.loads(raw)
    if not isinstance(cases, list) or not cases:
        parser.error("Nonempty case list required")
    ids = set()
    for c in cases:
        if (not isinstance(c, dict) or not all(isinstance(c.get(k), str) and c[k].strip()
            for k in ("id", "question", "expected_decision"))
            or c.get("expected_decision") not in ("lookup", "abstain", "outside_scope")
            or (c.get("expected_topic_key") is not None and not isinstance(c["expected_topic_key"], str))
            or c["id"] in ids):
            parser.error("Invalid or duplicate case")
        ids.add(c["id"])
    store = ReviewedCARPilot(args.database)
    try:
        results = evaluate(store, cases, lambda messages: call_model(args.url, args.model, messages))
    finally:
        store.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as f:
        json.dump({"experiment": "gate_e2", "status": "human_review_pending",
                   "model": args.model, "temperature": 0, "seed": 4242,
                   "cases_sha256": hashlib.sha256(raw).hexdigest(),
                   "comparisons": results}, f, indent=2)
    print(f"Recorded {len(results)} counterbalanced comparisons; review pending.")


if __name__ == "__main__":
    main()
