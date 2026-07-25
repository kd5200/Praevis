# Plan: Phase 5 — Hardening

**Date:** 2026-07-24  
**Goal:** Expand security fixtures/regressions, add request limits, structured API errors, request timing/logging, and polish docs.

## Steps

1. Add malicious fixtures (tool-use, encoded instructions, role markers, zero-width, command exec).
2. Expand `tests/security` regression coverage.
3. Add request-id + timing middleware; structured error responses.
4. Add configurable rate limit and max request body size.
5. Lightweight metrics interface stub (null implementation).
6. Update API_SPEC, RUNBOOK, SECURITY_MODEL, agent docs; run tests/lint.

## Acceptance criteria

- [x] New fixtures covered by security tests.
- [x] API errors return `{error:{code,message,request_id}}`.
- [x] Rate limit / body limit configurable and tested.
- [x] Request logs include request_id and duration_ms.
- [x] Docs/runbook updated; tests/lint pass.
