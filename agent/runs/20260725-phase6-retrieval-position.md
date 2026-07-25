# Run summary — 2026-07-25 Phase 6 P6-01/P6-02

## Objective

Audit Praevis against the refined secure-retrieval product position; document preserve-first plan; implement one small integrity-hash increment.

## Tests before changes

```text
python3 -m pytest -q
→ 58 passed
```

## Changes

- Documented ADR-0012; updated PRODUCT, AGENTS, ARCHITECTURE, API_SPEC, TASKS, ROADMAP, STATUS, HANDOFF
- Added `pipeline/integrity.py` (`sha256_digest`)
- Pipeline computes `sanitized_content_hash` over sanitized text
- DB column + Alembic `0002_sanitized_hash`
- API: `integrity` object; provenance gains original/sanitized hashes and URL fields
- Minimal dashboard labels for both hashes
- Unit + integration tests

## Tests after changes

```text
python3 -m pytest -q
→ 60 passed
```

## Incomplete / next

- P6-03 transformation records
- P6-04 policy layer
- P6-05 nested scores
- P6-06 source spans
- P6-07 SSRF regression matrix
- P6-08 agent context fields

## Notes

Repository remains runnable. Run `make migrate` for Postgres hosts needing `0002_sanitized_hash`.
