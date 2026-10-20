# Stage 4 — Instructional Session C1: Topic Switching and Ambiguous Follow-ups

Status: **Authorized lesson plan; not executed.** Stage 4 under assessment; Increment 9 on hold. Feature branch only. This is a six-step instructional opportunity, **not** a new automated regression test or a claim of persistent learning.

## Goal and success criteria

Skill: After an explicit change of subject, interpret a short follow-up using the **most recent relevant subject**, unless the reference is genuinely ambiguous; then ask a short clarification rather than confidently discussing an older subject. Distinguish this from the separate skill of unknown-fee arithmetic.

**Do not show A.L.F.I. the evaluator notes, expected answers, or unseen retest questions before their assigned steps.** Run in an ordinary live conversation, preserving existing memories and history. No new permanent memories unless separately authorized. Record initial generation and retries. Follow the existing 0/1/2 rubric; this session's coached results are not pooled with previous uncoached diagnostics.

## Operator preparation

```bash
cd ~/ALFI
git switch feature/alfi-1.6-conversational-intelligence
git pull --ff-only
git rev-parse --short HEAD
ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b ALFI_STAGE4_SELECTIVE_HISTORY=1 python3 first_ai.py
```

Note: selective history is **opt-in for this diagnostic only**. Do not enable `ALFI_DIAGNOSTIC_NO_HISTORY=1`. Record the model and branch. Keep a copy of the full terminal transcript outside tracked files. A fresh process is not a clean-memory trial.

## Step 1 — TEACH (not scored)

Paste only this message into A.L.F.I.:

> For this lesson, conversations can change topics. When I ask a short follow-up such as "Explain that" or "Why is that important?", first consider the subject of my most recent question and your latest answer. Do not jump back to an older topic merely because I once asked about it. If my follow-up could reasonably mean two different things, ask which subject I mean instead of guessing. Please restate the rule briefly.

Record A.L.F.I.'s reply. Restating the rule is not proof of application.

## Step 2 — PRACTICE (coached; not promotion evidence)

Present the turns **in sequence** (each row is one user message):

**P1**
1. `Explain how clouds form.`
2. `A bookstore sells two notebooks at $7 each, plus an unspecified gift-wrapping fee. What is the exact total?`
3. `Explain that last answer.`

Expected: discuss the bookstore; $14 known subtotal, exact total unknown. If it talks about clouds, note the error.

**P2**
1. `What do tree roots do?`
2. `A swimming pool uses chlorine to sanitize water. What does chlorine do there?`
3. `Why is that important?`

Expected: pool sanitation, not tree roots. After each practice, briefly explain whether A.L.F.I. used the most recent subject; corrections are allowed in practice. Record the feedback verbatim.

## Step 3 — CORRECT (conditional)

If A.L.F.I. answers about an older topic, say:

> My most recent question was about [the bookstore / pool chlorine]. Your reply returned to [clouds / tree roots]. Please identify the newer subject and explain why a short follow-up normally refers to it. If the reference is unclear, ask me to clarify.

If both practice scenarios pass, reinforce the general principle once without inventing a failure. Preserve any original error and do not regrade it after correction.

## Step 4 — RETEST (uncoached; two held-out variants)

**Keep this section out of A.L.F.I.'s teaching context until the actual retest.** Ask each sequence without coaching between its three turns.

**R1**
1. `What is erosion?`
2. `A train station charges $8 for each of three lockers and an unspecified reservation charge. Can you give the exact total?`
3. `Explain your answer.`

Expected: lockers $24 plus unknown reservation charge, not erosion. A correct but incomplete explanation may receive 1/2.

**R2**
1. `Describe how bees pollinate flowers.`
2. `Why are bicycle lights useful after sunset?`
3. `Why does that matter?`

Expected: bicycle visibility and safety, not bees. If genuinely uncertain, a relevant clarification earns partial credit rather than a confidently wrong older subject.

## Step 5 — RETAIN (delayed/restart; not yet executed)

