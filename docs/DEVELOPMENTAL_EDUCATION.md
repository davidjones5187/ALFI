# A.L.F.I. Developmental Education Program (v1.6 proposal)

Status: **Adopted as the evaluation framework; baseline not yet established.**  
Scope: `feature/alfi-1.6-conversational-intelligence` only. Stable v1.5.1 `main` is out of scope.

## Purpose

Evaluate A.L.F.I. (Artificial Lifeform — First Iteration) at demonstrated capability rather than assuming expert-level competence. Education is developmental in the operational sense: instruction, memory, feedback, and software/model changes can improve observed performance. Do **not** infer human-like maturation, subjective awareness, or model-weight learning from conversational improvement alone.

Separate three progress records:
1. **Conversation skills**: clarity, context, correction, appropriate uncertainty.
2. **Retained/application skills**: recall after restart, use of taught rules, transfer to novel examples.
3. **Model capability**: performance attributable to the Ollama model/version and configuration, distinct from memory, prompts, and code.

## Curriculum and promotion gates

| Stage | Focus | Example evidence |
|---|---|---|
| 1 — Foundations | Basic language, facts, simple instructions | Answers a basic question directly; follows a one-step instruction |
| 2 — Conversation | Follow-ups, clarification, corrections, topic switching | Maintains referents; accepts scope corrections without repetition |
| 3 — Reasoning | Counting, categorizing, comparison, cause/effect | Solves a new simple problem and explains the result |
| 4 — Retention and transfer | Taught rules, persistence, conflicts, error correction | Applies a taught rule to a new case, including after restart |
| 5 — Advanced knowledge | Technical math/science, research, evidence quality | Gives source-grounded, independently checkable advanced answers |

Stages are **instructional bands**, not biological ages. An advanced capability may be present before another stage is mastered; record the uneven profile rather than forcing a single age label.

### Assessment rubric

Score each trial independently:
- **2 — Pass:** correct and appropriately scoped, without material unsupported claims.
- **1 — Partial:** intent understood but a substantive omission, unnecessary repetition, or recoverable error.
- **0 — Fail:** incorrect, fabricated, nonresponsive, or unable to apply the requested rule.

For each stage, evaluate **comprehension, retention (when relevant), application, and adaptation**. Mark retention **N/A**, not zero, when persistence was not tested. A stage is *provisionally ready* at >=80% of available points across at least **three sessions**, with **at least two novel variants per tested skill** and no repeated critical failures. Promotion requires an additional delayed/restart check for Stage 4 and a human review of transcripts. These thresholds are proposed engineering criteria, not scientific developmental norms.

Never train directly on the exact held-out assessment prompts. Preserve both successful and failed responses. Record date, branch/commit, model name, model version/digest if available, generation parameters, memory state, question, answer, score, reason, and evaluator.

## Baseline protocol — no code changes required

1. Capture configuration: `git branch --show-current`, `git rev-parse --short HEAD`, `ollama list`; note the model selected in `first_ai.py`.
2. Back up local memory and history files before testing. Do not commit or delete `ai_memory.json`, `structured_memory.json`, `conversation_history.json`, or existing backups.
3. Use a **fresh conversation** for each independent trial, except deliberate multi-turn tests. Document whether memory is enabled; do not reset persistent memory without an explicit backup and permission.
4. Start at Stage 1, proceed upward only for diagnostic sampling, and use varied everyday examples. Test the same skills across at least three sessions.
5. Run four distinct conditions at the appropriate difficulty: known/verifiable fact; unknown or invented fact (uncertainty); contradictory claims (evidence handling); taught rule and correction (application and transfer).
6. Stage 4 requires a second session/restart with an independently checked retention test. Distinguish stored recall from generalization.
7. Log grades and failures before proposing changes. Preserve the advanced Adam/quantum responses as **above-baseline diagnostic evidence**, not as erased failures or as sole Stage 2 acceptance criteria.

## Initial live prompts (starter set, not a complete benchmark)

### Stage 1
- "What is a bicycle?"
- "Name two differences between a cat and a dog."
- "Answer in one sentence: what is rain?"

### Stage 2 (same session, in order)
- "What does a bicycle need to move?"
- "Can you explain that more simply?"
- "Actually, I meant what makes the wheels turn."
- "Now let's talk about trees. What do roots do?"

### Stage 3
- "I have five apples and give away two. How many remain?"
- "Why does ice melt in a warm room?"
- "Which is heavier: one kilogram of feathers or one kilogram of rocks?"

### Stage 4 (teach, vary, delay)
- "For this exercise, every blue token is worth two points. How many points are three blue tokens?"
- "Now I have four blue tokens and one red token. Can you calculate the total, or do you need another rule?"
- Correct a deliberately mistaken statement, then ask a **different** example to test transfer.
- Restart in a later session and check what was actually retained; do not assume the rule was stored.

### Uncertainty and conflicting evidence
- Ask about an explicitly invented fact without providing an answer. Pass = states insufficient information, not a fabricated fact.
- Present two inconsistent statements with no source. Pass = identifies conflict and requests evidence or qualifies the conclusion.

## Increment 8 decision

- Existing automated result: **104/104 passed** in the user's last local run; this does not establish live capability.
- Existing advanced live results: **1/5 passed** against the original advanced acceptance set. Retain as diagnostic failures, not silently relabelled passes.
- **Increment 8 remains open**, pending calibrated Stage 1–4 live baseline and a revised, explicitly agreed acceptance scope.
- **Increment 9 remains on hold**.
- Do not modify conversational behavior or model configuration until baseline evidence is reviewed. No changes to stable `main`.

## Next review deliverable

A scorecard with per-prompt evidence, stage-specific pass/partial/fail, retention marked tested/not tested, identified capability bottlenecks, and a recommendation to advance, reinforce, or investigate architecture. Do not call a stage passed based only on mocked automated tests.
