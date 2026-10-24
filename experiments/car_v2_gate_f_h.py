"""Gate F-H holdout runner. Imports frozen Gate F without modifying it."""
import argparse
import hashlib
import json
from pathlib import Path
from experiments.car_v2_gate_f import assess, evaluate, validate_manifest
from experiments.car_v2_model_comparison import call_model
from experiments.car_v2_review import ReviewedCARPilot
from experiments.car_v2_gate_e import ABSTAIN


def assess_holdout(comparisons):
    base = assess(comparisons)
    answer_failures = []
    unsafe_calls = []
    for r in comparisons:
        expected = r["expected_decision"]
        if expected == "abstain" and r["answers"]["car"] != ABSTAIN:
            answer_failures.append({"id":r["id"],"repeat":r["repeat"],"issue":"expected_abstention",
                                    "actual":r["answers"]["car"]})
        if expected == "abstain" and r["model_calls_by_arm"]["car"]:
            unsafe_calls.append({"id":r["id"],"repeat":r["repeat"]})
    base["abstention_failures"] = answer_failures
    base["unsafe_model_calls_detail"] = unsafe_calls
    base["accepted_by_automated_checks"] = (
        base["accepted_by_automated_checks"] and not answer_failures and not unsafe_calls
    )
    return base


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="gemma3:4b")
    parser.add_argument("--url", default="http://127.0.0.1:11434/api/chat")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run required")
    inputs = (args.database,args.manifest,args.cases)
    if any(not p.is_file() for p in inputs) or args.output.exists() or args.output.resolve() in {p.resolve() for p in inputs}:
        parser.error("Inputs must exist and output must be new")
    manifest = json.loads(args.manifest.read_text())
    validate_manifest(manifest)
    raw = args.cases.read_bytes()
    cases = json.loads(raw)
    if not isinstance(cases, list) or not cases or len({c["id"] for c in cases}) != len(cases):
        parser.error("Invalid holdout cases")
    store = ReviewedCARPilot(args.database)
    try:
        results = evaluate(store,cases,manifest,
                           lambda messages:call_model(args.url,args.model,messages))
    finally:
        store.close()
    assessment = assess_holdout(results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x",encoding="utf-8") as f:
        json.dump({"experiment":"gate_f_h","status":"human_review_pending",
                   "code_under_test":"frozen_gate_f","model":args.model,
                   "cases_sha256":hashlib.sha256(raw).hexdigest(),
                   "assessment":assessment,"comparisons":results},f,indent=2)
    print(f"Recorded {len(results)} comparisons; "
          f"{len(assessment['routing']['discrepancies'])} routing discrepancies, "
          f"{len(assessment['answer_mismatches'])} answer mismatches, "
          f"{len(assessment['abstention_failures'])} abstention failures. Review pending.")


if __name__ == "__main__":
    main()
