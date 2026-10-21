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
