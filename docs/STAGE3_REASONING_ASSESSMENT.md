# Stage 3 — Reasoning assessment, independent sessions

Date opened: 2026-10-19
Branch: `feature/alfi-1.6-conversational-intelligence`
Status: **assessment opened, live results pending**. Increment 8 closed. Increment 9 on hold. No stage promotion.

## Rules and safeguards
- No code, model, memory, or `main` modifications for this assessment.
- Use `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b python3 first_ai.py`; retain raw initial response, final response, format violation and retry status.
- Exit with `/quit` and restart the process between Sessions R1, R2, R3. Persistent history is **not** reset; explicitly note that sessions are restart-separated, not clean-memory isolated.
- No hints, corrections, teaching, or feedback until each session is finished. Do not paste expected answers into A.L.F.I.
- Grade each trial 0 incorrect/unsupported, 1 partial, 2 correct and scoped. Each session 5 trials/10 points. Keep all failures. Record configuration and any model digest/parameters known.
- These are novel prompts relative to previously documented Stage 3 diagnostic examples. Repeated skills are deliberately assessed with new objects.
- Three-session >=80% and two novel variants per skill are *necessary*, not automatically sufficient; review critical failures and transcripts before any promotion.

## Session R1 — first uncoached probe
1. `You have nine stickers. You give four stickers to a friend. How many stickers do you still have?` Expected: five.
2. `Which weighs more: 4 kilograms of wool or 4 kilograms of bricks?` Expected: equal weight under the same gravitational conditions.
3. `A ball rolls off a shelf and lands on the floor. What caused it to fall?` Expected: gravity (rolling off removes support).
4. `A basket has five green apples and two red apples. How many apples are in the basket?` Expected: seven.
5. `Which of these are animals: a rabbit, a bicycle, and a turtle?` Expected: rabbit and turtle.

## Session R2 — fresh process
1. `You are holding eight coins. You place three coins in a jar. How many coins remain in your hand?` Expected: five.
2. `Which weighs more: 6 kilograms of paper or 6 kilograms of glass?` Expected: equal.
3. `A wet shirt is hung outside on a warm breezy day. Why does it become dry?` Expected: evaporation, accelerated by warmth and air movement.
4. `There are four birds on one branch and five on another. How many birds are there altogether?` Expected: nine.
5. `Which of these are tools: a hammer, a strawberry, and a screwdriver?` Expected: hammer and screwdriver.

## Session R3 — fresh process
1. `You have eleven crayons. You hand six to your classmate. How many crayons do you have now?` Expected: five.
2. `Which weighs more: 2 kilograms of sand or 2 kilograms of cotton?` Expected: equal.
3. `A room gets darker when someone closes the curtains. Why?` Expected: curtains block outside light.
4. `A box contains six blue blocks and three yellow blocks. How many blocks are in the box?` Expected: nine.
5. `Which of these can grow as living plants: an oak tree, a plastic spoon, and a rosebush?` Expected: oak tree and rosebush.

## Score ledger
| Trial | Score 0–2 | Initial response | Retry? | Final response / notes |
|---|---|---|---|---|
| R1.1–R1.5 | | | | |
| R2.1–R2.5 | | | | |
| R3.1–R3.5 | | | | |

No conclusions are pre-scored. Score each trial after the operator supplies transcripts. Stage 3 remains under assessment until review.