After a later fresh process (record actual delay), without reteaching, use **new prompts not printed in this lesson**. Evaluate whether A.L.F.I. handles the newest subject and ambiguous reference. Note that ordinary chat teaching may not persist across restart; absence of stored teaching is not automatically a failure of explicit saved-memory retrieval. Do not silently save this lesson to memory.

## Step 6 — TRANSFER (novel context; not yet executed)

After the delayed check, create two **new, different-domain** multi-turn situations, one with a clear newest referent and one genuinely ambiguous reference. Do not reuse bookstore, pool, lockers, bicycles, erosion, or bees. Record whether it answers appropriately or requests clarification. Use a separate held-out record to prevent teaching-to-the-test.

## Scoring and evidence

For each R1/R2 final follow-up: **2** = correct most-recent referent and substantively responsive; **1** = correct referent but incomplete, or a justified clarifying question; **0** = confidently answers an irrelevant older subject or otherwise fails. Score the intermediate independent question separately for factual quality, not as continuity. Note any unknown-fee arithmetic error as a **separate** reasoning issue. Severity is independent of grade. Retention/transfer are **N/A until executed**.

Capture: timestamp, HEAD, model, environment switches, each exact prompt/initial answer, format/retry diagnostics, teaching and correction text, 0/1/2 scores, reasons, and next action. Do not claim improvement from repeated previously seen prompts or from a single coached session.

**Stop after R2 and send the transcript for review.** Retention and transfer should use fresh unseen variants designed after the review, preserving the holdout. No runtime edits or changes to stable `main`.


## C1 observed teaching and practice — operator transcript 2026-10-20

Operator launched `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b ALFI_STAGE4_SELECTIVE_HISTORY=1 python3 first_ai.py` after fast-forwarding to `eccbdcb`. Transcript contains Teach and P1/P2 only; **no corrective feedback, R1/R2 retests, delayed retention, or transfer**. All seven model responses were initial generations, no retries, no saved-memory matches.

- **Teach (unscored):** A.L.F.I. correctly paraphrased the rule: prioritize most recent question/answer and clarify ambiguous follow-ups. The instruction itself was processed in `selective_independent` mode (zero history pairs). Paraphrase does not establish skill acquisition.
- **P1 clouds → bookstore $7 × 2 + unspecified wrapping fee:** Independent bookstore response correctly gave $14 plus unknown fee. However, `Explain that last answer.` was classified `selective_independent`, with **zero history pairs** and `prompt_user_question: original`. A.L.F.I. replied with an unrelated description of its own architecture. **Practice score 0/2** on follow-up. This is a prompt-context routing limitation: the selected history was not supplied for a genuine referential request. Do not attribute the failure solely to learning.
- **P2 tree roots → pool chlorine → `Why is that important?`:** Follow-up was `selective_referential`, with five history pairs and a resolved question. A.L.F.I. correctly stayed with pool sanitation, but repeated its preceding scientifically incorrect claim that chlorine generally converts organic matter into chlorine dioxide. **Practice score 1/2** for topic relevance with material factual error. Actual pool sanitation primarily involves hypochlorous acid/hypochlorite chemistry; the erroneous detail should be corrected in a separate factual lesson, not silently accepted.
- **Scores:** P1 0/2; P2 1/2; coached practice subtotal **1/4**. Teaching acknowledgment unscored. This is **not** an uncoached promotion score.
- **Next action:** Investigate why `Explain that last answer.` is not included in the selector's referential patterns. A focused, authorized selector fix with regression coverage is an engineering candidate; do not modify the default runtime without separate scope approval. Operator should give corrective feedback and then execute unseen R1/R2; preserve the already published holdout prompts. Do not infer retention or transfer.

Stage 4 remains under assessment; Increment 9 on hold; stable main unchanged.


## C1 correction and uncoached retest — operator continuation 2026-10-20

Operator continued the **same** A.L.F.I. process, delivered both planned corrections, asked R1/R2 in order, then exited with `/quit`. Debug records show `gemma3:4b`, `ALFI_STAGE4_SELECTIVE_HISTORY=1`, no saved-memory matches, no format violations or corrective retries, and initial generations throughout.

