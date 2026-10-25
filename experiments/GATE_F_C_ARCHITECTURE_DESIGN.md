# Gate F-C — Two-Stage Routing Architecture (design only)

Status: DESIGN PROPOSED; human acceptance pending. No implementation authorized.
Branch: `experiment/car-v2-isolated-pilot`.
Frozen comparators: Gate F-H2R and Gate F-B. Preserve original F-BH result and all earlier failures.

## Evidence motivating the design

Gate F-BH ran 261/261 unit tests and 24 post-freeze, nonblinded synthetic cases, using a model stub (not Ollama). Frozen F-H2R: approved 10/10, abstain 6/10, general 4/4; four attack-bearing requests returned *approved* values rather than abstaining. Strict F-B: approved 5/10, abstain 10/10, general 0/4. The strict router refused five benign retrieval variants and four general requests. No unapproved synthetic values were disclosed in that holdout. These are observed fixture results, not proof of real-world robustness.

## Proposed trust boundaries

1. **Ingress and normalization.** Accept a bounded Unicode string; retain the original text for audit; normalize only for matching. Reject oversized, malformed, or mixed-format inputs. User content is untrusted, including quoted text, apparent role instructions, and assertions of approval.
2. **Stage 1: protected-memory relevance triage.** Output one of `memory_candidate`, `general_candidate`, or `uncertain`, with a reason code. Never let user-provided claims of approval confer authority. A general classification must require positive evidence of a self-contained, non-memory request; absence of a manifest alias alone is insufficient. Any overlap with known entity aliases, reviewed/approved language, references to prior answers, or ambiguous mixed requests must stay inside the protected boundary.
3. **Stage 2: structured protected intent.** Only `memory_candidate` requests enter a constrained parser yielding `entity_id`, `attribute_id`, `intent=read_current_approved`, and `untrusted_extra_text` (or a rejection). The parser must reject competing entities/attributes, historical claims, roleplay, instructions to substitute answers, and unsupported transformations. Harmless wording variants should be specified and measured rather than silently accepted.
4. **Authority gate.** An exact key lookup returns a value only when exactly one approved, correctly typed record exists and its payload key matches. Unverified, missing, superseded, malformed, or conflicting records abstain. Neither classifier nor parser can approve records.
5. **General-conversation gate.** Only positively classified general requests may reach a model; the model receives no protected memory, manifest, or private record context. Uncertain requests abstain (or request clarification in a later UI design), never fall through to unrestricted model generation.
6. **Audit.** Emit reason codes, routing stages, record status category (not secret content), model-call counts, and synthetic expected outcomes. No automatic human approval.

## Decision table

| Stage 1 | Stage 2 | Action |
|---|---|---|
| general_candidate | not run | general model without protected context |
| uncertain | not run | abstain |
| memory_candidate | unique approved-read intent | authority gate |
| memory_candidate | ambiguous, unsupported, or adversarial | abstain |
| memory_candidate | valid intent but missing/unapproved record | abstain |
| memory_candidate | valid intent and unique approved record | return approved value without model call |

## Key failure modes and design constraints

- **Memory disguised as general:** aliases absent, obfuscated, indirect, quoted, or embedded in unrelated questions. Default to `uncertain` if protected relevance cannot be excluded.
- **False general pass-through:** classify on the whole request, not a convenient substring. Mixed memory/general requests are not general.
- **False refusal:** benign punctuation, politeness, framing, conflicting third-party notes, and paraphrases should be separate scored strata.
- **Entity collision:** longest alias alone is not proof of unique identity; test nested aliases and overlapping aliases with explicit ambiguity handling.
- **Manifest injection:** treat aliases and record payloads as data, validate shapes, lengths, collisions, and control characters.
- **Authority ambiguity:** approved status alone is insufficient; require unique current approved record and matching payload.
- **Evaluation blind spots:** a correct returned approved value is still a failure when the expected policy is to abstain from attack-bearing text; count unsafe routing independently of leaked unapproved values.
- **General response quality:** a stub establishes pass-through only; real model quality requires a separate explicitly authorized study.

## Proposed Gate F-C1 acceptance protocol (requires separate authorization)

A. Freeze architecture, code commit IDs, policy labels, and scoring rubric **before** generating an independently authored challenge. Holdout preparer must not adapt cases to observed candidate results.
B. Synthetic fixture with novel entities and attributes, approved and unapproved records, nested and overlapping aliases, invalid payloads, and conflicting approved records.
C. Balanced preregistered categories: straightforward approved reads; benign paraphrases; benign conflicting notes; punctuation/context; unknown and historical requests; unapproved/malformed records; direct/indirect adversarial prompts; mixed general/memory requests; genuine general conversation.
D. Measure per-category: correct approved answers, unsafe policy acceptance, unapproved value disclosure, false abstention, incorrect entity/attribute, general pass-through, and unsafe model calls. Report denominators and exact cases; do not collapse into one accuracy number.
E. Require **zero** unapproved disclosures, zero protected-context model calls, and zero adversarial/mixed-request general pass-through in the challenge. Usability targets must be explicitly agreed before test execution, not set retrospectively. A clean holdout is necessary but insufficient for production authorization.
F. Compare with both frozen F-H2R and F-B; preserve raw failures and `human_review:null` until user supplies approval.
G. Run unit tests and static checks separately from behavioral evaluation. Record dataset and code hashes. No production data, imports, or writes.

## Current ruling

Gate F-BH: completed, behavioral FAIL, preserved.
Gate F-C: architecture design only; **no Gate F-C1 implementation, holdout, final Gate F acceptance, or production integration authorized**.
