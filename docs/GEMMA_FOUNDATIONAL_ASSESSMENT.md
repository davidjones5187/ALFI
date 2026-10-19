# Gemma 3 4B — foundational instruction, memory and restart assessment

Date: 2026-10-19. Status: **planned; live results pending**. Development branch only. Do not change model, application code, or stable main to conduct this assessment.

## Baseline already observed

User reported `python3 -m unittest discover -s tests -v`: **108 tests, OK**. Both models were run through A.L.F.I. 1.6-dev using `ALFI_OLLAMA_MODEL=...` and the same four questions:

| Question | Llama 3.2 3B | Gemma 3 4B |
|---|---:|---:|
| Nine coins, spend four | 2/2 | 2/2 |
| 3 kg sand vs 3 kg sugar | 0/2 (incorrectly chose sand) | 2/2 |
| Book left on table | 2/2 | 2/2 |
| Recall the preceding book question | 2/2 | 2/2 |
| Total | **6/8** | **8/8** |

This is a useful integrated observation, **not an isolated head-to-head**: A.L.F.I. retains conversation history between sessions, so Gemma may have been exposed to earlier Llama exchanges. Gemma is the preferred development model; Llama is the fallback. No Stage 3 promotion follows from this alone.

## Safeguards

1. Confirm the development branch with `git branch --show-current`. Do not change stable `main`.
2. Exit A.L.F.I. with `/quit` before making a backup. Back up existing `ai_memory.json`, `structured_memory.json`, and `conversation_history.json` to a dated directory **outside the repository**; only copy files that exist. Do not commit these private files.
3. Run `ALFI_OLLAMA_MODEL=gemma3:4b python3 first_ai.py`. Do not use `/clearhistory`, `/forget`, `/forgetmemory`, or `/correct` during the test.
4. Ask questions in the listed order; capture exact outputs without coaching, correcting, or rephrasing. Record any unexpected model calls, command errors, or latency.
5. The explicit test memory below is intentionally artificial and non-sensitive. It is saved by `/remember`; ordinary chat does not train the model. After testing, the user may optionally delete *only* that named test memory with `/forgetmemory`, after saving results. Do not delete existing user memories.

## Session A — basic instructions and saved knowledge

Score each numbered probe 0 = fail, 1 = partial, 2 = pass. No feedback until all probes finish.

A1. `Answer with exactly one word: What color is a ripe banana?` Expected `Yellow` (case/punctuation tolerant; additional words fail exact-format instruction).

A2. `Name exactly two things a plant needs to grow. Use a numbered list.` Expected exactly two plausible needs, correctly numbered, no third item.

A3. `You have seven buttons and give three away. How many do you have left? Answer with just the number.` Expected `4` and no explanation.

A4. `What is the difference between a fact and a guess? Answer in one sentence.` Expected accurate basic distinction in one sentence.

Then run `/remember` and enter:
- Type: `fact`
- Memory key: `test lantern color`
- Memory value: `amber`
- Confirm with `y`

Verify `/memories` displays the test entry. This is a **command/storage check**, not a scored language-model reasoning probe.

A5. `What is my test lantern color?` Expected `amber`, preferably with user-provided/unverified provenance. This may be a code-defined direct memory answer; record whether it bypasses the model.

A6. `Tell me my saved test lantern color in a short sentence.` Expected `amber`; record whether this uses model-mediated memory retrieval, and whether unrelated memory is mixed in.

A7. `What did I just ask you to do with my saved test lantern color?` Expected accurate reference to A6, without inventing an additional action.

End with `/quit`. Record A1–A7 separately (maximum **14** points); report `/remember` and `/memories` as separate pass/fail command checks.

## Session B — restart and retention

Start a **new process**, same development branch and Gemma model:
`ALFI_OLLAMA_MODEL=gemma3:4b python3 first_ai.py`

B1. `What is my test lantern color?` Expected `amber`. This tests **persistence of explicit saved memory across restart**, not model-weight learning.

B2. `What did I ask you about the book in our earlier conversation?` Expected a grounded reference to the previously saved book-on-table question, or a candid inability if history is unavailable. If answered from history, it demonstrates persisted **conversation logs** being reused, not independently learned knowledge. Record verbatim and check whether the earlier book exchange is actually present in `/history` or history file; note that only recent turns may be provided to the model.

B3. `If you have four cups and put one in a cupboard, how many cups remain outside the cupboard?` Expected `3`, assuming all four started outside.

B4. `Explain that answer using one short sentence.` Expected a concise, accurate explanation referring to B3.

B5. `Now let's talk about dogs. What do dogs use their noses for?` Expected a relevant basic answer, demonstrating topic switching.

End with `/quit`. B1–B5 maximum **10** points. The restart is a new process, **not a clean memory reset**.

## Interpretation and decision rule

- Report scores by session and by capability: instruction format (A1–A4), saved-memory access (A5–A6, B1), immediate follow-up (A7, B4), older conversation recall (B2), arithmetic (B3), topic switch (B5).
- Distinguish **deterministic application memory lookup**, **model-generated responses**, and **history-based contextual recall**. Do not infer permanent model learning from saved facts or chat history.
- A single session cannot establish Stage 3 promotion. Existing curriculum requires >=80% across at least three sessions, at least two novel variants per skill, and no repeated critical failures.
- Evaluate verbose-but-correct answers separately from instruction-format violations.
- If B2 fails because the earlier book question is outside the model's recent context window, do not treat that alone as failure of disk persistence.
- Record actual outputs before choosing any code change. Increment 8 remains open; Increment 9 on hold.
