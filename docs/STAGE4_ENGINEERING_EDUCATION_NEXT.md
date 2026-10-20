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
