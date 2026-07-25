# Runbook — local development

## Prerequisites

- Docker + Docker Compose v2
- Make
- Node.js 20+ (for `apps/web`)
- Python 3.12 preferred (3.11 may work for local tooling; Compose uses 3.12)

## First-time setup

```bash
cp .env.example .env
make setup
make up
```

`make up` starts PostgreSQL and Redis. API/web/worker can run via Make targets or Compose profiles when enabled.

## Common commands

| Command | Purpose |
|---------|---------|
| `make setup` | Install Python and Node dependencies |
| `make up` / `make down` | Start/stop infra (Postgres, Redis) |
| `make api` | Run API on :8000 |
| `make web` | Run Next.js on :3000 |
| `make worker` | Run Celery worker |
| `make test` | Run pytest |
| `make test-security` | Security-focused tests |
| `make lint` | Ruff lint |
| `make typecheck` | mypy + web tsc |
| `make migrate` | Alembic upgrade head |
| `make seed` | Seed data (placeholder) |
| `make clean` | Remove caches and build artifacts |

## Migrations

With Postgres running (`make up`):

```bash
make migrate
```

Uses `DATABASE_URL` from the environment (default host port `15432`).

## Dashboard

```bash
make up && make migrate
make api      # :8000
make worker   # async scans
make web      # :3000
```

Open http://localhost:3000 to submit URLs and review scan results.

- Sync (default): leave "Wait for completion" checked.
- Async: uncheck it, ensure `make worker` is running, and the detail page will poll until finished.

## Health checks

```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/ready
```

## Troubleshooting

- **Port in use:** Change ports in `.env`. Default host Postgres mapping is `15432` to avoid clashes with local Postgres on `5432`.
- **Ready fails:** Ensure `make up` is running and `DATABASE_URL` / `REDIS_URL` match Compose.
- **Python version:** Prefer running API via Docker image `python:3.12` if host lacks 3.12.
- **429 rate_limited:** Raise `RATE_LIMIT_PER_MINUTE` or set `0` to disable locally.
- **413 request_too_large:** Raise `MAX_REQUEST_BODY_BYTES`.
- **Async scans stuck in queued:** Ensure `make worker` is running and Redis is healthy.

## Request correlation

API responses include `X-Request-ID` and `X-Response-Time-Ms`. Pass your own `X-Request-ID` to correlate client and server logs.

## Security note

Do not point automated tests at arbitrary public URLs. Use fixtures under `tests/fixtures/` and `tests/malicious-pages/`, plus mocked HTTP transports. Never commit real secrets; use `.env` locally only.
