# Project Status

Updated: 2026-10-08. Describes what is on `main`, not local uncommitted work.

## What works

- Sync scan: `POST /v1/scans` with `wait_for_completion: true` runs normalize → SSRF validate → limited fetch → sanitize/extract → rule detection → score → persist.
- Async path: `wait_for_completion: false` enqueues Celery; clients poll `GET /v1/scans/{id}`. Sync remains the reliable local path.
- Decisions `allow` / `warn` / `block` from deterministic scores. A critical finding blocks.
- Prompt-injection rules catch visible text, hidden DOM text, and basic zero-width obfuscation. Evidence is stored on findings.
- HTML sanitizer removes scripts, iframes, forms, event handlers, unsafe URL schemes, comments, and hidden nodes.
- Receipt fields: original and sanitized hashes, plus `integrity.transformations` (Alembic `0002` and `0003`).
- Destination blocks for standard loopback, private, link-local, and cloud-metadata hosts, including public-to-private redirects, oversized bodies, and disallowed content types.
- `fixture://` demo pages under `tests/fixtures` and `tests/malicious-pages`.
- Dashboard can submit a URL and show decision, scores, findings, content, and provenance.
- Health and readiness endpoints, structured API errors, in-process rate limit, request id.

## What is incomplete or broken

- Final allow/warn/block still lives inside `pipeline/score.py`. There is no separate versioned policy module and no `decision_reasons` field.
- Scores are flat integers. Nested `content_risk` / `source_trust` objects are not on the API.
- Sanitized text has no source spans or citation ids.
- Requests do not accept agent id, framework, or policy profile.
- Non-standard IP spellings (decimal, hex, octal, shorthand such as `127.1`) are not blocked by the code on `main`. Standard literals are.
- DNS rebinding against a live resolver is not covered. Checks run at fetch time when no mock transport is injected.
- No API authentication, tenancy, or usage metering.
- Raw artifacts are local files (`var/artifacts`), not object storage.
- Rate limiting is per process, not shared across API replicas.
- SDKs and `packages/contracts` are stubs. The dashboard is an operator view, not the product surface.
- Pages that depend on JavaScript are not fully retrieved.

## Blockers

None for local sync scans. Production use is blocked on auth, a stable receipt contract, and deployment — not on the current vertical slice.
