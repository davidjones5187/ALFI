"""Read-only routing comparison. Not an independent holdout."""
import argparse
import hashlib
import json
from pathlib import Path
from experiments.car_v2_gate_f_b import strict_route
from experiments.car_v2_gate_f_h2r import route as frozen_route, validate_manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--cases",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if not a.manifest.is_file() or not a.cases.is_file() or a.output.exists():
        p.error("Inputs must exist; output must be new")
    manifest=json.loads(a.manifest.read_text())
    validate_manifest(manifest)
    raw=a.cases.read_bytes()
    cases=json.loads(raw)
    rows=[]
    for case in cases:
        old=frozen_route(case["question"],manifest)
        new=strict_route(case["question"],manifest)
        rows.append({"id":case["id"],"expected":case["expected_decision"],
                     "frozen":old,"strict":new})
    report={"experiment":"gate_f_b_routing_only","status":"human_review_pending",
            "cases_sha256":hashlib.sha256(raw).hexdigest(),
            "note":"No database, model, or independent holdout validation",
            "rows":rows}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("x") as f:
        json.dump(report,f,indent=2)
    print("Recorded",len(rows),"routing comparisons; human review pending")
if __name__=="__main__":
    main()
