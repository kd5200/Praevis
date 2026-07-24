# Plan: Phase 3 — Dashboard

**Date:** 2026-07-24  
**Goal:** Minimal operational dashboard to submit URLs and inspect scan results.

## Scope

P3-01 … P3-04. Preserve existing web visual tokens. No branding polish beyond usability.

## Steps

1. Add CORS config to API for local web origin.
2. Add web `lib/` types + API helpers (server-side fetch).
3. Home page: submit form (server action) + recent scans list.
4. Detail page: decision, risk/trust, findings, sanitized content, provenance.
5. Typecheck/lint/build; update agent docs.

## Acceptance criteria

- [x] Submit URL from dashboard and land on result view.
- [x] Result shows decision, scores, findings, content, provenance.
- [x] Recent scans list links to details.
- [x] Web typecheck/lint/build pass; health/API tests still pass.
- [x] STATUS/HANDOFF/run updated.

## Out of scope

Worker async polling UI polish (Phase 4), auth, heavy design system.
