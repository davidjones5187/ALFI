"""Offline counterbalanced CAR comparison using an existing reviewed pilot database."""
import argparse
import json
from pathlib import Path
from experiments.car_v2_context import build_car_context
from experiments.car_v2_model_comparison import make_messages, call_model
from experiments.car_v2_review import ReviewedCARPilot


def compare(store, cases, model_call, repeats=2):
    if repeats < 2:
        raise ValueError("At least two repetitions required")
    results = []
    for case in cases:
        guidance = build_car_context(store, case["topic_key"], enabled=True)
        for repetition in range(repeats):
            order = ("baseline", "car") if repetition % 2 == 0 else ("car", "baseline")
            answers = {}
            for arm in order:
                answers[arm] = model_call(make_messages(
                    case["question"], guidance if arm == "car" else ""))
            results.append({"id": case["id"], "repeat": repetition + 1,
                            "order": list(order), "question": case["question"],
                            "guidance_applied": bool(guidance),
                            "answers": answers, "human_review": None})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", default="gemma3:4b")
    args = parser.parse_args()
    if not args.run:
        parser.error("Model calls require --run")
    if args.output.exists():
        parser.error("Refusing to overwrite results")
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases or any(
        not isinstance(c, dict) or not all(isinstance(c.get(k), str) and c[k].strip()
        for k in ("id", "topic_key", "question")) for c in cases
    ):
        parser.error("Cases must have id, topic_key, question")
    if not args.database.is_file():
        parser.error("Pilot database must already exist")
    store = ReviewedCARPilot(args.database)
    try:
        results = compare(store, cases, lambda messages: call_model(
            "http://127.0.0.1:11434/api/chat", args.model, messages))
    finally:
        store.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as out:
        json.dump({"model": args.model, "temperature": 0, "seed": 4242,
                   "status": "human_review_pending", "results": results}, out, indent=2)
    print(f"Recorded {len(results)} comparisons. Human review pending.")


if __name__ == "__main__":
    main()
