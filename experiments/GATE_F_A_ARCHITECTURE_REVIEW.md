# Gate F-A — Routing Architecture Assessment (design review)

Status: **design review, pending local verification and human acceptance**. This is not a production integration proposal.

## Frozen baseline
- Human-approved Gate F-H2R: `experiments/car_v2_gate_f_h2r.py`.
- Original F-H and F-H2 failed JSON evidence remains immutable.
- No changes to `main`, production memory, or the approved experimental router.

## Architecture map
1. **Manifest matching**: token-bounded entity and attribute aliases select a topic key. Overlapping aliases use longest-match disambiguation.
2. **Query policy**: regular expressions screen adversarial, historical, and unsupported language.
3. **Authority boundary**: lookup requires exactly one retrieved approved record with a JSON topic key matching the route and a nonempty string value.
4. **Execution**: authorized lookup returns the verified value without an LLM call; abstention also avoids an LLM call; unrelated questions use the model.
5. **Evaluation**: paired baseline/CAR comparisons, repeated AB/BA, deterministic Ollama settings; stronger holdout scorer checks abstention content and model-call counts.

## Findings from the recorded evidence
- F-H 22/28 routing; H-R 28/28 on same holdout.
- F-H2 28/32 routing; H2-R 32/32 on same holdout.
- The direct unapproved-record lookups in F-H2R abstained without model calls.
- Two successive new challenge sets exposed previously unseen adversarial phrasing, despite prior 100% remediation retests.
- Therefore 100% on a repaired holdout is **not** proof of open-ended instruction-intent recognition.

## Architectural risks
| Risk | Mechanism | Required evidence |
| --- | --- | --- |
| Lexical brittleness | Regexes miss new paraphrases, negation, or cross-sentence directives | Fresh, blinded adversarial and benign near-neighbor pairs |
| False refusal | Benign quotation or hypothetical discussion matches an attack pattern | Separate false-positive rate and benign-control suite |
| Entity ambiguity | Longest alias is not always the intended referent | Alias-collision, quoted-name, and multi-entity tests |
| Attribute ambiguity | Attribute aliases match incidental mentions in the question | Multi-attribute and negated-attribute tests |
| Manifest integrity | Incomplete validation of aliases, collisions, or metadata | Malformed and adversarial manifest tests |
| Authority provenance | `status == approved` is necessary but may not prove reviewer identity, record freshness, or revocation | Independent audit of record lifecycle and authorization |
| Out-of-scope leakage | Unrecognized protected entity may be passed to model | Unknown alias and entity-typo safety tests |
| Scorer blind spots | Some original scorers only check routing and approved-answer equality | Unified scorer verifying abstentions, model calls, and outside-scope behavior |

## Decision options
**A. Continue regex patching**: low implementation cost; weak evidence of generalization. Not recommended as primary strategy.

**B. Restrictive query grammar with explicit intent schema**: parse known safe question forms; abstain on unparsed or contradictory inputs. Stronger fail-closed guarantees but lower recall. **Recommended next experiment** for a small, auditable local assistant.

**C. Separate intent classifier**: can improve recall but requires independently labeled data, calibration, adversarial tests, and an abstention threshold; never allow classifier output to confer record approval. Consider only after B is benchmarked.

## Gate F-A acceptance criteria
1. Explicitly separate **routing safety** from **memory authority**; neither substitutes for the other.
2. Freeze F-H2R and compare candidate B against it on **fresh**, pre-registered benign/adversarial pairs.
3. Report true-positive, false-positive, false-negative, false-abstention, authority violations, and model-call safety separately.
4. Ensure approval state is enforced in the data-access layer, not inferred from user text or classifier output.
5. Preserve all failed cases and do not revise test expectations after execution.
6. Human reviewer must explicitly approve the architecture decision before implementation of a replacement router or any production integration.

## Recommendation
Accept this assessment as a **design artifact only** after review. Next request authorization for a Gate F-B restrictive-grammar prototype and independent evaluation, not an open-ended regex expansion. No final Gate F acceptance is implied.