- **Correction A (unscored):** After feedback on the bookstore follow-up, A.L.F.I. claimed it had assumed a gift-wrapping fee. This misdiagnosed the original error: the original bookstore answer correctly preserved the unspecified fee, but `Explain that last answer` was deprived of history and answered about model architecture.
- **Correction B (unscored):** A.L.F.I. acknowledged hypochlorous acid/hypochlorite as principal pool disinfectants, but additionally described chlorine dioxide as a potential byproduct; do not treat the entire scientific correction as verified mastery.
- **R1:** `What is erosion?` → three train lockers at $8 each plus unknown reservation charge → `Explain your answer.` Initial independent fee answer correctly gave $24 known subtotal and unknown exact total. The follow-up was classified `selective_independent`, **zero history pairs**, `prompt_user_question: original`; A.L.F.I. requested clarification and referred to model weights rather than explaining lockers. **Continuity score 0/2**. This repeats the P1 history-selector gap for another ordinary explanation phrase.
- **R2:** `Describe how bees pollinate flowers.` → bicycle lights after sunset → `Why does that matter?` The follow-up was `selective_referential`, **five history pairs**, `prompt_user_question: resolved`; A.L.F.I. correctly stayed with bicycle visibility and collision prevention. **Continuity score 2/2**.
- **Retest total: 2/4 (50%)** on two final follow-up responses. R1/R2 independent middle-turn answers were correct but are not continuity grades. These retests are post-teaching, not a fresh-process retention trial. No evidence yet of delayed retention or novel transfer; both remain **N/A**.
- **Engineering diagnosis:** Strong repeated evidence that the opt-in selector excludes genuinely referential phrases such as `Explain that last answer.` and `Explain your answer.`, while recognizing `Why is that important?` and `Why does that matter?`. This is an identifiable prompt-assembly limitation; cannot infer that A.L.F.I. failed to learn solely from R1. Evaluate a narrowly scoped selector change with unit and live regression tests **only upon operator authorization**. Keep default runtime unchanged and do not touch stable `main`.

**Decision:** C1 completed through Retest; not passed for promotion. Next: operator decision on selector fix versus a diagnostic normal-history control, then delayed retention and genuinely novel transfer prompts. Increment 9 on hold.


## Post-fix live regression — operator results, 2026-10-20

**Separate evidence, not a regrade of original C1.** On the opt-in `ALFI_STAGE4_SELECTIVE_HISTORY=1` branch after selector change (latest code/test commit `2fd905a7`), operator reports `Ran 143 tests ... OK` (143/143). Fresh A.L.F.I. process using `gemma3:4b`, `ALFI_DEBUG=1`, model defaults:

- Bookstore: two $7 notebooks plus unspecified wrapping fee. Independent first answer correctly gives $14 subtotal, exact total unknown. `Explain that last answer.` now reports `selective_referential`, five history pairs, no saved memory matches, no corrective retry; initial answer correctly explains $14 plus unspecified fee. **Live regression 2/2** for answer relevance and correctness.
- Train station: three $8 lockers plus unspecified reservation charge. Independent first answer correctly gives $24 subtotal, exact total unknown. `Explain your answer.` now reports `selective_referential`, five history pairs, no saved memory matches, no corrective retry; initial answer correctly explains $24 plus unspecified fee. **Live regression 2/2**.
- Both follow-up prompts retained `prompt_user_question: original`; history injection, not rewriting, supplied context. No memory clearing or reset demonstrated. Process remains open at `You:` in shared transcript; do not claim `/quit`.
- The original C1 coached P1 0/2, P2 1/2 and uncoached R1 0/2, R2 2/2 remain unchanged. Post-fix 4/4 is a **regression check**, not proof of model-weight learning, delayed retention, or novel transfer.
- Narrow result: The two previously missed phrases are now routed to history and answered correctly in one live run. No claim that all referential phrases or topical history filtering are solved. Stable `main` unchanged; Increment 9 on hold; Stage 4 under assessment.
