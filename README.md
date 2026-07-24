# Praevis

Working codename for an **AI security gateway**: submit a URL, receive sanitized content, security findings, provenance, and a trust assessment before AI agents consume untrusted web data.

```text
AI agent → Praevis security gateway → external internet resource
```

> Branding is temporary. Prefer replaceable constants for product display names.

## Quick start

```bash
cp .env.example .env
make setup
make up          # PostgreSQL + Redis
make api         # http://localhost:8000
# optional:
make web         # http://localhost:3000
make worker
```

Health:

```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/ready
```

## Documentation

| Doc | Description |
|-----|-------------|
| [AGENTS.md](./AGENTS.md) | Agent rules and repo map |
| [docs/PRODUCT.md](./docs/PRODUCT.md) | Product vision |
| [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) | System design |
| [docs/SECURITY_MODEL.md](./docs/SECURITY_MODEL.md) | Security controls |
| [docs/API_SPEC.md](./docs/API_SPEC.md) | HTTP API |
| [docs/RUNBOOK.md](./docs/RUNBOOK.md) | Local operations |
| [docs/TASKS.md](./docs/TASKS.md) | Task board |
| [agent/STATUS.md](./agent/STATUS.md) | Current status |
| [agent/HANDOFF.md](./agent/HANDOFF.md) | Next task |

## Repository layout

```text
apps/api          FastAPI service
apps/web          Next.js dashboard
apps/worker       Celery worker
packages/         Contracts, SDKs, security rules
infrastructure/   Docker, Terraform stubs, scripts
docs/             Product & engineering docs
agent/            Agent workflow memory
tests/            Cross-cutting fixtures and suites
```

## Development commands

See `Makefile` and `docs/RUNBOOK.md`. Common targets: `setup`, `dev`, `test`, `lint`, `typecheck`, `clean`.

## Current milestone

**Phase 1 — Repository foundation.** Scan pipeline and dashboard features land in later phases (see `docs/ROADMAP.md`).
