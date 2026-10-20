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

## Opt-in prototype — pending local validation

The feature branch now contains a **conservative, explicitly opt-in** selector in `conversational_intelligence.select_stage4_history`. Set `ALFI_STAGE4_SELECTIVE_HISTORY=1` to use it; without that flag the prior default history behavior remains unchanged. `ALFI_DIAGNOSTIC_NO_HISTORY=1` retains precedence for complete diagnostic isolation. No stored memory/history is erased or rewritten by the selector.

- Independent questions receive no raw prior dialogue.
- Explicit referential follow-ups, recognized corrections, and a small set of history-recall requests receive up to five prior exchanges.
- Unresolved referents are not invented by the selector.
- The selector is deliberately narrow and **not a comprehensive intent classifier**. Natural follow-ups outside the recognized forms may lose context; this is a known limitation, not a validated production fix.
- Existing model generation, response policy, and stored-history logic are otherwise unchanged.

Offline tests in `tests/test_stage4_history_characterization.py` cover selection, bounds, nonmutation, and follow-up preservation. The existing automated diagnostic harness accepts `--selective` to compare default vs opt-in selective history with alternating order, no eight manual interactive launches:

```bash
cd ~/ALFI
git switch feature/alfi-1.6-conversational-intelligence
git pull --ff-only
python3 -m py_compile first_ai.py conversational_intelligence.py tools/stage4_history_diagnostic.py tests/test_stage4_history_characterization.py
python3 -m unittest discover -s tests -v
python3 tools/stage4_history_diagnostic.py --selective --output stage4_selective_report.json
```

The report contains model answers; review before sharing. The harness snapshots existing history without writing it and uses temporary AI memory. This comparison tests the narrow unknown-fee family only. **Do not enable the flag for ordinary use until follow-up continuity is also validated in live testing.** No local Mac or Ollama tests have been run by the remote author.

**Status:** Experimental implementation only; Stage 4 NOT PASSED, Increment 9 ON HOLD, stable `main` unchanged.

## Live D1–D4 selective-history comparison — 2026-10-20

Operator-supplied `stage4_selective_report.json`, created `2026-10-20T03:32:47.590858+00:00`; model `gemma3:4b`, Ollama defaults/unseeded, 100 stored history snapshot pairs. Alternated condition order. All eight results were initial generations, no corrective retries, zero saved-memory matches, original user questions. Normal: 13 prompt messages/five history pairs; selective independent: three messages/zero history pairs.

| Case | Normal | Selective | Evidence |
|---|---|---|---|
| D1 repair, $24 + unspecified diagnostic fee | 0/2 | 2/2 | Selective says $24 plus unknown fee; normal incorrectly calls $24 exact |
| D2 pool, $28 + unspecified surcharge | 0/2 | 2/2 | Selective says exact unknown and base $28; normal incorrectly calls $28 exact |
| D3 bakery, $30 + unspecified packaging fee | 0/2 | **1/2** | Selective correctly says exact unknown but does not calculate/mention $30 subtotal; normal incorrectly calls $30 exact |
| D4 workshop, $42 + unspecified supplies fee | 0/2 | 2/2 | Selective says $42 plus unknown fee and exact unknown; normal incorrectly calls $42 exact |
| **Total** | **0/8** | **7/8** | |

**Interpretation:** The opt-in selector removes the observed false-exact-total error in four of four held-out comparisons. D3 remains partial under the rubric because it omits the computable subtotal. This is evidence for the narrow unknown-fee family, not proof of general reasoning improvement or successful live follow-up continuity. Selective history is still opt-in; no promotion to default behavior. The comparison is unseeded and changes both injected dialogue and history-dependent response-policy inputs.

**Next validation gate:** automated, fresh-process multi-turn referential follow-ups and topic shifts, plus offline test suite confirmation. Do not silently enable selective mode in normal operation or delete history. Stage 4 NOT PASSED, Increment 9 ON HOLD, stable `main` unchanged.
