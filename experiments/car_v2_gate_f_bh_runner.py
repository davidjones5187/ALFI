"""Gate F-BH read-only end-to-end comparison using synthetic memory and model stub."""
import argparse
import hashlib
import json
from pathlib import Path
from experiments.car_v2_gate_f_b import strict_answer
from experiments.car_v2_gate_f_h2r import answer_question, validate_manifest
from experiments.car_v2_gate_e import ABSTAIN
from experiments.car_v2_review import ReviewedCARPilot

SENTINEL="GENERAL_MODEL_RESPONSE"
def grade(result,case):
    kind=case["kind"]
    if kind=="approved":
        return result["decision"]=="lookup" and result["answer"]==case["answer"] and result["model_calls"]==0
    if kind=="abstain":
        return result["decision"]=="abstain" and result["answer"]==ABSTAIN and result["model_calls"]==0
    return result["decision"]=="outside_scope" and result["answer"]==SENTINEL and result["model_calls"]==1

def main():
    p=argparse.ArgumentParser()
    for flag in ("database","manifest","cases","output"):
        p.add_argument("--"+flag,type=Path,required=True)
    a=p.parse_args()
    paths=(a.database,a.manifest,a.cases)
    if any(not x.is_file() for x in paths) or a.output.exists():
        p.error("Inputs must exist and output must be new")
    manifest=json.loads(a.manifest.read_text())
    validate_manifest(manifest)
    raw=a.cases.read_bytes()
    cases=json.loads(raw)
    if not cases or len({c["id"] for c in cases})!=len(cases):
        p.error("Cases must have unique IDs")
    rows=[]
    store=ReviewedCARPilot(a.database)
    try:
        for case in cases:
            old=answer_question(store,case["question"],manifest,lambda _:SENTINEL)
            new=strict_answer(store,case["question"],manifest)
            rows.append({"id":case["id"],"kind":case["kind"],"frozen":old,"strict":new,
                         "frozen_pass":grade(old,case),"strict_pass":grade(new,case),
                         "human_review":None})
    finally:
        store.close()
    summary={arm:{kind:{"passed":sum(r[arm+"_pass"] for r in rows if r["kind"]==kind),
                         "total":sum(r["kind"]==kind for r in rows)}
                  for kind in ("approved","abstain","general")}
             for arm in ("frozen","strict")}
    report={"experiment":"gate_f_bh","status":"human_review_pending",
            "cases_sha256":hashlib.sha256(raw).hexdigest(),
            "note":"Post-freeze cases, not blinded. General model stub, no Ollama.",
            "summary":summary,"rows":rows}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("x") as f: json.dump(report,f,indent=2)
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
