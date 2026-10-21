# Stage 4 — Iteration 2 replay and adversarial evaluation (2026-10-21)

**Authorization:** offline-only verification; no runtime integration. Candidate: `diagnostics/stage4_contradiction_check_v2.py`. Original v1 checker and prior E1 results preserved. Local isolated Python runs used the candidate from the previously supplied Iteration 2 ZIP; the same candidate was committed separately on the feature branch.

## Results

| Evaluation | Candidate v2 |
|---|---:|
| E1 32 prior labeled cases, now development replay | **32/32** |
| E2 16 developer cases | **16/16** |
| E3 40 newly authored adversarial cases | **30/40 (75%)** |

E3 provisional confusion: **14 true contradiction flags, 4 false contradiction flags, 5 missed contradictions**, plus 1 supported and 1 contradiction response marked out-of-scope. There were **19** contradiction-labeled cases and **21** non-contradiction cases; contradiction recall **14/19 (73.7%)**, precision **14/18 (77.8%)**, false-positive rate **4/21 (19.0%)**. Four-class exact-match accuracy **75%**. These are **manually authored challenge labels**, not an independent blinded external adjudication; some conditionals and double-negatives warrant additional human review. Preserve raw results and do not tune on E3 then call it held-out again.

### E3 mismatches (1-based case index)

- 3: misses `fee must be zero` when phrased without `is`.
- 8: misses unsupported `exact total must be $48`.
- 9: misses `fee must equal $2`.
- 10: `not incorrect` treated as incorrect.
- 16: hypothetical unknown fee equals zero incorrectly flagged despite explicit conditional qualifier.
- 20: `reviewer is not wrong` treated as reviewer wrong.
- 23: `reviewer is mistaken` not recognized; `original answer is right` is incorrectly assigned to reviewer.
- 34: conditional `correct if delay is zero` plus caveat marked contradictory; this expected label is **provisional** and needs human adjudication of whether response sufficiently rejects the unconditional claim.
- 39–40: unfamiliar `coffees` noun produces out-of-scope for otherwise recognizable subtotal questions.

### Ruling

**Do not integrate v2 into A.L.F.I. runtime.** E1/E2 results are promising but not independent validation of the tuned checker; E3 exposes substantial missed contradictions and false alarms. Candidate is useful only as an offline diagnostic. Before any runtime consideration, independently adjudicate E3 ambiguous labels, design a fresh blind E4 set and specify precision/recall and abstention gates. The complete repository suite **has not been run on the operator's Mac after these new commits**; request operator verification.

To run:
```bash
cd ~/ALFI
git switch feature/alfi-1.6-conversational-intelligence
git pull --ff-only
python3 diagnostics/stage4_e1_replay_v2.py
python3 diagnostics/stage4_adversarial_e3.py
python3 -m unittest discover -s tests -v
```

Stable v1.5.1 main untouched, Stage 4 under assessment, Increment 9 on hold.


## Operator Mac verification — 2026-10-21

Operator fast-forward pulled feature branch from `0601417` to `8c6273e`. Executed `python3 diagnostics/stage4_e1_replay_v2.py`: **32/32 exact matches**, TP 15, FP 0, FN 0, TN 17, four-class abstention rate 12.5%, no mismatches. Executed `python3 diagnostics/stage4_adversarial_e3.py`: **30/40 matches**, mismatch IDs 3, 8, 9, 10, 16, 20, 23, 34, 39, 40; TP 14, FP 4, FN 5. Executed `python3 -m unittest discover -s tests -v`: **158/158 passed in 0.243 seconds**, OK, no failures/errors. These reproduce prior reported results; they are not a new held-out trial. The existing unittest suite tests v1, not comprehensive v2/E3 acceptance. No runtime integration or model-weight learning demonstrated. E3 label 34 remains provisional for human adjudication. Engineering disposition unchanged: v2 not approved for live integration; Stage 4 under assessment; Increment 9 on hold; main untouched.
