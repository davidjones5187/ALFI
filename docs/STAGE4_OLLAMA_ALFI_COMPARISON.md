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
