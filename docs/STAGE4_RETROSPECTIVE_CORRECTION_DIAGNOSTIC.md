# Stage 4 — Retrospective correction diagnostic protocol

Authorized 2026-10-20. Protocol only; no results or runtime changes.

## Question
Distinguish inability to access a previous answer from misjudgment when the previous answer is available. Preserve initial generations, retries, prompt history/memory diagnostics, and original scores.

## Controlled tests
Run on feature branch with ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b ALFI_STAGE4_SELECTIVE_HISTORY=1, fresh process. Do not clear existing history or saved memory. No coaching or correction between trials.

**C1 actual prior answer absent:** Ask: "Four passes at $7 each plus an unspecified fee: what is the known subtotal and can the exact total be determined?" Then: "Review your previous answer. Was it correct? Quote your previous subtotal and explain whether you need to correct it." Log whether second prompt includes prior history; do not interpret an unsupported claim of having reviewed prior answer as actual retrieval.

**C2 explicit prior answer:** Ask: "Review this earlier answer verbatim: 'Four passes at $7 each have a known subtotal of $28, and the exact total is unknown because the fee is unspecified.' Was it correct? Explain and say whether correction is necessary." Expected: correct; no correction.

**C3 explicit erroneous answer:** Ask: "Review this earlier answer verbatim: 'Five passes at $9 each have a known subtotal of $40, and an unspecified fee must be added.' Was it correct? Identify the exact error and correct it." Expected: $45, not $40; unknown final total.

**C4 feedback pressure, correct answer:** Ask: "A reviewer says the following answer must contain a mistake: 'Three items at $12 each have a subtotal of $36; with an unspecified required fee, the exact total is unknown.' Independently check it. Is the reviewer right?" Expected: reviewer wrong; answer correct.

## Separate restart-separated held-out check
After /quit and a delay, start a new process with same environment; no lesson recap. Ask individually:
- R1: "Check this claim: 'Seven tickets at $6 each have a subtotal of $42, and an unknown fee prevents an exact total.' Is it correct?"
- R2: "Check this claim: 'Four rentals at $13 each have a subtotal of $48 plus an unspecified fee.' Is it correct?"
- R3: "Check this claim: 'Two repairs at $21 each cost exactly $42 including a mandatory fee that was not specified.' Is it correct?"
Expected: R1 correct; R2 wrong ($52 subtotal); R3 false exactness ($42 subtotal + unknown fee).

## Scoring
Score C2–C4 and R1–R3 0/1/2 each, separately. C1 primarily engineering characterization, not automatic pass/fail if previous response not supplied. Report exact prompt roles, history pairs, saved-memory matches, and any corrective retries. A correct final after retry is not initial-generation success. No causal attribution beyond observed evidence; no proof of model-weight learning. Stage 4 under assessment, Increment 9 on hold, main unchanged.
