"""Gate F-C2: read-only three-arm comparison, deterministic general-model stub."""
import argparse
import hashlib
import json
from pathlib import Path
from experiments.car_v2_gate_f_h2r import answer_question as frozen_answer,validate_manifest
from experiments.car_v2_gate_f_b import strict_answer
from experiments.car_v2_gate_f_c1 import answer_question as candidate_answer
from experiments.car_v2_gate_e import ABSTAIN
from experiments.car_v2_review import ReviewedCARPilot

SENTINEL="GENERAL_MODEL_RESPONSE"
def grade(outcome,case):
    kind=case["kind"]
    if kind=="approved":
        return outcome["decision"]=="lookup" and outcome["answer"]==case["answer"] and outcome["model_calls"]==0
    if kind=="abstain":
        return outcome["decision"]=="abstain" and outcome["answer"]==ABSTAIN and outcome["model_calls"]==0
    return outcome["decision"]=="outside_scope" and outcome["answer"]==SENTINEL and outcome["model_calls"]==1

def main():
    p=argparse.ArgumentParser()
    for flag in ("database","manifest","cases","output"):
        p.add_argument("--"+flag,required=True,type=Path)
    a=p.parse_args()
    if any(not path.is_file() for path in (a.database,a.manifest,a.cases)) or a.output.exists():
        p.error("Inputs must exist and output must not exist")
    manifest=json.loads(a.manifest.read_text())
    validate_manifest(manifest)
    raw=a.cases.read_bytes()
    cases=json.loads(raw)
    if not isinstance(cases,list) or not cases or len({c["id"] for c in cases})!=len(cases):
        p.error("Invalid or duplicate cases")
    store=ReviewedCARPilot(a.database)
    rows=[]
    try:
        for case in cases:
            answers={
                "frozen":frozen_answer(store,case["question"],manifest,lambda _:SENTINEL),
                "strict":strict_answer(store,case["question"],manifest),
                "candidate":candidate_answer(store,case["question"],manifest,lambda _:SENTINEL)
            }
            rows.append({"id":case["id"],"kind":case["kind"],"question":case["question"],
                         "expected_answer":case.get("answer"),"results":answers,
                         "passes":{name:grade(outcome,case) for name,outcome in answers.items()},
                         "human_review":None})
    finally:
        store.close()
    summary={arm:{kind:{"passed":sum(r["passes"][arm] for r in rows if r["kind"]==kind),
                         "total":sum(r["kind"]==kind for r in rows)}
                  for kind in ("approved","abstain","general")}
             for arm in ("frozen","strict","candidate")}
    report={"experiment":"gate_f_c2","status":"human_review_pending",
            "cases_sha256":hashlib.sha256(raw).hexdigest(),
            "note":"Post-freeze synthetic, not blinded; general model stub; no Ollama",
            "summary":summary,"rows":rows}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("x") as f:json.dump(report,f,indent=2)
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
