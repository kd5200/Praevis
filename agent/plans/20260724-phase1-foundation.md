# Plan: Phase 1 — Repository Foundation

**Date:** 2026-07-24  
**Agent run goal:** Establish monorepo structure, docs, service skeletons, Compose, and health checks.

## Scope

Phase 1 only. No scan pipeline, SSRF fetcher, detectors, scoring, or dashboard features beyond a Next.js placeholder page.

## Steps

1. Create monorepo directories and root configs (`pyproject.toml`, `package.json`, Docker Compose, Makefile, `.env.example`).
2. Write product/architecture/agent documentation with meaningful MVP content.
3. Scaffold FastAPI API with `GET /health` and `GET /ready`, structured logging stubs, and pytest coverage.
4. Scaffold Celery-oriented worker package (entrypoints only; no scan jobs yet).
5. Scaffold Next.js + TypeScript + Tailwind web app with a minimal placeholder page.
6. Stub packages: `contracts`, `sdk-python`, `sdk-typescript`, `security-rules`.
7. Prepare `infrastructure/docker`, empty Terraform layout, and helper scripts.
8. Add Cursor agent rules for durable workflow.
9. Install deps, start Compose (Postgres + Redis), run lint/typecheck/tests, verify health endpoints.
10. Record results in `agent/runs/`, update `STATUS.md` and `HANDOFF.md`.

## Decisions to record

- Codename `Praevis` kept replaceable via config/branding constants.
- Task queue: Celery + Redis (standard for Python MVP; pipeline stays framework-independent).
- Python packages managed from root `pyproject.toml` with `apps/api` and `apps/worker` as installable packages.
- Local host Python may be 3.11; containers and declared target use 3.12.

## Acceptance criteria

- [x] Documented structure exists as specified.
- [x] `docker compose up` starts PostgreSQL and Redis.
- [x] API health tests pass.
- [x] Web app builds or starts without fatal config errors.
- [x] Lint/typecheck commands exist and run (pass or documented gaps).
- [x] Agent status/handoff/run summary updated.

## Out of scope

Scan models, Alembic migrations beyond placeholder, fetch/sanitize/detect/score, dashboard scan UI, worker job processing.
