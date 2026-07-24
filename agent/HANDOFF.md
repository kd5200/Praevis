# Handoff

**Updated:** 2026-07-24 (Phase 1 complete)

## Recommended next task

**Phase 2 start:** Define SQLAlchemy models (`Scan`, `Finding`, `RetrievedContent`), Alembic migration scaffolding, and `POST /v1/scans` that creates a `queued` scan record (pipeline stages can still be stubs). Follow with URL normalization unit tests.

## Verify environment

```bash
cp .env.example .env   # if needed; default Postgres host port is 15432
make setup
make up
make test
curl -s http://localhost:8000/health
curl -s http://localhost:8000/ready
```

## Notes for the next agent

- Read root `AGENTS.md`, `agent/STATUS.md`, `docs/DECISIONS.md`, `docs/TASKS.md` before coding.
- Do not fetch uncontrolled public websites in tests; introduce fixture server/mocks with SSRF defenses.
- Keep scan pipeline stages framework-independent (callable from API sync path and Celery later).
- Codename Praevis is temporary; keep branding easy to replace.
- Raw content must not be dumped unrestricted into Postgres — design a storage interface early.
