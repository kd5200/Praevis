# Architecture — Praevis

## Product contract

Praevis provides **provenance-preserving secure retrieval** for AI agents (ADR-0012). Framework integrations (MCP, Copilot Studio, OpenAI tools) are adapters to the HTTP retrieval API — not the core domain.

## High-level

```text
┌────────────┐     ┌────────────┐     ┌─────────────┐     ┌──────────────┐
│  Next.js   │────▶│  FastAPI   │────▶│   Worker    │────▶│  External    │
│  dashboard │     │  apps/api  │     │ apps/worker │     │  HTTP(S)     │
└────────────┘     └─────┬──────┘     └──────┬──────┘     └──────────────┘
                         │                   │
                   ┌─────▼─────┐       ┌─────▼─────┐
                   │ PostgreSQL│       │   Redis   │
                   └───────────┘       └───────────┘
```

## Components

| Component | Role |
|-----------|------|
| `apps/api` | Versioned HTTP API, health/ready, scan CRUD/status, sync mode for light pipelines |
| `apps/worker` | Async scan pipeline execution via Celery + Redis |
| `apps/web` | Minimal operational dashboard |
| `packages/contracts` | Shared schemas / OpenAPI-aligned types |
| `packages/security-rules` | Versioned deterministic detector rules |
| `packages/sdk-*` | Client SDKs (stubs in Phase 1) |
| PostgreSQL | Durable scans, findings, content metadata |
| Redis | Task broker / job messaging |

## Scan pipeline stages (framework-independent)

1. `normalize_url`
2. `validate_destination`
3. `resolve_dns`
4. `fetch_resource`
5. `inspect_redirects`
6. `classify_content_type`
7. `extract_content`
8. `run_security_detectors`
9. `sanitize_content`
10. `calculate_scores`
11. `persist_results`
12. `finalize_decision`

Stages should accept and return typed objects so the same pipeline can run in-process, in Celery workers, or later in containers/serverless.

## Storage

- Relational DB stores scan metadata, findings, and **sanitized** content fields.
- Raw artifacts use a storage interface designed for later encrypted object storage + retention (do not dump unrestricted raw HTML into Postgres).

## Sync vs async

- `wait_for_completion: true` — API may run pipeline in-process (MVP) or wait on worker completion.
- Async — API queues job; client polls `GET /v1/scans/{id}`.

## Observability

Structured logs with `request_id`, `scan_id`, `pipeline_stage`, `detector`, `duration_ms`, `outcome`. No secrets or full sensitive page bodies in logs. Metrics/tracing interfaces prepared later; do not overbuild in MVP.
