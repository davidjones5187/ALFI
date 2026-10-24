# CAR v2 isolated pilot — experimental branch

This is a deliberately restricted **adapter scaffold** informed by the uploaded
CAR v2 research prototype, not a replacement for it and not a live integration.
It uses a dedicated SQLite file, explicit Context–Action–Result proposals, scoped
readback, restart persistence, and a hard no-promotion boundary.

## Trust boundary

The adapter **cannot confirm** lessons. `confirm()` raises `PermissionError`.
Unverified proposals are never returned by `retrieved_lessons()`. A later
authenticated confirmation bridge must be separately designed and reviewed.
An evidence reference is a string, not independently verified evidence.

## Run on Mac

```bash
git fetch origin
git switch experiment/car-v2-isolated-pilot
git pull --ff-only
python3 -m unittest discover -s tests -v
```

Expected test discovery count is 175 if the 167-test baseline remains unchanged.
The pilot tests require no Ollama and never write legacy memory files.

## Not implemented

- No integration with `first_ai.py` or default `MemoryStore`
- No migration, automatic extraction, or model-directed confirmation
- No confirmed lesson retrieval, correction promotion, or supersession
- No live Gemma comparison or Stage 4 learning validation
- No secure deletion, concurrency benchmark, or independent semantic audit

## Next gate

After all regression tests pass, compare the original CAR v2 package against
this scaffold and specify an authenticated confirmation API before adding any
runtime retrieval. Preserve stable v1.5.1 and the frozen Stage 4 evidence.
