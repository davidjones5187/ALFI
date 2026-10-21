# Stage 4 — Independent challenge evaluation E1 (2026-10-21)

**Scope:** 32 newly constructed, manually labeled challenge cases, evaluated against the **unchanged** standalone `diagnostics/stage4_contradiction_check.py`. Source and labels: `diagnostics/stage4_heldout_evaluation.py`. No live Ollama calls, no runtime integration, no model-weight changes. This is a small designed challenge set, not a representative statistical sample. The case labels are human-authored expected diagnostic classes, not live A.L.F.I. outputs.

## Results

- Exact four-class matches: **18/32 (56.25%)**.
- Contradictions: **TP 7**, **FN 8** of 15; **recall 46.67%**.
- Non-contradictions: **FP 1**, **TN 16** of 17; **precision 87.5%**, **false-positive rate 5.88%**.
- Abstentions and out-of-scope predictions combined: **14/32 (43.75%)**. Of these, 4 are the correctly labeled abstention/out-of-scope cases; the remainder reflect missed recognized claims.

| Ground truth / Predicted | contradiction | supported | insufficient_evidence | out_of_scope |
|---|---:|---:|---:|---:|
| contradiction | 7 | 3 | 3 | 2 |
| supported | 1 | 7 | 3 | 2 |
| insufficient_evidence | 0 | 0 | 2 | 0 |
| out_of_scope | 0 | 0 | 0 | 2 |

**Notable misses:** H05 false-positive reviewer disagreement (the response rejects reviewer but also calls original answer correct); H15–H17 correctly phrased verdict but unsupported invented fee or reasoning contradiction; H11–H12 synonym `valid/invalid`; H21–H24 explicit zero and optional fees; H25–H28 unfamiliar number word or item noun. Exact cases and reproducible evaluator are committed; no modification was made to the checker to improve this score.

## Ruling

**Independent challenge gate FAILED.** The checker does not satisfy a zero-false-positive goal and misses more than half of the designed contradictions. Do not integrate into A.L.F.I. runtime. Next step, subject to separate approval, is an offline-only revision addressing verdict-target disambiguation, negation/synonyms, and unknown-quantity assertions, followed by a **new sealed held-out set**, rather than rescore this set as independent after tuning.

**Reproduction (feature branch only):**
```bash
python3 diagnostics/stage4_heldout_evaluation.py
python3 -m unittest discover -s tests -v
```
The 32-case results above were generated with an isolated local copy of the existing checker. **The operator's full repository test suite has not yet been rerun after this evaluation-script commit.**

Stable v1.5.1 main untouched; Stage 4 under assessment; Increment 9 on hold.
