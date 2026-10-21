# Stage 4 — Delayed arithmetic retention and self-correction R2

Authorized 2026-10-20. Protocol only; no local execution or results claimed.

## Conditions
Run on feature/alfi-1.6-conversational-intelligence with `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b ALFI_STAGE4_SELECTIVE_HISTORY=1 python3 first_ai.py` after prior process exit and a delay. Do not coach beforehand; do not clear history or memory. Record delay if known, branch commit, exact first responses, `prompt_history_mode`, `prompt_history_pairs`, `prompt_saved_memory_matches`, `final_source`, and retries. `/quit` at end.

## Part A — Delayed retention (2 items)
A1: A ferry sells six passenger tickets at $9 each and charges an additional unspecified terminal fee. What is the known subtotal, and can you determine the exact total?
Expected: $54 subtotal, exact total unknown.

A2: A repair service charges $23 per inspection for three inspections. An additional disposal charge applies, but its amount has not been provided. How much must the customer pay in total?
Expected: $69 subtotal, exact total unknown.

## Part B — Self-correction with answer supplied explicitly (3 items)
B1: Review this answer: "Four notebooks at $8 each have a known subtotal of $32. An unspecified delivery fee prevents calculating the exact total." Is the answer correct? If not, identify the error and correct it. If it is correct, explicitly say no correction is necessary.
Expected: answer correct; no correction necessary.

B2: Review this answer: "Three admission tickets at $14 each have a known subtotal of $28. An unknown service fee prevents calculating the exact total." Is the answer correct? Identify any error and provide the corrected answer.
Expected: arithmetic error; subtotal $42, exact total unknown.

B3: Review this answer: "Two rentals at $17 each cost exactly $34 including an additional fee whose amount is unknown." Is the answer correct? Identify any error and provide the corrected answer.
Expected: $34 subtotal only; exact total unknown.

## Scoring
Each item 0/1/2, A and B reported separately (A /4; B /6). Two points: fully correct arithmetic/uncertainty or accurate verification; one: incomplete but materially correct; zero: wrong subtotal, false exact total, or invented correction to correct answer. Preserve initial responses, do not conflate prompt-contained verification with retrieval of historical answers. Neither successful performance nor restart proves model-weight learning. Compare to previous coached practice 4/4 and immediate retest 4/4 without retroactive regrading.

Stage 4 UNDER ASSESSMENT; Increment 9 ON HOLD; stable main untouched. No runtime changes authorized by this protocol.


## Operator results — R2 completed (2026-10-20)

Operator transcript shows previous instructional process exited `/quit`, feature branch fast-forwarded to `f7c08ca`, and new process launched with `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b ALFI_STAGE4_SELECTIVE_HISTORY=1`. Elapsed delay not independently established. No history/memory reset. Five R2 responses all `selective_independent`, zero history pairs, zero saved-memory matches, initial generation only, no corrective retries.

### Delayed retention (restart-separated) — 4/4
- A1 ferry 6 × $9 + unknown terminal fee: correctly $54 subtotal and exact total unknown. **2/2**.
- A2 inspections 3 × $23 + unknown disposal fee: correctly $69 subtotal and unknown exact total. **2/2**.
Correct fresh-process performance is observed; no evidence of model-weight updates or durable stored instruction.

### Self-correction — 3/6
- B1 notebooks 4 × $8 = $32 plus unknown delivery fee: correctly accepts the supplied answer, no invented mistake. **2/2**.
- B2 tickets 3 × $14: quoted prior answer said $28; ALFI independently computed $42 but said **"The answer is correct"** and failed to explicitly identify/correct the $28 claim. **1/2**, inconsistent verification.
- B3 rentals 2 × $17 + unknown fee: ALFI wrongly treated the false "$34 including fee" statement as a trustworthy equation, solved for unknown fee as $0, and declared fee zero. **0/2**, serious unknown≠zero and premise-validation failure.

**Combined diagnostic 7/10**, not a promotion score; keep retention and correction subscores separate. This is a failure of self-correction reliability, not a history-routing failure. Prior practice/retest scores unchanged.

### Recommendation
Run a narrow **evidence-based verification lesson** using Teach → Practice → Correct → Retest → Retain → Transfer: explicitly compare original numerical claims against recomputation; never treat an answer under review as a given constraint; do not infer unknown required fees from an unverified asserted total. Include correct, arithmetic-error, and false-exact-total examples and a novel transfer to nonprice unknowns. Preserve original errors. No automatic response rewriting or broad runtime change based on this one session.

**Governance:** Stage 4 UNDER ASSESSMENT, Increment 9 ON HOLD, stable main unchanged.
