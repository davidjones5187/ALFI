# Stage 4 — Controlled Direct Ollama vs A.L.F.I. Diagnostic

Date: 2026-10-19
Status: **Prepared; operator execution pending**
Branch: `feature/alfi-1.6-conversational-intelligence`

## Purpose

Investigate repeated Stage 4 failure on **known subtotal + unspecified component**. Compare Gemma 3 4B through direct Ollama and through A.L.F.I., without modifying code, memory, or existing history. This is a diagnostic comparison, **not** a clean causal experiment: direct Ollama lacks A.L.F.I.'s system prompt, retrieval, and history context, and model generation may be nondeterministic.

## Controlled prompt (hold out until testing)

`A museum charges $7 per adult ticket. There is also a booking fee, but its amount has not been provided. What is the exact total for two adult tickets including the booking fee?`

Expected evaluation: $14 is the known ticket subtotal; exact total cannot be determined because the booking fee is unknown. A symbolic answer `$14 + booking fee` is valid. Claiming exact total $14 is incorrect. No answer key or teaching text should be supplied to either system before testing.

## Execution procedure

1. Ensure development branch; `git pull --ff-only`. Note `git rev-parse --short HEAD`, `ollama list`, and relevant Ollama version. Do not clear history, use `/teach`, or modify memories.
2. Run **direct Ollama first** in a fresh invocation:
   `ollama run gemma3:4b`
   Enter the held-out prompt exactly once, capture full output, and exit with `/bye` (or Ctrl+D if necessary). This CLI route is intended as a minimal fresh interactive model conversation; it does not guarantee identical decoding settings to A.L.F.I.
3. Run A.L.F.I. in a **new process**:
   `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b python3 first_ai.py`
   Enter the **identical** held-out prompt exactly once, capture initial response, retry flags, and final response, and exit `/quit`.
4. Send both complete transcripts including command banners and diagnostic flags. No corrections or intervening coaching.

## Scoring and interpretation

Score each output 2 (correct uncertainty and subtotal), 1 (partial/ambiguous), 0 (asserts exact subtotal despite unspecified fee). Report separately direct and A.L.F.I. results and whether A.L.F.I. used initial generation or retry. A single matched or mismatched pair is **not proof** of model vs application root cause.

- **Both fail:** model-level tendency is plausible; A.L.F.I. context may still contribute.
- **Direct passes, A.L.F.I. fails:** application context/routing becomes a stronger hypothesis; inspect prompt construction and relevant retrieval before modifying anything.
- **Both pass:** error may be intermittent or prompt-dependent; repeat with preregistered novel variants if warranted.
- **Direct fails, A.L.F.I. passes:** application context may help, or variability may explain difference.

For a stronger comparison later, use multiple new held-out variants, repeated fresh sessions, same Ollama model digest, and where possible matched generation options and equivalent message histories. Never imply identical conditions from model name alone.

## Governance

Stage 3 provisionally approved; Stage 4 under assessment; Increment 8 closed; Increment 9 on hold; stable `main` untouched. **No code changes or persistent-memory edits authorized by this plan.**

## C1 results and read-only prompt-path inspection — 2026-10-19

**Operator transcript:** Direct `ollama run gemma3:4b` returned ticket subtotal $14 and exact-total expression `$14 + b`, explaining that the unknown booking fee prevents a numeric exact total: **2/2**. A.L.F.I. via `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b python3 first_ai.py` said the exact total *including* the unspecified fee was $14 while acknowledging the fee remained undetermined: **0/2**. Debug trace confirms `initial_generation`, `format_violation: none`, `corrective_retry: not_needed`. The joined command `ollama listollama run gemma3:4b` failed before the valid direct invocation and did not affect either answer.

