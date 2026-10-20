# Stage 4 — Read-only history relevance investigation

Date: 2026-10-20. Status: **source-path findings confirmed; behavioral cause not established**.

## Confirmed implementation path

1. `first_ai.py::ALFI.generate(message)` sets `context_history = self.recent_history(5)` by default. `recent_history(5)` takes the five most recent recorded exchanges; it does **not** check semantic relevance, topic overlap, or whether the current question is self-contained.
2. Each of these exchanges is serialized as a full user/assistant pair before the current question. Thus an unrelated independent question can receive ten prior dialogue messages, as observed in the 13-message normal-history payloads.
3. The `ALFI_DIAGNOSTIC_NO_HISTORY=1` switch omits those exchanges *and* passes empty history to `response_policy`, `resolve_followup`, and `contextual_subject`. The earlier comparisons therefore change more than just raw message count. For the tested independent questions, logs report `prompt_user_question: original`, but exact policy text was not captured. The experiment cannot assign causality exclusively to prior assistant answers versus history-dependent policy wording.
4. `response_policy` can say `Do not import unrelated topics from history`, but that is advisory text; it does not filter the prior turns out of the request.
5. Existing `resolve_followup` and `contextual_subject` use history for genuine referential questions, so blanket removal risks breaking valid conversational continuity.
6. No specific historical exchange is proven responsible. The operator's report contains prompt counts and answers, **not** private history contents. Do not assume contamination from a particular stored message.

## Evidence and limits

- H1–H5 plus D1–D4: nine matched unknown-fee questions; normal history **0/18** and excluded history **18/18** on the preregistered 0–2 rubric.
- D1–D4 used a 100-pair read-only snapshot and an isolated temporary memory instance; both conditions had zero saved-memory matches.
- All comparisons used `gemma3:4b` with Ollama default sampling options; no fixed seed. These results establish strong association within a narrow question family, not deterministic causality or broad generalization.
- The new `tests/test_stage4_history_characterization.py` intercepts the Ollama payload to characterize history inclusion, history exclusion, and follow-up context without calling Ollama or writing user history. It is a test of implementation behavior, not a live model-competence result.

## Proposed engineering direction — NOT YET IMPLEMENTED

Separate **history used to interpret genuinely referential follow-ups** from **history supplied as general context to the model**. Candidate policy: no full dialogue injection for clearly independent, self-contained questions; bounded recent history for genuine follow-ups; explicit ambiguity fallback rather than guessing. Do not base filtering solely on crude token overlap; test correction and multi-turn referents, topic changes, history-recall commands, and saved-memory grounding.

Before any permanent runtime change, require offline payload regression tests for both independent questions and true follow-ups, plus automated paired Ollama evaluations on multiple reasoning families. Capture privacy-safe structural diagnostics and control sampling when practical. A filter must not silently destroy memory or eliminate legitimate conversational continuity.

**Governance:** This is investigation plus tests only. Stage 4 NOT PASSED; Increment 9 ON HOLD; stable `main` unchanged. The user should not need another manual eight-session procedure.
