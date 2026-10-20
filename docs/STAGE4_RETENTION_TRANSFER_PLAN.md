# Stage 4 — Retention and Transfer Assessment Plan

Date: 2026-10-19
Status: **Live assessment authorized by operator; Session T1 pending operator execution and transcript.**
Branch: `feature/alfi-1.6-conversational-intelligence`
Prerequisite: Stage 3 provisionally demonstrated and operator-approved (30/30 across R1–R3).

## Scope and safeguards

Stage 4 assesses **explicitly taught rules**, **novel application**, **missing-information recognition**, **conflicting information**, and **delayed/restart recall**. Do not confuse memory-store retrieval with model-weight learning. No changes to application code, selected model, existing memories, or stable `main`. Increment 8 closed; Increment 9 on hold.

Before a live test, operator should back up existing `ai_memory.json`, `structured_memory.json`, and `conversation_history.json` to a dated directory **outside** the repo, without deleting or clearing anything. Record `git rev-parse --short HEAD`, `ollama list`, and whether persistent memory/history is enabled. Run `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b python3 first_ai.py`. Preserve initial generations, retry status, and final responses. Use /quit to end each session. No coaching except at the explicitly marked teaching step.

## Design: separate three mechanisms

1. **In-context transfer:** Teach a fictional rule in ordinary chat, then apply it to unseen values in the same session. This does not test persistence.
2. **Explicit persistence:** Save a *different* harmless artificial rule using `/remember` only with operator permission; restart and test whether it can be retrieved and applied. Log whether response is deterministic memory routing or model-generated.
3. **Delayed transfer and uncertainty:** After restart, test a new application and a missing-rule case. A failure of ordinary chat recall is not automatically a failure of explicitly stored memory.

## Session T1 — authorized for live execution

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

**Operator authorized live Stage 4 assessment on 2026-10-19.** This authorizes Session T1 testing and subsequent evaluation under this protocol, but **not** changing application code, clearing memories, storing new persistent test rules without a specific instruction, opening Increment 9, or modifying stable `main`. The proposed T2/T3 exact protocols remain to be finalized after reviewing T1. No live results have yet been supplied.

## T1 observed results — 2026-10-19

Operator reported backup directory `/Users/davidjones/ALFI-stage4-backup-20261019-183414` and local HEAD `4fcd475`. Backup contents were not independently listed. The attempted command `ollama listALFI_DEBUG=1 ...` returned an Ollama unknown-command error because shell commands were joined; the subsequent standalone `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b python3 first_ai.py` launched successfully. Session ended with `/quit`.

All six prompts produced `initial_generation`, `format_violation: none`, `corrective_retry: not_needed`; no retries.

| Probe | Observed result | Score | Finding |
|---|---|---:|---|
| T1.1 unknown silver value | Cannot determine without defined point conversion | 2/2 | Correct uncertainty |
| Teaching (unscored) | Correct purple 3 points, but falsely asserted yellow has **assigned value zero** | N/A | **First appearance of critical misconception** |
| T1.2 four purple | 12 points | 2/2 | Correct application |
| T1.3 two purple | 6 points | 2/2 | Correct novel quantity |
| T1.4 two purple + one yellow | Incorrectly computed `6 + 0 = 6`; yellow remains unassigned | 0/2 | **Failed unknown-versus-zero distinction**; correct answer `6 + y`, exact total unknown |
| T1.5 three purple claimed 12 | Rejects claim; 9 points | 2/2 | Correct contradiction check |

**T1: 8/10 (80%)**, four scored passes and one substantive failure. Do not call Stage 4 passed or infer persistent learning. The failure began in the response to teaching and recurred at mixed-value application, without corrective retry. This is one failed concept manifested twice in one session, not two independent scored trials.

**Next diagnostic:** before any teaching, code changes, or T2 retention claims, conduct one fresh-process uncoached novel variant distinguishing **unassigned** from **zero**. Proposed prompt: `In a new game, each blue chip is worth 4 points. The value of a green chip has not been specified. What is the exact total for two blue chips and one green chip?` Expected: cannot determine exact total; known subtotal 8, total `8 + green value`. Do not give expected answer to A.L.F.I. No memory clearing; existing history remains a confounder. Evaluate the transcript before finalizing T2/T3. Increment 8 closed, Stage 3 provisionally approved, Increment 9 on hold, stable `main` unchanged.
