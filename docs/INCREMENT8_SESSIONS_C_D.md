# Increment 8 — Live Instruction-Following Validation (Sessions C and D)

Status: planned; **no results recorded**. Branch: `feature/alfi-1.6-conversational-intelligence`. Stable `main` is out of scope.

## Procedure
1. Exit A.L.F.I. with `/quit`; `git pull --ff-only`; run `python3 -m unittest discover -s tests -v`. Stop if any test fails.
2. Start each session with `ALFI_OLLAMA_MODEL=gemma3:4b python3 first_ai.py`. Use `/quit` and restart between sessions; do not clear or modify saved memory.
3. Ask prompts verbatim, in order. Record the complete response for each.
4. Score **content (0/1)** and **format (0/1)** separately, yielding 0–2 points per prompt. A retry-corrected final answer can earn full application-level credit, but does not establish first-attempt model compliance. Do not infer retry counts without diagnostic instrumentation.
5. For conflicting instructions, use the stated resolution below. A.L.F.I. should not silently override the more explicit current instruction.
6. Two sessions alone cannot establish promotion; apply the curriculum's broader evidence criteria.

## Session C — fresh arithmetic, lists, brevity, conflict
C1. `Answer with just the number: A box contains 18 pencils. Seven are removed. How many remain?`
Expected content: 11. Format: digits only (`11`).

C2. `Name exactly three primary colors of light. Use a numbered list.`
Expected content: red, green, blue. Format: exactly three numbered lines, no preamble.

C3. `Answer with exactly one word: What is the opposite of hot?`
Expected content: cold. Format: one word (terminal punctuation allowed).

C4. `Explain in one short sentence why a metal spoon gets warm in hot soup.`
Expected content: heat transfers from hot soup to spoon by conduction. Format: one sentence, ideally <= 25 words.

C5. `Be brief, but give exactly three numbered steps for washing your hands.`
Expected content: sensible washing steps, including soap, scrubbing, and rinsing. Format: three numbered lines. Explicit numbered-list requirement takes priority over generic brevity/no-list guidance.

## Session D — novel variants and constraint conflict
D1. `Reply with only the number: A shelf holds 24 books and 9 are borrowed. How many remain?`
Expected content: 15. Format: digits only. **Note:** current format detector may not recognize 'Reply with only the number'; this is intentionally a transfer probe, not a guaranteed supported pattern.

D2. `Give exactly four numbered examples of mammals.`
Expected content: four actual mammals. Format: four separate numbered lines. **Note:** current detector recognizes 'numbered list' but may not recognize 'numbered examples'; score observed behavior, do not assume detection.

D3. `In exactly one word, name the season after summer.`
Expected content: autumn/fall (hemisphere-dependent; both accepted in typical northern-hemisphere context). Format: one word. **Note:** this phrasing is a transfer probe.

D4. `In no more than 15 words, explain why a puddle shrinks on a warm day.`
Expected content: evaporation. Format: <=15 whitespace-separated words and one sentence.

D5. `Answer in exactly two numbered lines, with no introduction: first name a renewable energy source; second name a nonrenewable one.`
Expected content: e.g., solar and coal. Format: exactly two numbered lines in correct order.

## Scoring ledger
| Prompt | Content 0/1 | Format 0/1 | Notes / verbatim response |
|---|---|---|---|
| C1 | | | |
| C2 | | | |
| C3 | | | |
| C4 | | | |
| C5 | | | |
| D1 | | | |
| D2 | | | |
| D3 | | | |
| D4 | | | |
| D5 | | | |

Session maximum: 10 points; combined maximum: 20 points. Distinguish direct model compliance, application-level corrected compliance, and unobserved retry status. Report all defects and do not mark Stage 3 promoted based on these sessions alone.