**Read-only source inspection:** `first_ai.py` `generate()` builds a system prompt, appends up to three relevant structured memories as another system message, injects up to five saved user/assistant history pairs, appends `response_policy(...)` as a further system message, and sends the resolved user question to `http://127.0.0.1:11434/api/chat` with `stream: false`. It does not explicitly set `options`/temperature in the observed request construction. The system prompt says to be accurate and acknowledge uncertainty. `conversational_intelligence.py` `response_policy()` says answer accurately, distinguish established/hypothetical results, and prefer a short paragraph; `precision_guidance()` supplies generic technical-terminology guidance. `contextual_subject()` applies only to a narrowly matched importance question, not the museum prompt. No specific instruction to set unspecified quantities to zero was found in these reviewed static code paths.

**Conclusion:** The contrast supports a prompt/context/settings investigation, **not** a proven application defect. Exact model digest, decoding options, injected local memory/history, and final request payload were not captured. The direct CLI answer was substantially longer, another sign the environments differ. The current debug trace logs the selected model and answer, not the complete outgoing messages.

**Next diagnostic recommendation:** Without changing code or deleting history, capture a **redacted** list of the final Ollama message roles and sources and whether structured-memory matches/history were included; do not print private memory values. Then run several preregistered novel variants with matched generation options if feasible. Do not implement a rule-specific fix or open Increment 9 based on one paired observation.

**Governance:** Stage 4 under assessment, not promoted; Stage 3 provisionally approved; Increment 8 closed; Increment 9 on hold; stable `main` unchanged. No code or memory changes made in this review.

## Authorized diagnostic implementation and follow-up comparison — 2026-10-19

Operator approved a narrow debug-only prompt-structure instrument and further comparisons. Added `first_ai.py` diagnostics **only when `ALFI_DEBUG=1`**: `prompt_roles`, `prompt_message_count`, `prompt_saved_memory_matches`, `prompt_history_pairs`, `prompt_system_messages`, `prompt_user_question` (original/resolved), and `prompt_generation_options` (Ollama defaults). These new fields contain counts/roles/status only, not memory or conversation text. Existing `initial_response` debug output **still displays model-generated answer text**, which may echo user information: do not treat the entire debug log as redacted. No prompts, memory, or history are written by the diagnostic itself. Added regression test to check expected role structure and absence of example private prompt/history text in these debug lines. **Tests have not been executed on the operator's Mac; verification is pending.** No inference-engine logic or prompt content changed.

### Local verification (run before live comparisons)

```bash
cd ~/ALFI
git switch feature/alfi-1.6-conversational-intelligence
git pull --ff-only
python3 -m unittest discover -s tests -v
```

Stop and report any test failures. Keep private history and memory files intact.

### Held-out comparison C2

Prompt: `A community center charges $9 per class. A registration surcharge applies, but its amount is unknown. What is the exact amount owed for four classes including the surcharge?`

Expected: known subtotal $36; exact total $36 + unknown surcharge, not determinable.

### Held-out comparison C3

Prompt: `A garden store sells seedlings for $6 each. Delivery is an additional charge whose amount has not been stated. What is the exact total for five seedlings including delivery?`

Expected: known subtotal $30; exact total $30 + unknown delivery, not determinable.

For **each** prompt, start fresh `ollama run gemma3:4b`, ask exactly once, capture answer, exit `/bye`. Then start a fresh `ALFI_DEBUG=1 ALFI_OLLAMA_MODEL=gemma3:4b python3 first_ai.py`, ask the identical prompt exactly once, capture answer and redacted prompt-structure fields, exit `/quit`. Do not coach or correct. Running C2 then C3 will add previous test questions to A.L.F.I.'s existing history; report this limitation. Do not use `/clearhistory`, `/teach`, `/remember`, or change generation settings.

Score each response 0/1/2, separately by environment, and review debug fields. These two paired observations remain exploratory because sampling settings and historical context are not fully matched. Do not promote Stage 4 or implement a targeted reasoning fix based solely on these results.

**Governance:** Increment 8 closed; Stage 3 provisionally approved; Stage 4 under assessment; Increment 9 on hold; stable `main` untouched.

## C2/C3 operator results and ruling — 2026-10-19

Operator confirmed local syntax compilation and **124/124 automated tests passed** after regression syntax fix at `86baba7`. Automated success does not establish live model reasoning.

