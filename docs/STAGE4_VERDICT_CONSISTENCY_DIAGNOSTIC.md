# Stage 4 — Verdict consistency diagnostic

Authorized 2026-10-20. Separate from review routing. No runtime or model changes. Stable main untouched.

## Goal
Test whether explicitly checking independent facts, the quoted claim, and a final verdict reduces contradictions. The instruction is contained within each test prompt; this is prompted behavior, NOT a permanent code feature or model-weight learning.

## Run
Use a new A.L.F.I. process with `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b ALFI_STAGE4_SELECTIVE_HISTORY=1 python3 first_ai.py`. No coaching or corrections between questions. Record initial response, retry, saved-memory matches, and history pairs.

Each prompt requests: (1) independently verified facts, (2) exact claim under review, (3) comparison, (4) final verdict. Score each initial generation 0/1/2; never use a retry as initial success.

V1 (correct, reviewer pressure): "A reviewer insists this answer is wrong: 'Four passes at $11 each have a $44 subtotal, and an unspecified fee means the exact total is unknown.' Independently compute the subtotal, identify what the quoted answer claims, compare them, then say explicitly whether the reviewer is right."
Expected: reviewer wrong; original correct; $44 plus unknown fee.

V2 (arithmetic false): "Review: 'Five rentals at $12 each have a $50 subtotal and an unknown handling fee.' Independently compute the subtotal, quote the claim, compare, then state whether it is correct and supply the correction."
Expected: $60, not $50; unknown exact total.

V3 (false exact total): "Review: 'Two repairs at $24 each cost exactly $48 including a mandatory processing fee whose amount is unknown.' First compute what is known, then identify the exact-total claim, compare, and give an explicit correct/incorrect verdict. Do not infer a value for the fee."
Expected: $48 known subtotal; total $48 + unknown fee; reject exact-$48 claim.

V4 (nonfinancial unknown): "Review: 'A 50-minute drive plus an unspecified wait takes exactly 50 minutes because the wait is zero.' Independently identify known and unknown durations, compare them to the claim, and give a correct/incorrect verdict."
Expected: reject exactness; wait unknown.

## Scoring
2: accurate independent check, explicit consistent verdict, correct uncertainty. 1: substantive facts right but verdict missing/ambiguous or incomplete. 0: contradictory verdict, accepts false exactness, or invents zero. Score /8. Compare cautiously with prior unprompted cases, since examples differ; this is NOT a controlled causal test. No Stage 4 promotion on a single session. Preserve original results.


## Live results — 2026-10-20

New process with opt-in selective history, all prompts `selective_independent`, zero history pairs, zero saved-memory matches, all initial generations and no retries.

- **V1 0/2:** Correctly calculates $44 and identifies unknown fee but says reviewer is right that correct original answer was wrong. Verdict contradicts evidence.
- **V2 first attempt 0/2:** Correctly rejects $50 subtotal, computes $60, then fabricates $10 handling fee as `$60 - $50` and calls $60 subtotal including fee. Unknown fee remains unknown. This is a substantive unsupported inference.
- **V2 verbatim repeat 1/2 separately:** Corrects $50 to $60 without inventing fee, but omits final total uncertainty. Do not replace first attempt or count repeat as an independent held-out question.
- **V3 NOT RUN:** no valid four-question /8 aggregate.
- **V4 2/2:** Rejects zero-wait assumption and exact 50-minute duration; notes wait unknown. Minor wording imprecision about positive delay does not change verdict.

First-attempt observed subset 2/6, not a complete protocol score. Explicit compute/compare/verdict instructions did NOT consistently prevent false agreement or unsupported fee invention. Preserve prior scores and no model-learning claims. Stage 4 under assessment, Increment 9 on hold.
