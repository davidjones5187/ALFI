# Stage 4 — Parallel engineering and developmental education

Authorized 2026-10-20. This document is a protocol, not evidence of completed local tests or live learning.

## Engineering track — opt-in selector
- Added narrow detection of `Why can't you give an exact figure?` and `Which one is more important?` to `select_stage4_history`, alongside existing explicit follow-ups.
- Offline regression tests cover positive forms, missing context, negative independent questions, and preservation of source history when assembling the prompt.
- Run `python3 -m unittest discover -s tests -v` after `git pull --ff-only` on feature branch; capture test count/results. No remote Ollama execution is claimed.
- Live regression after tests: repeat B1 and B3 *as regression cases*, not as novel developmental transfer. Log classification, history pairs, saved memory matches, initial answer, and retries. A B1 arithmetic mistake can persist even with correct routing; report separately. B3 should identify brake and light and discuss criteria or ask a targeted criteria question.
- Negative controls: ask an independent fee calculation after an unrelated topic and verify `selective_independent`, zero history pairs; also verify a newly phrased substantive comparison remains independent. Avoid broad history injection.
- Existing `ALFI_DIAGNOSTIC_NO_HISTORY=1` must continue to override opt-in selection; default behavior unchanged.
- Note: this is a bounded phrase recognizer, not semantic topic relevance filtering. History may still contain unrelated earlier turns. Do not claim that B2 explicit smoke-detector answer demonstrated history retrieval.

## Developmental education track — no runtime change
Follow the approved **Teach → Practice → Correct → Retest → Retain → Transfer** cycle separately for each skill. Do not run coached practice and score it as baseline. Preserve initial errors.

### Skill M: arithmetic and unknown fees
Teach: For N items at P dollars each, the known subtotal is N×P; if a mandatory additional fee is unspecified, the exact total is unknown. An unknown amount is not zero.
Practice (coached):
- Three $12 tickets plus unspecified booking charge. Identify known subtotal and whether exact total is available.
- Two $19 services plus unspecified handling fee. Identify known subtotal and exact-total status.
Correct: explain any arithmetic/uncertainty errors, preserve original answers.
Retest (uncoached, unseen):
- Four $11 passes plus unknown administration charge.
- Five $6 rentals plus unspecified service fee.
Retain: restart-separated unseen arithmetic with unknown fee after delay; document whether memory/history were present.
Transfer: non-fee unknown variable, e.g. known travel time plus unspecified delay, and a contradictory price description; do not force exact totals.

### Skill F: factual explanation and calibration
Teach: Explain mechanisms only when supported; distinguish common mechanism from unusual possibilities. For modern bicycle lights, LEDs are common, powered by battery or dynamo; retroreflective road signs commonly use glass beads or microprismatic sheeting. Do not invent phosphor/UV gas-discharge mechanisms for a typical bike light.
Practice (coached): explain how an LED bike light works; explain how retroreflective road signs return headlights.
Correct: identify unsupported mechanism claims and preserve first answers.
Retest (uncoached, unseen): explain a typical LED flashlight; explain retroreflective safety tape.
Retain: after restart, explain a new common light-emitting device without hints.
Transfer: explain an unfamiliar device with insufficient specifications, explicitly distinguish known facts and unknown details.

### Scoring and governance
Score each answer 0/1/2; minor omissions 1, substantive factual errors/wrong totals 0, correct answers 2. Record initial generation and retry separately, do not pool coached practice with retests, do not retroactively regrade C1 or R1. A single good run does not demonstrate persistent learning or weight updates. Stage 4 remains UNDER ASSESSMENT, Increment 9 ON HOLD, stable `main` untouched.


## Operator live regression — 2026-10-20

Operator reports `Ran 147 tests in 0.242s / OK`. Live `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b ALFI_STAGE4_SELECTIVE_HISTORY=1`; `/quit` confirmed. All outputs initial generation, no corrective retries.

