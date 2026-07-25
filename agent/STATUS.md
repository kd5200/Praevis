# Project status

**Last updated:** 2026-07-24  
**Active phase:** Phase 5 — Hardening (**complete**)  
**Codename:** Praevis (replaceable)

## Summary

MVP vertical slice is hardened: expanded malicious fixtures/regressions, structured API errors, request-id/timing middleware, configurable rate/body limits, detector zero-width normalization, and docs/runbook updates. All five planned phases for the initial milestone are complete.

## Completed

- Phase 1 foundation
- Phase 2 backend vertical slice
- Phase 3 dashboard
- Phase 4 worker execution
- Phase 5 hardening (P5-01 … P5-06)

## In progress

- None

## Not started / later

- Production Terraform, distributed rate limits, object storage for raw artifacts, auth/multi-tenant, optional LLM classifiers (post-MVP roadmap)

## Environment notes

- `make test` / `make test-security`
- Limits: `RATE_LIMIT_PER_MINUTE`, `MAX_REQUEST_BODY_BYTES`, `MAX_URL_LENGTH`
- Postgres host port **15432**; Redis **6379**

## Blockers

None
