# Stage 4 — Opt-in contradiction check: engineering proposal (P1)

**Status:** Proposal and offline evaluation design only. No runtime authorization or implementation. Approved for investigation 2026-10-21. Branch: `feature/alfi-1.6-conversational-intelligence`. Stable v1.5.1 `main` must not change. Increment 9 on hold.

## Evidence and problem statement

V2 first-attempt scores: ordinary review **2/8** (A1=0, A2=0, A3=0, A4=2); checklist-assisted **4/8** (B1=0, B2=2, B3=2, B4=0). Phases differed in order, processes, and saved-memory matches, so no causal efficacy claim. Errors included agreeing with a reviewer whose objection contradicts correct evidence, inventing a fee to explain an erroneous subtotal, equating a known subtotal plus unknown mandatory fee with the subtotal, and accepting a zero delay merely because zero is possible. Routing fix is a distinct, verified issue.

## Scope

Propose a **read-only, opt-in post-generation contradiction assessor**, invoked only on explicitly requested review/verification questions. It inspects the original user question and the model's **initial response** and returns a structured diagnostic: `supported`, `contradiction`, `insufficient_evidence`, or `out_of_scope`, with evidence spans and issue category. It must not silently edit the answer, alter memory/history, change generation settings, trigger a retry, or assert model-weight learning. No default behavior change.

This is a *candidate architecture*, not a claim that a general-purpose reliable verifier already exists. An LLM reviewing itself can repeat the same mistake; therefore begin with offline manual/structured annotation and adversarial tests before considering an LLM-based assessor or deterministic rules. The assessor must distinguish **claim under review** from **reviewer's opinion** and **unknown variable** from **zero**.

## Candidate evidence checks

1. Extract proposition(s): the quoted original claim, any third-party challenge, quantities, qualifiers such as `exactly`, `including`, `unknown`, `unspecified`.
2. Compute independently supported facts where unambiguous: quantity × unit rate; known subtotal; unknown additive term. Never infer an unknown fee from a difference between two asserted subtotals.
3. Determine what verdict the response actually issues and its target (quoted claim versus reviewer).
4. Compare evidence, uncertainty and verdict. Flag contradictions, unsupported exactness, and invented values. Do not flag legitimate conditionals such as 'if fee=0 then total=subtotal' unless they are asserted as established.
5. When uncertain about parsing, abstain (`insufficient_evidence`) rather than claiming a contradiction.

## Independent offline assessment before code

Construct a labeled corpus with the **eight V2 initial responses** (preserve phase identity and original scores) plus new held-out variants: correct and incorrect reviewer assertions, fee-zero explicitly specified, unknown mandatory fee, incorrect subtotal, optional fee, nonfinancial delays, and unrelated ordinary questions. Annotate claim target, known subtotal, unknowns, expected verdict, actual verdict, and error type. Keep labels and model-generated assessments separate.

Evaluate a candidate assessor in a standalone diagnostic script or manual worksheet first, without integration into `first_ai.py`. Record confusion matrix, precision/recall for true contradictions, false-positive rate on correct answers, abstention rate, and whether issues are detected before any retry. Minimum proposed gate for further consideration: **zero false-positive contradiction flags on the known-correct V2 examples**, no false assertion that unknown means zero, and independently successful held-out reviewer-pressure cases. These are design gates, not observed outcomes; expand sample size before a production decision.

## Non-goals and safeguards

- No general-purpose mathematical solver or replacement answer generator.
- No rewriting of A.L.F.I.'s answer in this proposal.
- No changes to `main`, stored memory, teaching state, or selective-history routing.
- No silent promotion of Stage 4 or authorization of Increment 9.
- Avoid overfitting to exact V2 wording; use novel held-out paraphrases and nonfinancial controls.

## Decision

**Proposal ready for review.** Next decision is whether to authorize **offline prototype/evaluation only**, with no runtime wiring. A runtime opt-in implementation requires a later explicit approval after results are examined.
