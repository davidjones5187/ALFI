# Stage 4 — Offline iteration 2: reviewer targets and unknowns

Authorized: offline-only revision, no runtime wiring. A separate v2 checker and fresh E2 challenge set were constructed and executed in an isolated Python environment. The original E1 checker and scores remain unchanged.

**E2 designed challenge set:** 16/16 expected four-class labels matched; 7/7 deliberately contradictory responses detected, 0 false contradiction alarms among 9 other cases. This is a small, authored diagnostic set; not representative reliability evidence or an independent external audit. It must not be used to claim readiness for runtime integration. Unlike E1, E2 was constructed for the revision and should be treated as a developer challenge set rather than a blind externally sealed benchmark.

Changes in candidate v2: longer number-word recognition, reviewer-specific verdict targeting, verdict synonyms, explicit unsupported unknown-fee amount checks, and conservative abstention on unrecognized claims. Remaining risks include negation scope, quoted multi-claim answers, other item categories, and unsupported explanations without numeric assertions.

**Decision:** Offline candidate only; do not replace or integrate the existing checker. Next: transfer candidate and E2 script to repo feature branch, run full suite and larger blinded challenge with independently prepared labels. Stage 4 under assessment, Increment 9 on hold, main untouched.
