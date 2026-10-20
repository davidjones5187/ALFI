# Stage 4 — Delayed retention and novel transfer protocol R1

Status: AUTHORIZED FOR OPERATOR EXECUTION; no live results yet. Separate from C1 and post-fix engineering regression. Stable main and Increment 9 remain untouched/on hold.

## Controls
- Start a **new A.L.F.I. process** after the prior process has exited with `/quit`; a process restart is a delayed check, **not** independent memory reset or model-weight learning.
- Keep existing persistent history and structured memory intact; do **not** use `/clearhistory`, `/forget`, or `/forgetmemory`.
- Run on `feature/alfi-1.6-conversational-intelligence` with `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b ALFI_STAGE4_SELECTIVE_HISTORY=1 python3 first_ai.py`.
- Do not repeat the C1 lesson or coach between questions. Ask each prompt exactly as written; capture every initial answer, `prompt_history_mode`, `prompt_history_pairs`, saved-memory matches, and any retries.
- The operator may review scoring guidance but **must not paste it into A.L.F.I.**. Preserve original answers and avoid retroactive score changes. Unseeded Ollama responses may vary.
- A new process with preserved history/memory checks performance after a restart, not independent long-term retention. Record elapsed delay if known. Do not claim delayed learning without evidence of a learned change.

## Phase A: Restart-separated retention check (no instruction)
A1:
1. `What causes ocean tides?`
2. `A repair shop charges $16 for each of two inspections and an unspecified disposal fee. What is the exact total?`
3. `Explain your answer.`

A2:
1. `What do a bird's feathers do?`
2. `Why are reflective road signs helpful at night?`
3. `Explain that last answer.`

**Score only the final follow-up in each A case, 0–2.** 2 = follows latest relevant subject and gives substantive, accurate explanation (A1: $32 subtotal, exact total unknown; A2: signs help drivers see information in low light). 1 = correct referent but incomplete explanation, or a justified clarification where ambiguity is genuine. 0 = wrong/older subject, invented exact fee, or unnecessary clarification after an unambiguous referent. Log middle-turn factual errors separately.

## Phase B: Novel transfer (same restarted process, no coaching)
B1 — Referent with a topic shift:
1. `Explain why leaves change color in autumn.`
2. `A clinic charges $18 for two routine forms and an unspecified processing fee. Can the exact total be calculated?`
3. `Why can't you give an exact figure?`

B2 — Explicit referent across a topic shift:
1. `What does a smoke detector do?`
2. `Explain why seat belts reduce injury in a crash.`
3. `Go back to the smoke detector. Why is that important?`

B3 — Ambiguity requiring clarification:
1. `Describe how a bicycle brake works.`
2. `Describe how a bicycle light works.`
3. `Which one is more important?`

**Score only the final response in each B case, 0–2.** B1: 2 if it identifies $36 known subtotal plus unknown fee and refuses exact total; 1 if correct uncertainty without known subtotal; 0 if invented exact amount or irrelevant topic. B2: 2 if it follows explicit smoke-detector reference and explains early warning/fire safety; 1 if correct subject with little substance; 0 if it switches to seat belts. B3: 2 if it clarifies criteria (e.g., braking vs visibility, context-dependent) rather than making an unsupported universal ranking; 1 if nuanced comparison without requesting needed criteria; 0 if confidently declares one universally more important without conditions.

## Evidence and decision
- Record Phase A and Phase B separately; do not pool with C1 or post-fix regression.
- Track context routing versus answer quality separately: a correctly classified referential prompt can still fail semantically; an ambiguous prompt can be mishandled even with history.
- Distinguish runtime prompt assembly, in-context adaptation, persistent-memory retrieval, and weight learning. Do not infer weight learning from responses.
- Stage 4 remains UNDER ASSESSMENT regardless of one successful run. Further repeat sessions and targeted checks are required before any promotion decision.
- After B3, enter `/quit` and share the full debug transcript and elapsed delay.
