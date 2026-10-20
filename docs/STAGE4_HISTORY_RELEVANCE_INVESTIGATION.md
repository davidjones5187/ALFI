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

## Automated continuity gate — awaiting operator execution

Added `tools/stage4_continuity_diagnostic.py` and offline harness tests. Four synthetic scenarios (F1/F2 follow-up chains; T1/T2 topic shifts followed by referential questions) are run in both default and opt-in selective modes, with alternating condition order. Each sequence starts with empty synthetic in-memory dialogue; subsequent turns use the model's actual prior answer, not a canned response. The 8 sequences comprise **24 generated turns** in one invocation. No stored conversation history is read or written, no `ALFI.record()` is invoked, and each ALFI instance uses temporary memory files.

```bash
cd ~/ALFI
git switch feature/alfi-1.6-conversational-intelligence
git pull --ff-only
python3 -m py_compile tools/stage4_continuity_diagnostic.py tests/test_stage4_continuity_diagnostic.py
python3 -m unittest discover -s tests -v
python3 tools/stage4_continuity_diagnostic.py --output stage4_continuity_report.json
```

**Human review rubric:** Score whether follow-ups retain the correct preceding subject, whether independent topic shifts omit unrelated content, whether a follow-up after a shift refers to the **new** subject, and whether unknown-fee arithmetic avoids false exact totals. A single report contains the full answers and structural prompt diagnostics for comparison; do not infer correctness from execution success alone. Ollama defaults are unseeded; these synthetic conversations are not a production-equivalent saved-memory test.

**Status:** remote implementation committed, local execution and live results not yet verified. Do not enable selective mode by default. Stage 4 NOT PASSED; Increment 9 ON HOLD; stable `main` unchanged.

## Automated 24-turn continuity assessment — operator report 2026-10-20

Source: user-uploaded `stage4_continuity_report.json` created `2026-10-20T03:36:40.187647+00:00`; `gemma3:4b`, Ollama defaults (unseeded), synthetic in-memory histories only, no saved-memory matches, all 24 final answers from initial generation without retries. Four scenarios each executed normal and selective (eight three-turn sequences).

| Scenario | Normal | Selective | Assessment |
|---|---|---|---|
| F1 photosynthesis → why important → another example | Pass | Pass | Correct subject continuity |
| F2 firewall → how work → tell more | Pass | Pass | Correct subject continuity, some repetitiveness |
| T1 bicycle helmet → theater $27 + unknown fee → explain that | Fail | Pass | Normal explanation begins with invented $36 total then correctly says $27+x unknown; selective stays with theater and unknown fee |
| T2 water cycle → museum $24 + unknown fee → why important | Fail | Fail | Both versions discuss the older water-cycle subject rather than most recent museum question; selective museum answer also incorrectly calls $24 the total including unknown service charge |

**Source-path hypothesis (not yet instrumentally proven):** `contextual_subject` in `conversational_intelligence.py` skips recent substantive user questions that do not begin with `explain`, `describe`, `what is`, `what are`, or `tell me about`. It can therefore select the earlier `Explain the water cycle.` over the newer museum question when the user says `Why is it important?`. The observed T2 result is consistent with that behavior; inspect `response_policy`, `resolve_followup`, and `contextual_subject` jointly before changing code. A second independent issue is the false exact-total claim in selective T2 despite history exclusion.

**Ruling:** Straightforward follow-up continuity 2/2 selective; topic-switch continuity 1/2 selective. This is a **partial pass**, not Stage 4 promotion. No selector default change authorized. Next candidate work: fix referent precedence with focused offline tests, then rerun automated continuity and unknown-fee diagnostics. Increment 9 ON HOLD; stable `main` unchanged.


## Second automated continuity report — 2026-10-20 04:14 UTC

Operator submitted `stage4_continuity_report_run2.json` (24 turns, eight three-turn sequences, `gemma3:4b`, Ollama unseeded defaults, synthetic in-memory history, zero saved-memory matches, all initial generations without retries). This repeats the **same** prompts as run 1, so it measures run-to-run consistency, not novel transfer or learning.

- **F1 photosynthesis:** Both conditions correctly stay on topic. The final "Give me another example" response in each condition mostly restates the mechanism without giving a clear new example: **partial credit on final turn**.
- **F2 firewall:** Both conditions maintain subject across turns; the final "Tell me more" largely repeats existing explanation rather than deepening it: consider partial credit for depth, despite correct referent.
- **T1 helmet → theater fee → "Explain that":** Both conditions correctly identify $27 subtotal and unknown booking fee; final explanation correctly stays with theater. Normal condition's run-1 contradictory "$36" claim does not recur.
- **T2 water cycle → museum fee → "Why is it important?":** Both conditions correctly compute $24 + unknown charge on second turn, but **both revert to water cycle on final turn**, reproducing run 1's wrong-referent behavior. Because "it" is semantically ambiguous after a calculation, test an explicitly anchored follow-up as well before concluding the routing code alone is at fault.

**Scenario-level outcome** (correct subject continuity, with answer-completeness caveats): F1 normal/selective pass/pass; F2 pass/pass; T1 pass/pass; T2 fail/fail. Across both reports, normal scenario passes 5/8, selective passes 6/8. These small repeated prompts are not statistically independent and do not establish a reliability rate. Stage 4 remains under assessment; investigate referent precedence with code inspection and unseen contrastive prompts. No authorization to change default selector or open Increment 9.