| Case | Direct Ollama | A.L.F.I. | Key observation |
|---|---|---|---|
| C1 museum | 2/2 | 0/2 | Direct `$14+b`; A.L.F.I. claims exact $14 |
| C2 community center | 2/2 | 0/2 | Direct `$36+s`; A.L.F.I. claims exact $36 |
| C3 garden store | 1/2 | 0/2 | Direct explains `$30+d` and unknown charge, **but final boxed answer is $30**; A.L.F.I. claims exact $30 |
| **Total** | **5/6** | **0/6** | All A.L.F.I. answers initial generation, no retries |

**C2 debug:** `gemma3:4b`; roles `system,user,assistant,user,assistant,user,assistant,user,assistant,user,assistant,system,user`; 13 messages; 5 history pairs; 0 structured-memory matches; 2 system messages; original user question; Ollama defaults; no format violation or retry. A.L.F.I. says exact amount $36 while surcharge remains unspecified.

**C3 debug:** `gemma3:4b`; roles `system,system,user,assistant,user,assistant,user,assistant,user,assistant,user,assistant,system,user`; 14 messages; 5 history pairs; 1 structured-memory match; 3 system messages; original user question; Ollama defaults; no format violation or retry. A.L.F.I. says exact $30 while delivery remains undefined.

**Interpretation:** Structured-memory retrieval is not necessary for the failure (C2 has zero matches). Historical context is present in both runs, but its contents and causal effect are unverified. Direct Gemma's C3 reasoning/final-answer inconsistency shows the base model can also fail this pattern. Direct CLI versus A.L.F.I. still differs in prompts, history, and potentially generation parameters; a paired result is not a causal isolation. C2/C3 are not delayed retention tests and do not establish model-weight learning.

**Recommended next diagnostic, pending operator authorization:** Non-destructive, reversible *ephemeral* context-isolation experiment with saved history left intact: compare same-model requests with no history versus the usual last five turns, controlling system instructions and decoding as closely as practical. Do not use `/clearhistory` or edit persistent files. Capture only aggregate prompt-source diagnostics; avoid logging private history. A second step can isolate the policy system message and explicit generation options if necessary.

**Governance:** Stage 4 **NOT PASSED**; Stage 3 provisionally approved; Increment 8 closed; Increment 9 on hold. No reasoning code changes or memory edits authorized. Stable `main` untouched.

## H1 history-isolation operator results — 2026-10-19

Operator pulled development branch through `2206ad0`. Python syntax compilation succeeded and **125/125 automated tests passed** (0.028 seconds), including `test_diagnostic_history_exclusion_is_ephemeral`.

**H1 prompt:** A workshop charges $8 for each seat. A separate materials fee applies, but its amount is unspecified. What is the exact total for three seats including materials? Expected: known subtotal $24; exact numerical total unknown ($24 + unspecified materials fee).

- **Normal history: 0/2.** `prompt_history_mode: normal`, 13 messages, 5 history pairs, 0 saved-memory matches, 2 system messages, original user question, Ollama defaults. Initial and final response incorrectly claimed the exact total including unspecified materials was $24. No format violation or corrective retry.
- **History excluded: 2/2.** `prompt_history_mode: excluded`, 3 messages, 0 history pairs, 0 saved-memory matches, 2 system messages, original user question, Ollama defaults. Initial and final response correctly distinguished the $24 seat subtotal from the unknown total including materials. No format violation or corrective retry.

**Assessment:** This single within-prompt contrast strengthens the historical-context-interference hypothesis but does not prove causation: generation variability remains possible, and the normal first run records H1 before the second run (though history is excluded from its model prompt). Earlier direct Ollama C3 showed a base-model final-answer error. Do not promote Stage 4 or implement a reasoning fix based on one isolation pair. Recommend preregistered additional held-out A/B trials with counterbalanced order and repeated runs; maintain original history and avoid memory deletion. Operator authorization needed for further implementation changes.

**Governance:** Stage 4 NOT PASSED; Increment 9 ON HOLD; stable `main` untouched.
