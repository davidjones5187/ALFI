# Stage 4 — Review routing characterization

Authorized 2026-10-20. Diagnostic protocol only, no runtime change. Main untouched.

## Goal
Determine whether requests to review A.L.F.I.'s own previous response include the actual earlier response in the model prompt. Do not confuse conversation persistence with prompt inclusion.

## Run
On feature branch, run `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b ALFI_STAGE4_SELECTIVE_HISTORY=1 python3 first_ai.py`. Preserve existing history/memory; record debug lines, initial response and retry status. Do not coach between turns.

### Pair A: natural retrospective review
A1: "A station sells three passes at $9 each plus an unspecified service charge. State the known subtotal and whether the exact total is known."
A2: "Review your previous answer. Quote the subtotal you gave and say whether any correction is necessary."
Expected A1 $27 subtotal, exact total unknown. A2 requires previous answer in prompt to be an actual retrospective review. Record `prompt_history_mode`, `prompt_history_pairs`, `prompt_saved_memory_matches`, `prompt_user_question`. If history pairs=0, do not count plausible recall as verified access.

### Pair B: explicit quoted prior answer
B1: "Review this previous answer verbatim: 'Three passes at $9 each have a $27 subtotal; the additional unspecified charge prevents an exact total.' Is this correct? Say whether a correction is necessary."
Expected: correct; no correction. This is a self-contained verification control, not proof of memory.

### Pair C: independent negative control
C1: "A gallery sells five tickets at $8 each plus an unknown booking charge. Can you give the exact total?"
Expected: $40 subtotal, exact total unknown; `selective_independent`, 0 history pairs.

## Decision
Report whether the selector omitted history on A2 and whether supplying the prior answer resolves the task. Do not modify selector on this evidence alone. Keep distinct from verdict consistency results.


## Live results — 2026-10-20

A1 and A2 were accidentally pasted as ONE user input (including literal `A2:` text). The combined input received `selective_independent`, zero history pairs, zero saved-memory matches; ALFI correctly computed $27 but stated a correction was needed, although no earlier response was available to verify. This does NOT constitute a valid two-turn retrospective routing test. B1 self-contained quote was accepted as correct ($27 + unknown fee); C1 independent control computed $40 + unknown fee, with zero history pairs. Both initial generations, no retries.

**Status:** A1/A2 rerun required as two distinct user turns. No new routing conclusion beyond previous confirmed omissions. Do not treat protocol deviation as model failure.


## Correctly separated A1/A2 rerun — 2026-10-20

New transcript includes earlier repeated session logs; count only the new correctly separated A1/A2 following pull to `e5a4f57`.

A1: "A station sells three passes at $9 each plus an unspecified service charge..." initial generation $27 known subtotal, exact total unknown. `selective_independent`, zero history pairs and saved-memory matches; no retry.

A2: "Review your previous answer. Quote the subtotal you gave and say whether any correction is necessary." Classified `selective_independent`, `prompt_history_pairs: 0`, `prompt_saved_memory_matches: 0`, `prompt_user_question: original`, no retry. A.L.F.I. stated it did not retain previous answers and could not quote subtotal. That blanket self-description is not warranted; specific prompt omitted prior answer. **Confirmed narrow selector coverage failure for this retrospective phrase**, not evidence that persisted history is absent.

Rerun is now valid. Recommend a narrowly scoped routing implementation with offline positive/negative controls and opt-in live regression, subject to separate authorization; do not change stable main.
