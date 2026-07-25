# Plan — Phase 6 retrieval-position optimization

**Date:** 2026-07-25  
**Status:** P6-01/P6-02 complete; remaining tasks open

## Goal

Align the repository with the refined product position without rewriting the working Phases 1–5 vertical slice.

## Preserve-first optimization map

### Keep

| Module | Why |
|--------|-----|
| `pipeline/normalize.py`, `validate_destination.py`, `fetch.py` | Controlled retrieval already implemented and tested |
| `pipeline/detect.py` + `packages/security-rules` | Deterministic AI-specific inspection |
| `pipeline/extract.py` | Sanitization/extraction (extend, don’t replace) |
| `pipeline/runner.py` + sync path | End-to-end slice works |
| `apps/worker` Celery reuse of API pipeline | Async optional; sync preserved |
| Dashboard submit/list/detail | Sufficient operator UI |
| Structured errors, rate limits, fixtures | Hardening stays |

### Harden

| Module | Gap |
|--------|-----|
| SSRF/redirect test matrix | Missing integer/hex IPs, public→private redirect cases, DNS-rebinding focused tests |
| Fetch MIME/extension mismatch | Content-type allowlist exists; mismatch detection thin |

### Extend

| Module | Next |
|--------|------|
| Integrity hashes | **Done (P6-02)** |
| `extract.py` | Transformation records (P6-03) |
| `score.py` | Split decision into `policy` module (P6-04); nest scores (P6-05) |
| Provenance | Source spans / citations (P6-06) |
| Request schema | Additive `agent` / `policy` fields (P6-08) |

### Migrate (versioned, additive)

| Contract | Plan |
|----------|------|
| `POST /v1/scans` body | Keep `url`; later accept `resource` envelope as alternate |
| Flat `risk_score`/`trust_score` | Keep aliases; add nested `scores.content_risk` / `scores.source_trust` |
| `scan_id` as receipt id | Keep; add `audit_id` when persistence model expands |

### Defer

SDK expansion (both), MCP core, browser automation, paid TI/AV, billing, multi-tenant admin, agent-action platform.

### Remove

None — no dead modules warrant deletion this milestone.

## First increment (this session)

Dual integrity hashes + `integrity` API object + Alembic `0002_sanitized_hash`.
