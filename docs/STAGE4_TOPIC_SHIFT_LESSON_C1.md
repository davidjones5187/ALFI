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