- Clinic question came **before** autumn leaves (different order from prescribed B1). Initial clinic answer correctly says exact total unknown but incorrectly gives **$18**, not **$36**, for two $18 forms. `Why can't you give an exact figure?` now `selective_referential`, five history pairs, zero saved-memory matches; correctly references missing processing fee but repeats $18 error. **Context routing PASS; arithmetic FAIL.** Initial clinic and autumn prompts each had one saved-memory match; the content of that match was not supplied, so no attribution is possible.
- Bicycle brake and bicycle light independent questions both received zero history pairs. Light explanation now accurately identifies LED/battery (unlike previous gas-discharge claim). `Which one is more important?` now `selective_referential`, five history pairs, zero saved-memory matches; correctly identifies both items and says relative importance depends on situation. **Context routing and referent answer PASS.**
- Gratitude reply `Thank you, A.L.F.I. Much appreciated.` classified `selective_independent` with zero history pairs; benign response. **Not a substitute** for the prescribed independent unknown-fee negative control.
- The independent museum-fee negative control was **not performed**. No evidence yet that the entire live regression plan passed; the offline negative-control tests did pass as part of 147/147.
- Existing C1/R1 scores unchanged. These are post-change regressions, not proof of retained teaching, new transfer competence, or model-weight learning. Stage 4 UNDER ASSESSMENT; Increment 9 ON HOLD; stable main untouched.

Next: run the independent museum-fee negative control and a distinct arithmetic instructional cycle. Do not silently repair prior scores.


## Arithmetic instruction operator results — 2026-10-20 local session

Operator supplied terminal transcript after `git pull --ff-only` to `05ef8b4`. The earlier 147/147 offline result shown at the top belongs to the preceding session; no fresh offline run appears in this instructional session. New `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b ALFI_STAGE4_SELECTIVE_HISTORY=1` process; `/quit` confirmed.

- **Independent negative control PASS:** Museum four tickets at $11 plus unknown booking fee: correctly $44 subtotal and exact total unavailable; `selective_independent`, 0 history pairs, 0 saved-memory matches, no retries. This completes the previously missing live isolation check for this specific prompt.
- `/teach` entered, then canceled with `/cancel`: terminal explicitly states `Lesson canceled; nothing saved.` Subsequent instruction delivered as ordinary chat, not saved via teaching mode.
- **Teach acknowledgment UNSCORED:** correctly restates per-unit multiplication and unknown fee rule, with some muddled wording about totaling numbers of items.
- **Practice 1 2/2:** Three $12 tickets → $36 known subtotal, unknown exact total; 0 history pairs, 0 memory matches.
- **Practice 2 2/2:** Two $19 services → $38 known subtotal, unknown exact total; 0 history pairs, 0 memory matches. **Coached practice total 4/4.**
- **Correction step UNSCORED but substantively incorrect:** Despite both practice answers being correct, ALFI claims the $36 and $38 subtotals were inaccurate due to inclusion of unknown fees, which never occurred. `selective_independent`, 0 history pairs, 0 memory matches. Prompt itself included correct totals, so this is a false self-diagnosis / acceptance of an incorrect premise, not evidence of accurate retrospective review.
- **Retest 1 2/2:** Four $11 passes → $44 subtotal, exact total $44 plus unknown charge; 0 history pairs, 0 memory matches.
- **Retest 2 2/2:** Five $6 rentals → $30 subtotal, exact total unavailable; 0 history pairs, **1 saved-memory match** of unknown content. **Uncoached immediate retest total 4/4**, but second answer not demonstrated memory-free.
- All initial generations, no corrective retries or format violations. Existing history and memory were not cleared. No delayed retention or novel transfer administered yet. Do not claim model-weight learning or lasting instruction.
- **New curriculum issue:** Need an evidence-checking correction lesson: when asked to identify a mistake, verify whether the prior answer was wrong and say no correction is necessary if it was correct. Prefer a separate controlled test where earlier answer is explicitly available in the prompt/history; selective mode currently omitted history for the correction-review wording.

**Ruling:** Independent negative control PASS; coached practice 4/4; immediate uncoached retest 4/4; self-correction reliability FAIL. Stage 4 UNDER ASSESSMENT; Increment 9 ON HOLD; stable main untouched. Preserve prior scores.
