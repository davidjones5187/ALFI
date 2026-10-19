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

## Foundational-first assessment policy (2026-10-19)

- Keep all new assessment questions at an everyday foundational level until evidence supports increasing difficulty. Use one concept per question, plain language, and minimal jargon.
- Before instruction or correction, run an **uncoached probe** using a new example. Do not reveal the expected answer to A.L.F.I. until its first response has been recorded.
- After a failure, test one comparable novel variant before deciding whether it is an isolated error or a repeated pattern. Then teach the general principle and test transfer with another novel example.
- Score observed answers, not presumed internal reasoning or learning. Record whether a response came before or after instruction and whether prior conversation/history may have primed it.
- Current Stage 3 follow-up probe: **"Which is heavier: 10 kilograms of cotton or 10 kilograms of steel?"** Expected: equal gravitational weight under the same conditions. Do not coach first.
- Current observations: Stage 1 6/6 initial, Stage 2 8/8 initial, Stage 3 4/6 initial (the 1 kg feathers/rocks comparison failed). All stages remain provisional until multi-session requirements are met.

## Stage 3 restart diagnostic — everyday reasoning (2026-10-19)

The initial Stage 3 sequence is closed for analysis, not declared passed. Seven observed trials: five-apples subtraction (2/2); ice melting (2/2); 1 kg feathers versus rocks (0/2); 10 kg cotton versus steel (0/2); define weight (1/2); equal masses and gravitational force (2/2); two 5 kg boxes (2/2). **Total 9/14 (64.3%)**. Correct answers after multiple weight-related questions may reflect conversational priming; no retention or independent learning is established.

Run a **fresh process/session**, without deleting or resetting persistent memory. Keep the current branch and model fixed; note the restart and existing memory state. Ask the following exact five questions in order without coaching, corrections, or feedback between them:

1. "You have six pencils and give two to a friend. How many pencils do you have left?" (subtraction; four)
2. "Which is longer: a 12-inch ruler or an 8-inch ruler?" (comparison; 12-inch ruler)
3. "A glass falls off a table and breaks. What most likely caused it to break?" (cause/effect; impact when it hit the floor)
4. "You have three red marbles and three blue marbles. How many marbles do you have altogether?" (addition; six)
5. "A cup of hot tea is left on a table. What will happen to its temperature as time passes?" (everyday physical reasoning; cools toward ambient temperature)

Score each 0–2 using the existing rubric (maximum 10). Preserve exact answers and the session metadata. This is a **restart-session diagnostic**, not an independent clean-memory trial; persistent memory may still influence answers. Compare results to the previous session without merging the new score into a claim of formal stage promotion. Stage 3 remains under assessment; Increment 8 open, Increment 9 on hold. Do not change application code, model, or stable main.

## Stage 3 restart diagnostic — observed results (2026-10-19)

User restarted with `python3 first_ai.py`; banner `A.L.F.I. 1.6-dev | Conversational Intelligence`. The five prescribed questions were asked in order without recorded intervening feedback:

1. Six pencils, give two away: "You still have six pencils. The transfer of pencils to your friend did not change the number of pencils you possess." **0/2** (incorrect; four remain).
2. 12-inch versus 8-inch ruler: "The 12-inch ruler is longer than the 8-inch ruler." **2/2**.
3. Glass falls and breaks: "The most likely cause of the glass breaking is the impact of the fall, which subjected the glass to a sudden and significant force that exceeded its structural integrity." **2/2**.
4. Three red and three blue marbles: "You have six marbles in total, as each color (red and blue) has an equal number (three) and they are combined." **2/2**.
5. Hot tea left on table: "The tea's temperature will decrease over time, as heat is transferred to the surrounding environment (the table and air) through conduction and convection, causing the tea to lose heat and eventually cool down." **2/2**.

**Fresh-session score: 8/10 (80%).** Prior diagnostic: 9/14 (64.3%). These are different test sets and not evidence of learning or a longitudinal score improvement. Stage 3 remains under assessment; one session at threshold does not satisfy three-session/novel-variant requirements. Failure may concern action/possession semantics, arithmetic application, or answer generation; do not assign a cause without discriminating probes. Next uncoached basic probe: "You have six pencils. You put two pencils in a drawer. How many pencils are still in your hand?" Expected four, assuming all six began in hand; if the user has not specified that, wording should be clarified to "You are holding six pencils. You put two in a drawer. How many are still in your hand?" No code/model changes; Increment 8 open, Increment 9 on hold.
