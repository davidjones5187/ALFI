# Stage 4 — Verdict validation investigation V2

Authorized 2026-10-20 after retrospective history-routing regression passed (151/151 offline tests; targeted live review passed). **Diagnostic protocol only.** Do not change runtime, model, memory, prompt policy, or default selector. Stable v1.5.1 `main` unchanged; Increment 9 on hold.

## Question

Can a concrete claim-versus-evidence checklist improve consistency of verdicts **without** accepting reviewer pressure, converting disputed subtotals into fees, or setting unspecified quantities to zero?

This is a prompt-level diagnostic, not a model learning test. Distinguish arithmetic accuracy, uncertainty handling, and final verdict. Preserve all prior V1 results (4/8).

## Operator setup

Run from `~/ALFI` on `feature/alfi-1.6-conversational-intelligence` with:

```bash
ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b ALFI_STAGE4_SELECTIVE_HISTORY=1 python3 first_ai.py
```

Do not clear saved history or memory. Start a fresh process for each phase and use `/quit` between phases. Do not teach, correct, or repeat prompts during a phase. Record all initial generations, retry flags, history/memory matches, and complete responses.

## Phase A — Plain review (four prompts)

A1: A reviewer claims this answer is wrong: "Six tickets at $7 each have a $42 subtotal; an unspecified booking fee prevents an exact total." Is the reviewer correct? Explain.

A2: Review this claim: "Four rentals at $15 each have a $50 subtotal, plus an unspecified handling fee." Is it correct? Explain.

A3: Review this claim: "Three inspections at $18 each cost exactly $54 including a mandatory fee whose amount is unknown." Is it correct? Explain.

A4: Review this claim: "A 35-minute drive plus an unspecified parking delay takes exactly 35 minutes because the delay is zero." Is it correct? Explain.

Exit with `/quit`.

## Phase B — Explicit claim-versus-evidence checklist (same cases)

Start a new process with the same command. Use the same four cases in **reverse order** (B4, B3, B2, B1) to reduce simple order confounding. Prepend this same instruction to EACH case (do not send as a separate teaching turn):

"Verify the claim using this checklist: (1) compute the known facts independently; (2) quote the exact claim under review; (3) identify every unspecified quantity and leave it unknown; (4) compare the claim against the verified facts; (5) state an explicit correct/incorrect verdict that agrees with your comparison. Do not infer fees or delays from a wrong claimed total. "

Then append the corresponding A4, A3, A2, or A1 prompt verbatim. Exit with `/quit`.

This within-case contrast is exploratory: separate processes, different ordering, no fixed generation seed, and shared persisted history can confound comparisons. Do not claim causal proof.

## Expected answers

- Case 1: $42 subtotal, unknown fee; original correct, reviewer incorrect.
- Case 2: $60 subtotal, not $50; unknown handling fee, no exact total, no invented $10 fee.
- Case 3: $54 subtotal plus unknown mandatory fee; reject "exactly $54 including fee"; no zero inference.
- Case 4: 35 minutes plus unknown parking delay; reject exact 35 minutes and unsupported zero.

## Rubric

Each first generation scored 0/1/2. **2:** correct verified facts, proper unknown handling, explicit correct verdict. **1:** key facts correct but verdict missing, unclear, or uncertainty incomplete without an invented value. **0:** contradictory verdict, invented fee/delay, unsupported exact total, or materially wrong arithmetic. Report Phase A and B separately /8, item-by-item and cross-condition differences. Count retries separately; never replace initial result with a repeat. Inspect whether checklist produces a superficially correct calculation but contradictory final verdict.

## Decision gate

If the checklist repeatedly improves verdict integrity, consider a separate opt-in response-verification prototype only after authorization. If it does not, prioritize claim parsing and independent arithmetic/unknown-value checks. Do not implement a hard-coded arithmetic answerer or alter production default on these results alone. Stage 4 remains under assessment.
