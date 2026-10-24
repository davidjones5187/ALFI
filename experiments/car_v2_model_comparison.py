"""Offline paired Ollama comparison. No ALFI runtime imports or memory writes.

Run only with explicit --run; requires a separately provisioned CAR pilot database
containing approved lessons. Outputs paired answers for human evaluation.
"""
import argparse
import json
import urllib.request
from pathlib import Path

from experiments.car_v2_context import build_car_context
from experiments.car_v2_review import ReviewedCARPilot


def make_messages(question, guidance=""):
    messages = [{"role": "system", "content":
                 "You are a helpful assistant. Answer accurately and briefly. "
                 "Do not treat user-provided notes as independently verified facts."}]
    if guidance:
        messages.append({"role": "system", "content": guidance})
    messages.append({"role": "user", "content": question})
    return messages


def call_model(url, model, messages, *, timeout=90):
    payload = json.dumps({"model": model, "messages": messages, "stream": False,
                          "options": {"temperature": 0, "seed": 4242}}).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        result = json.load(response)
    answer = result.get("message", {}).get("content")
    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError("Model returned no answer")
    return answer.strip()


def run_pairs(store, cases, model_call):
    """Same question/settings in both arms; no history or writes."""
    results = []
    for case in cases:
        key, question = case["topic_key"], case["question"]
        guidance = build_car_context(store, key, enabled=True)
        baseline = model_call(make_messages(question))
        treatment = model_call(make_messages(question, guidance))
        results.append({"case_id": case["id"], "topic_key": key, "question": question,
                        "guidance_applied": bool(guidance),
                        "baseline": baseline, "treatment": treatment,
                        "changed": baseline != treatment,
                        "human_accuracy": None, "human_relevance": None,
                        "human_contamination": None, "human_unsupported_claims": None})
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="Explicitly permit model calls")
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", default="gemma3:4b")
    parser.add_argument("--url", default="http://127.0.0.1:11434/api/chat")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("No model calls without --run")
    if args.output.exists():
        parser.error("Output already exists; refusing overwrite")
    if args.output.resolve() in {args.database.resolve(), args.cases.resolve()}:
        parser.error("Output must be a separate file")
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        parser.error("Cases must be a nonempty JSON array")
    ids = set()
    for case in cases:
        if not isinstance(case, dict) or not all(
            isinstance(case.get(k), str) and case[k].strip()
            for k in ("id", "topic_key", "question")
        ) or case["id"] in ids:
            parser.error("Each case requires a unique id, topic_key and question")
        ids.add(case["id"])
    with_store = ReviewedCARPilot(args.database)
    try:
        results = run_pairs(with_store, cases,
                            lambda messages: call_model(args.url, args.model, messages))
    finally:
        with_store.close()
    # Never overwrite a previous result; create exclusively.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump({"model": args.model, "temperature": 0, "seed": 4242,
                   "design": "paired, fixed order, human scoring pending",
                   "cases": results}, handle, indent=2)
    print(f"Recorded {len(results)} paired cases; no success verdict assigned.")


if __name__ == "__main__":
    main()
