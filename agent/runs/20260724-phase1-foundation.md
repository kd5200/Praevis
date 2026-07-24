# Run summary — Phase 1 foundation

**Timestamp:** 2026-07-24T16:15:00Z (approx)  
**Plan:** `agent/plans/20260724-phase1-foundation.md`  
**Outcome:** Phase 1 complete

## Goal

Bootstrap the Praevis monorepo: structure, docs, API/web/worker skeletons, Compose, Makefile, health checks, and validation tooling.

## Work performed

- Created full monorepo tree and root configuration.
- Wrote product, architecture, security, API, decisions, roadmap, tasks, and runbook docs.
- Wrote agent workflow files and Cursor always-on rule.
- Implemented FastAPI health/ready with dependency probes and structured logging helpers.
- Implemented Celery worker skeleton (`ping` task).
- Implemented Next.js + Tailwind placeholder page.
- Stubbed contracts/SDKs/security-rules packages and Terraform placeholders.
- Started Postgres + Redis via Docker Compose; verified live API probes.

## Files created (high level)

- Root: `AGENTS.md`, `README.md`, `Makefile`, `docker-compose.yml`, `.env.example`, `pyproject.toml`, `package.json`, `.gitignore`
- Docs: `docs/*.md`
- Agent: `agent/*`, plan under `agent/plans/`
- Apps: `apps/api`, `apps/web`, `apps/worker`
- Packages: `packages/contracts`, `sdk-python`, `sdk-typescript`, `security-rules`
- Infra: Dockerfiles, Terraform stubs, `wait-for-infra.sh`
- Cursor: `.cursor/rules/praevis-agents.mdc`

## Commands executed

```text
python3 -m pip install -e ".[dev]"
python3 -m pip install -e "./apps/api" "./apps/worker" "./packages/sdk-python"
cd apps/web && npm install
docker compose --env-file .env up -d postgres redis
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
python3 -m mypy apps/api/src apps/worker/src packages/sdk-python/src
cd apps/web && npm run typecheck && npm run lint && npm run build
# live probes via TestClient + curl against uvicorn
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
```

## Test / validation results

| Check | Result |
|-------|--------|
| `pytest -q` | **4 passed** |
| `ruff check` / `ruff format --check` | **pass** |
| `mypy` | **pass** |
| `apps/web` typecheck / lint / build | **pass** |
| Compose Postgres + Redis | **healthy** (`15432`, `6379`) |
| `GET /health` | **200** `{"status":"ok","service":"praevis-api"}` |
| `GET /ready` (live deps) | **200** database+redis ok |

## Architectural decisions

- ADR-0001: Codename Praevis (replaceable)
- ADR-0002: Python 3.12 target (host may be 3.11)
- ADR-0003: Root tooling + installable app packages
- ADR-0004: Celery + Redis
- ADR-0005: Default host Postgres port 15432

## Incomplete / known issues

- Host Python is 3.11.3; Docker images target 3.12 (intentional per ADR-0002).
- Scan pipeline, models, Alembic, dashboard scan UI, and worker jobs are intentionally not implemented.
- `npm audit` reported vulnerabilities in the web dependency tree (not addressed in Phase 1).
- `next lint` deprecation warning (Next 16 migration later).

## Recommended next task

Begin Phase 2: SQLAlchemy models + Alembic + `POST /v1/scans` creating durable scan records.
