# Architecture decisions

Format: short ADRs. Newest first.

---

## ADR-0009 — Dashboard uses server actions + server fetch

**Date:** 2026-07-24  
**Status:** Accepted

**Decision:** The Next.js dashboard submits scans via a server action and loads list/detail via server-side fetch to the API. CORS is still enabled on the API for browser/SDK clients.

**Rationale:** Avoids relying on browser CORS for core flows; keeps credentials and base URL handling on the server.

---

## ADR-0008 — BeautifulSoup + lxml for HTML sanitize/extract

**Date:** 2026-07-24  
**Status:** Accepted

**Decision:** Use BeautifulSoup with the `lxml` parser for HTML extraction and sanitization. Do not execute JavaScript.

**Rationale:** Deterministic, testable, sufficient for MVP sanitization.

---

## ADR-0007 — Raw artifacts behind storage interface

**Date:** 2026-07-24  
**Status:** Accepted

**Decision:** Persist only sanitized text/HTML metadata in Postgres. Store raw bodies via `RawArtifactStore` (`memory` for tests, `local` filesystem for MVP). References are stored on `RetrievedContent.raw_content_reference`.

**Rationale:** Avoid unrestricted raw HTML in the primary DB; leave room for encrypted object storage + retention.

---

## ADR-0006 — In-process sync scan pipeline (Phase 2)

**Date:** 2026-07-24  
**Status:** Accepted

**Decision:** When `wait_for_completion=true`, run the framework-independent pipeline inside the API process. `wait_for_completion=false` creates a `queued` scan (worker execution in Phase 4).

**Rationale:** Delivers a complete vertical slice without blocking on Celery job wiring.

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
