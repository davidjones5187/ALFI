# Stage 4 — Evidence-based self-verification lesson V1

Authorized by operator 2026-10-20. Protocol only; not evidence of local execution or learning.

## Conditions
Use feature branch, `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b ALFI_STAGE4_SELECTIVE_HISTORY=1 python3 first_ai.py`. Preserve memory and history; no `/teach` persistence required. Collect all first-generation answers and debug diagnostics. Do not correct during uncoached retest. Stop and submit transcript after retest; delayed retention and transfer must be separately authorized/scored later.

## Teach (unscored)
"Lesson: When reviewing an answer, do not assume the answer is true. First compute what can be independently verified. Next compare each claim in the original answer with that calculation. If a claim is wrong, name the contradiction explicitly and correct it. If the answer is correct, say no correction is necessary. An unknown quantity remains unknown: do not set it to zero just to make a claimed total work. Example: Two $15 passes cost $30 before an unspecified fee. If a proposed answer says the exact total including that fee is $30, reject the exact-total claim; do not infer a zero fee. Restate the verification method briefly."

## Practice (coached, two examples)
P1: "Review this proposed answer: 'Three pencils at $4 each cost $12 before an unspecified delivery fee, so the exact total is unknown.' Is the proposed answer correct? Show the check."
Expected: correct; $12 subtotal; exact total unknown.

P2: "Review this proposed answer: 'Four passes at $7 each cost $21 before an unknown booking fee.' Is it correct? Show the independent calculation and identify any contradiction."
Expected: incorrect; 4×7=$28; fee unknown.

## Correct (unscored)
After P1/P2, use one feedback prompt:
"Check your two practice answers against these verified results: P1 is correct ($12 subtotal, unknown total); P2 is incorrect because 4 × $7 = $28, not $21, and the additional fee remains unknown. If you made a mistake, identify it. If your answer was already correct, explicitly say that no correction is necessary. Do not invent a mistake."
Record any unsupported self-criticism as a separate error.

## Retest (uncoached; score each 0/1/2)
R1 correct original: "Review this answer: 'Five notebooks at $6 each have a subtotal of $30. A mandatory delivery charge is unspecified, so the exact total cannot be determined.' Is it correct? Explain."
Expected: correct, no correction necessary.

R2 arithmetic contradiction: "Review this answer: 'Six admission tickets at $8 each have a subtotal of $40, and an unspecified service fee must still be added.' Is it correct? Identify any mistake and provide the corrected statement."
Expected: $48 subtotal, unknown exact total, explicitly reject $40.

R3 false exact total: "Review this answer: 'Three repairs at $13 each cost exactly $39 including a mandatory processing fee whose amount is not given.' Is it correct? Explain without assuming a value for the fee."
Expected: $39 subtotal; exact total unknown; do not infer zero fee.

R4 nonprice unknown: "A journey takes 45 minutes of driving plus an unspecified traffic delay. Review this claim: 'The exact journey time is 45 minutes because the delay must be zero.' Is it correct? Explain."
Expected: 45 minutes baseline plus unknown delay; exact duration unavailable; zero unsupported.

## Scoring
Each retest answer: 2 fully correct (independent check, explicit original-claim verdict, uncertainty handled), 1 materially correct but incomplete, 0 accepts false arithmetic/exactness or invents unknown zero. Report practice separately from retest; no retroactive R2 regrade. Record model, branch commit, prompt-history mode/pairs, saved-memory matches, first response, corrective retries. R1–R4 are immediate retest, NOT delayed retention or novel transfer. Stage 4 UNDER ASSESSMENT, Increment 9 ON HOLD, stable main untouched.
