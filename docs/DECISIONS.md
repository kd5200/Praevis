# Architecture decisions

Format: short ADRs. Newest first.

---

## ADR-0005 — Default host Postgres port 15432

**Date:** 2026-07-24  
**Status:** Accepted

**Decision:** Map Compose Postgres to host port `15432` by default (`POSTGRES_PORT`), while the container still listens on `5432`.

**Rationale:** Local host already had listeners on common Postgres ports (`5432`/`5433`), blocking Compose bind.

**Consequences:** `.env.example` and `DATABASE_URL` use `localhost:15432`. Override via `.env` when needed.

---

## ADR-0004 — Celery + Redis for task queue

**Date:** 2026-07-24  
**Status:** Accepted (Phase 1)

**Decision:** Use Celery with Redis as broker for `apps/worker`. Keep the scan pipeline as plain Python stages so it can run in-process or under other runners later.

**Rationale:** Widely supported, fits Compose MVP, Redis already required.

**Alternatives:** Dramatiq, RQ, custom asyncio queue.

---

## ADR-0003 — Root Python project with installable apps

**Date:** 2026-07-24  
**Status:** Accepted

**Decision:** Manage Python tooling from root `pyproject.toml`; install `apps/api` and `apps/worker` as packages (`praevis-api`, `praevis-worker`).

**Rationale:** Single lint/test entrypoint for agents; clear import boundaries.

---

## ADR-0002 — Python 3.12 target runtime

**Date:** 2026-07-24  
**Status:** Accepted

**Decision:** Official runtime is Python 3.12 (Docker images). Local hosts may temporarily use 3.11 for tooling if 3.12 is unavailable; CI/Compose should use 3.12.

**Rationale:** Matches stack mandate; containers provide consistency.

---

## ADR-0001 — Working codename Praevis

**Date:** 2026-07-24  
**Status:** Accepted

**Decision:** Use Praevis as temporary codename. Prefer `APP_NAME` / branding constants for user-facing strings where practical.

**Rationale:** Easy rebrand without deep renames of package paths in MVP (package names may still say `praevis` until rename).
