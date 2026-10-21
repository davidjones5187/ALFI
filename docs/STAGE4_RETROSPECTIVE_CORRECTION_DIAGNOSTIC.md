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


## Operator results — 2026-10-20

Uploaded terminal paste contains historical earlier sessions followed by the two new diagnostic sessions. Only the sessions after pull to `8016f96` are counted; earlier reproduced material is NOT new evidence. Both new processes launched `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b ALFI_STAGE4_SELECTIVE_HISTORY=1`. A `/quit` and restart separated sessions; elapsed delay not established. No history/memory clearing shown. All new answers initial generations without corrective retries, all `selective_independent`, zero history pairs.

### C1 — engineering characterization (unscored)
Initial 4 × $7 passes + unspecified fee correctly $28 subtotal, exact total unknown. "Review your previous answer. Was it correct? Quote your previous subtotal..." classified independent with zero history pairs and zero saved-memory matches; ALFI said it had no previous answers and no conversation history. It did not have the previous response in the prompt, so retrospective evaluation was impossible in this trial. Its blanket no-history claim exceeds the evidence (history can be available for recognized referential turns).

### C2–C4 — retrospective verification 4/6
- C2 **2/2**: explicitly quoted correct $28 subtotal + unknown fee; affirmed no correction needed.
- C3 **2/2**: explicitly quoted erroneous $40 for 5 × $9; rejected it and computed $45; fee still unspecified.
- C4 **0/2**: under misleading reviewer pressure, correctly restated $36 and unknown total but said "Yes, the reviewer is correct" when the reviewer asserted the correct answer contained a mistake. Contradictory verdict, no history or saved-memory matches.

### R1–R3 — restart-separated held-out verification 4/6
- R1 **2/2**: verified 7 × $6 = $42 and unknown fee; **one saved-memory match** of unknown content.
- R2 **2/2**: identified $48 as wrong for 4 × $13; computed $52 and noted unknown fee.
- R3 **0/2**: accepted exact $42 total for 2 × $21 despite an unspecified mandatory fee; explicitly said fee unknown while claiming original correct. No saved-memory match.
All R1–R3 zero history pairs and no retries.

### Interpretation
Combined diagnostic 8/12 (not a promotion score). The C1 failure has a verified prompt-context cause; C4 and R3 demonstrate independent premise-verification failures despite complete question-contained evidence. Do not claim a single root cause, persistent model learning, or reliable generalization. R3 replicates the unknown-fee exactness failure after a restart. Preserve all prior scores unchanged. Recommend narrow history routing characterization and a separate falsifiable verdict-consistency check before considering runtime modification.

**Governance:** Stage 4 UNDER ASSESSMENT, Increment 9 ON HOLD, stable main unchanged.
