# Project status

**Last updated:** 2026-07-25  
**Active phase:** Phase 6 — Retrieval-position optimization (**P6-02 done**; further P6 tasks open)  
**Codename:** Praevis (replaceable)

## Summary

Phases 1–5 MVP remains intact. Scope refined (ADR-0012): Praevis is provenance-preserving **secure retrieval** infrastructure, not a broad AI firewall/MCP platform. First optimization increment shipped: dual integrity hashes (`original_content_hash` + `sanitized_content_hash`) on scan responses, Alembic `0002_sanitized_hash`.

## Completed

- Phase 1–5 initial MVP
- P6-01 audit / preserve-first plan
- P6-02 integrity hashes + API `integrity` object

## In progress

- Phase 6 remaining tasks (transformations, policy layer, nested scores, spans, SSRF matrix, agent context)

## Not started / deferred

- Production Terraform, distributed rate limits, object storage, auth/multi-tenant, LLM classifiers
- MCP/Copilot Studio deep integrations (adapters later)
- Browser isolation, proprietary AV/TI, agent-action security platform

## Environment notes

- `make test` / `make test-security`
- After pull: `make migrate` (includes `0002_sanitized_hash`)
- Postgres host port **15432**; Redis **6379**

## Blockers

None
