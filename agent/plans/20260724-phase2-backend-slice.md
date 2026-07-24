# Plan: Phase 2 — Backend vertical slice

**Date:** 2026-07-24  
**Goal:** End-to-end URL scan path: submit → validate/fetch (mocked in tests) → sanitize → detect → score → persist → API response.

## Scope

Complete P2-01 … P2-10 with sync `wait_for_completion` in the API. Async worker jobs remain Phase 4.

## Steps

1. SQLAlchemy models + Alembic + DB session wiring; raw artifact storage interface (local/memory).
2. Pipeline stage modules with typed I/O (normalize → validate → resolve → fetch → extract → detect → sanitize → score).
3. Security rules catalog in `packages/security-rules` + loader.
4. Deterministic scoring + decision engine with unit tests.
5. Scan API: POST/GET list/detail/findings/content; persist results.
6. Fixtures (safe + malicious pages) and MockTransport fetch tests; SSRF/redirect regression tests.
7. Wire Makefile `migrate`; run lint/typecheck/tests; update agent docs.

## Decisions to record

- In-process sync pipeline for `wait_for_completion=true` in Phase 2.
- Raw artifacts behind a storage protocol (not unrestricted HTML in Postgres).
- BeautifulSoup for HTML parse/sanitize (deterministic, no JS execution).

## Acceptance criteria

- [x] Migrations create Scan/Finding/RetrievedContent tables.
- [x] POST `/v1/scans` with `wait_for_completion` returns decision, scores, findings, content, provenance.
- [x] SSRF/private IP/metadata destinations blocked with tests.
- [x] Prompt-injection fixtures produce findings.
- [x] Scoring is deterministic and explainable in unit tests.
- [x] No tests hit uncontrolled public websites.
- [x] Relevant lint/tests pass; STATUS/HANDOFF/run updated.

## Out of scope

Dashboard UI (Phase 3), Celery scan jobs (Phase 4), production hardening extras (Phase 5).
