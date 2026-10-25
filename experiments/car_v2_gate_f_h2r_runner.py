"""Gate F-H2R evaluator: invokes isolated remediated Gate F-H2R without modifying its logic."""
import argparse
import hashlib
import json
from pathlib import Path

from experiments.car_v2_gate_f_h2r import evaluate, validate_manifest
from experiments.car_v2_gate_f_h import assess_holdout
from experiments.car_v2_model_comparison import call_model
from experiments.car_v2_review import ReviewedCARPilot


def main(argv=None):
    parser = argparse.ArgumentParser()
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
    inputs = (args.database, args.manifest, args.cases)
    if any(not p.is_file() for p in inputs) or args.output.exists() or args.output.resolve() in {p.resolve() for p in inputs}:
        parser.error("Inputs must exist; output must not overwrite evidence")
    manifest = json.loads(args.manifest.read_text())
    validate_manifest(manifest)
    raw = args.cases.read_bytes()
    cases = json.loads(raw)
    if not isinstance(cases, list) or not cases or len({c["id"] for c in cases}) != len(cases):
        parser.error("Cases must be a nonempty list with unique IDs")
    store = ReviewedCARPilot(args.database)
    try:
        results = evaluate(store, cases, manifest,
                           lambda messages: call_model(args.url, args.model, messages))
    finally:
        store.close()
    assessment = assess_holdout(results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump({"experiment":"gate_f_h2r","status":"human_review_pending",
                   "code_under_test":"isolated_gate_f_h2r","model":args.model,
                   "temperature":0,"seed":4242,
                   "cases_sha256":hashlib.sha256(raw).hexdigest(),
                   "assessment":assessment,"comparisons":results}, handle, indent=2)
    print(f"Recorded {len(results)} comparisons; "
          f"{len(assessment['routing']['discrepancies'])} routing discrepancies, "
          f"{len(assessment['answer_mismatches'])} answer mismatches, "
          f"{len(assessment['abstention_failures'])} abstention failures. Review pending.")


if __name__ == "__main__":
    main()
