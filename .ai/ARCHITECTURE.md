# Architecture

Praevis is a monorepo. The retrieval pipeline is plain Python so the API and the worker share one implementation.

## Stack

| Piece | Choice |
|-------|--------|
| API | FastAPI (`apps/api`, package `praevis-api`), Python 3.12 |
| Dashboard | Next.js (`apps/web`), server actions and server-side fetch to the API |
| Worker | Celery (`apps/worker`) on Redis; task `praevis.worker.process_scan` |
| Database | PostgreSQL 16. Host port **15432** (`POSTGRES_PORT`); container listens on 5432 |
| Broker | Redis 7 |
| HTML | BeautifulSoup + lxml. No JavaScript execution |
| Rules | `packages/security-rules/rules/catalog.json` |
| Migrations | Alembic under `apps/api/alembic` (`0001` schema, `0002` sanitized hash, `0003` transformations) |
| Tests | pytest from the repo root. Security cases are marked `security` |
| SDKs | `packages/sdk-python` and `packages/sdk-typescript` are stubs |
| Contracts | `packages/contracts` is a placeholder; API models live in `praevis_api.schemas` |

Tooling is rooted in `pyproject.toml`. `make up` starts Postgres and Redis. `make api`, `make web`, and `make worker` run the processes. `make test` and `make test-security` run the suites.

## How the pieces talk

```text
Client or dashboard
    → POST /v1/scans
    → apps/api (FastAPI)
         sync: run pipeline in-process
         async: enqueue Celery, poll GET /v1/scans/{id}
    → pipeline (normalize → validate → fetch → store raw → extract/sanitize
                → detectors → score → persist)
    → PostgreSQL (scan, findings, sanitized content)
    → RawArtifactStore (memory in tests, local files under var/artifacts for MVP)
    → external HTTP(S) only after destination checks
```

The worker imports `praevis_api.services.scans.process_existing_scan`. Do not copy the pipeline into the worker.

Pipeline code lives in `apps/api/src/praevis_api/pipeline/`:

| Module | Role |
|--------|------|
| `runner.py` | Orchestrates a synchronous scan |
| `normalize.py` | URL cleanup; allows `http`, `https`, and `fixture` |
| `validate_destination.py` | SSRF: blocked hosts, private/loopback/link-local IPs, DNS checks |
| `fetch.py` | Manual redirects, revalidation, timeouts, size and content-type limits |
| `extract.py` | Sanitize HTML and record transformations |
| `detect.py` | Rule match on visible and hidden text |
| `score.py` | Deterministic risk, trust, and the current allow/warn/block decision |
| `integrity.py` | `sha256:` digests |
| `fixtures.py` | `fixture://` demo bodies |

`services/scans.py` persists results and maps them to the HTTP schema. Raw HTML stays out of Postgres; only a storage reference is stored.

## Boundaries

- Framework integrations (MCP, Copilot Studio, OpenAI tools) are HTTP clients of `/v1/scans`, not a second domain model.
- Sync (`wait_for_completion: true`) is the path tests and local demos rely on. Async is optional.
- Tests must use fixtures or `httpx.MockTransport`. Do not call uncontrolled public websites.
