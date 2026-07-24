# Tasks

Track acceptance-oriented work. Agents update status honestly.

## Phase 1 — Repository foundation

| ID | Task | Status |
|----|------|--------|
| P1-01 | Monorepo structure | done |
| P1-02 | Root configs (pyproject, package.json, env, Makefile) | done |
| P1-03 | Docker Compose (Postgres + Redis) | done |
| P1-04 | Documentation (PRODUCT, ARCHITECTURE, SECURITY_MODEL, API_SPEC, DECISIONS, ROADMAP, TASKS, RUNBOOK) | done |
| P1-05 | AGENTS.md + agent workflow files | done |
| P1-06 | FastAPI skeleton + health/ready | done |
| P1-07 | Next.js skeleton | done |
| P1-08 | Worker skeleton | done |
| P1-09 | Lint / typecheck / test configuration | done |
| P1-10 | Health endpoint tests pass; services start | done |
| P1-11 | Agent run summary + STATUS/HANDOFF update | done |

## Phase 2 — Backend vertical slice

| ID | Task | Status |
|----|------|--------|
| P2-01 | DB models + Alembic migrations | done |
| P2-02 | URL submission API | done |
| P2-03 | URL normalization | done |
| P2-04 | Destination validation / SSRF protections | done |
| P2-05 | Safe HTTP fetcher (mocked transports in tests) | done |
| P2-06 | HTML extraction + sanitization | done |
| P2-07 | Prompt-injection rules package | done |
| P2-08 | Deterministic scoring engine | done |
| P2-09 | Persist scan results | done |
| P2-10 | Return completed scan via API | done |

## Phase 3 — Dashboard

| ID | Task | Status |
|----|------|--------|
| P3-01 | Scan submission form | done |
| P3-02 | Scan status / result views | done |
| P3-03 | Findings, scores, decision, content, provenance | done |
| P3-04 | Wire dashboard to API | done |

## Phase 4 — Worker execution

| ID | Task | Status |
|----|------|--------|
| P4-01 | Redis-backed job processing | pending |
| P4-02 | Move slow ops to worker | pending |
| P4-03 | Polling scan status | pending |
| P4-04 | Preserve sync mode for local testing | pending |

## Phase 5 — Hardening

| ID | Task | Status |
|----|------|--------|
| P5-01 | Expand security fixtures | pending |
| P5-02 | Regression tests | pending |
| P5-03 | Request limits | pending |
| P5-04 | Structured error codes | pending |
| P5-05 | Logging and timing | pending |
| P5-06 | Docs and runbook update | pending |
