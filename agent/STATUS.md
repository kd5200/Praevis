# Project status

**Last updated:** 2026-07-24  
**Active phase:** Phase 1 — Repository foundation (**complete**)  
**Codename:** Praevis (replaceable)

## Summary

Phase 1 foundation is in place: monorepo layout, documentation, FastAPI/Next.js/Celery skeletons, Docker Compose (Postgres + Redis), Makefile, lint/typecheck/test tooling, and passing health endpoint tests. Live `/health` and `/ready` probes succeeded against Compose infra.

## Completed

- Monorepo structure (`apps/`, `packages/`, `infrastructure/`, `docs/`, `agent/`, `tests/`).
- Root configs: `pyproject.toml`, `package.json`, `docker-compose.yml`, `Makefile`, `.env.example`, `.gitignore`.
- Product and agent docs with meaningful MVP content.
- FastAPI API with `GET /health`, `GET /ready`, structured logging helpers.
- Celery worker skeleton with `ping` task.
- Next.js + Tailwind placeholder dashboard (builds successfully).
- Package stubs: contracts, sdk-python, sdk-typescript, security-rules.
- Terraform placeholders and Dockerfiles for api/worker.
- Cursor rule: `.cursor/rules/praevis-agents.mdc`.
- Validation: pytest 4 passed; ruff/mypy/web typecheck/lint/build green; Compose healthy; live probes OK.

## In progress

- None for Phase 1.

## Not started

- Phase 2: Backend vertical slice (models, fetch, sanitize, detect, score, persist).
- Phase 3: Dashboard scan UI.
- Phase 4: Worker job processing.
- Phase 5: Hardening and regression expansion.

## Environment notes

- Host Python: 3.11.3 (target runtime remains 3.12 via Docker images; ADR-0002).
- Host Postgres port mapping defaults to **15432** (host `5432`/`5433` were occupied).
- Redis on host port **6379**.
- Node: v20.19.4; npm: 10.8.2.

## Blockers

None.
