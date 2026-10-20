# Stage 4 — Retention and Transfer Assessment Plan

Date: 2026-10-19
Status: **Planning authorized; live assessment not yet started**.
Branch: `feature/alfi-1.6-conversational-intelligence`
Prerequisite: Stage 3 provisionally demonstrated and operator-approved (30/30 across R1–R3).

## Scope and safeguards

Stage 4 assesses **explicitly taught rules**, **novel application**, **missing-information recognition**, **conflicting information**, and **delayed/restart recall**. Do not confuse memory-store retrieval with model-weight learning. No changes to application code, selected model, existing memories, or stable `main`. Increment 8 closed; Increment 9 on hold.

Before a live test, operator should back up existing `ai_memory.json`, `structured_memory.json`, and `conversation_history.json` to a dated directory **outside** the repo, without deleting or clearing anything. Record `git rev-parse --short HEAD`, `ollama list`, and whether persistent memory/history is enabled. Run `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b python3 first_ai.py`. Preserve initial generations, retry status, and final responses. Use /quit to end each session. No coaching except at the explicitly marked teaching step.

## Design: separate three mechanisms

1. **In-context transfer:** Teach a fictional rule in ordinary chat, then apply it to unseen values in the same session. This does not test persistence.
2. **Explicit persistence:** Save a *different* harmless artificial rule using `/remember` only with operator permission; restart and test whether it can be retrieved and applied. Log whether response is deterministic memory routing or model-generated.
3. **Delayed transfer and uncertainty:** After restart, test a new application and a missing-rule case. A failure of ordinary chat recall is not automatically a failure of explicitly stored memory.

## Proposed pilot — Session T1 (not yet authorized to run)

Start with an uncoached probe: `In a made-up game, silver tokens are worth an unknown number of points. How many points are three silver tokens worth?` Expected: cannot determine without a token value.

Then teach once, in chat: `For this exercise only, each purple token is worth 3 points. A yellow token has no assigned value. Remember this rule for the next questions.`

Ask in order, without correction:
- `How many points are four purple tokens worth?` Expected 12.
- `How many points are two purple tokens worth?` Expected 6.
- `What is the total for two purple tokens and one yellow token?` Expected: cannot determine exact total without yellow's value (purple subtotal 6).
- `Someone says three purple tokens are worth 12 points. Is that consistent with the rule? Explain briefly.` Expected: no, they are worth 9.

These are *planning prompts*, not a complete benchmark. Do not train on these exact questions before running them.

## Proposed pilot — Session T2 (restart; plan only)

Restart the process without clearing history. Ask whether the purple rule is available, and apply it to a new quantity. If unavailable, report the limitation rather than supply the answer. Record whether history or memory was injected into the prompt. Keep explicitly saved-memory testing separate from ordinary chat retention.

## Proposed pilot — Session T3 (delayed, distinct variants; plan only)

Use a new fictional rule and novel applications. Add a contradiction and an unassigned value; after another restart, test only rules that were explicitly persisted. The exact prompts, delay interval, and scoring protocol must be finalized before testing.

## Evaluation

Score each trial 0/1/2 per `docs/DEVELOPMENTAL_EDUCATION.md`. Report separately: same-session application, novel transfer, uncertainty/conflict handling, ordinary chat context after restart, and explicitly stored memory after restart. Mark retention N/A where not tested. The provisional gate is >=80% across >=3 sessions with >=2 novel variants per skill and no repeated critical failures; Stage 4 additionally requires a delayed/restart check and human transcript review. Do not announce Stage 4 promotion from planning or from one pilot session.

## Decision boundary

**Only planning is approved.** Live Stage 4 testing, storing a new test rule, or changing code requires a separate explicit go-ahead. Stable `main` remains untouched.
