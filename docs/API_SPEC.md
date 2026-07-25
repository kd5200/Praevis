# API specification — Praevis

Versioned HTTP API under `/v1`. OpenAPI is served by FastAPI at `/docs`.

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness — process is up |
| GET | `/ready` | Readiness — dependencies reachable when configured |

### Example

```http
GET /health
```

```json
{ "status": "ok", "service": "praevis-api" }
```

## Scans

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/scans` | Submit URL for inspection |
| GET | `/v1/scans/{scan_id}` | Get scan |
| GET | `/v1/scans/{scan_id}/findings` | List findings |
| GET | `/v1/scans/{scan_id}/content` | Sanitized content |
| GET | `/v1/scans` | List recent scans |

### Request

```json
{
  "url": "https://example.com/article",
  "mode": "standard",
  "wait_for_completion": true
}
```

- `wait_for_completion: true` — run pipeline in-process (sync).
- `wait_for_completion: false` — enqueue Celery job; poll `GET /v1/scans/{id}`.

### Response (completed)

```json
{
  "scan_id": "uuid",
  "status": "completed",
  "submitted_url": "https://example.com/article",
  "final_url": "https://example.com/article",
  "risk_score": 22,
  "trust_score": 78,
  "decision": "allow",
  "findings": [],
  "content": {
    "title": "Example article",
    "text": "Sanitized extracted content",
    "content_type": "text/html"
  },
  "provenance": {
    "retrieved_at": "2026-07-24T12:00:00Z",
    "content_hash": "sha256:...",
    "original_content_hash": "sha256:...",
    "sanitized_content_hash": "sha256:...",
    "redirect_chain": [],
    "requested_url": "https://example.com/article",
    "normalized_url": "https://example.com/article",
    "final_url": "https://example.com/article"
  },
  "integrity": {
    "original_content_hash": "sha256:...",
    "sanitized_content_hash": "sha256:..."
  }
}
```

Notes:

- `provenance.content_hash` remains the **original retrieved body** hash (backward compatible).
- `integrity.original_content_hash` mirrors that value; `integrity.sanitized_content_hash` is over sanitized plain text.
- Future receipt fields (transformations, policy_version, detector_versions, nested scores, agent context) will evolve additively; see ADR-0012.

## Statuses

`queued` | `validating` | `fetching` | `analyzing` | `sanitizing` | `completed` | `blocked` | `failed`

## Decisions

`allow` | `warn` | `block` — derived from findings via the deterministic scoring engine.

## Errors

All non-2xx API errors use a structured envelope:

```json
{
  "error": {
    "code": "scan_not_found",
    "message": "Scan not found",
    "request_id": "uuid"
  }
}
```

| Code | HTTP | Meaning |
|------|------|---------|
| `scan_not_found` | 404 | Unknown scan id |
| `content_not_found` | 404 | Scan has no retrieved content |
| `validation_error` | 422 | Invalid body/query failed validation |
| `rate_limited` | 429 | Scan create rate limit exceeded |
| `request_too_large` | 413 | Body exceeds `MAX_REQUEST_BODY_BYTES` |
| `internal_error` | 500 | Unexpected server failure |

Pipeline/security failures on a scan are returned as completed/blocked scan records with `error_code` / `error_message` fields (not necessarily HTTP 4xx), e.g. `destination_blocked_ip`.

## Headers

| Header | Direction | Purpose |
|--------|-----------|---------|
| `X-Request-ID` | request/response | Correlation id (generated if omitted) |
| `X-Response-Time-Ms` | response | Handler duration |
| `Retry-After` | response | Present on `429` |

## Limits (configurable)

| Setting | Default | Notes |
|---------|---------|-------|
| `RATE_LIMIT_PER_MINUTE` | 60 | Per-client POST `/v1/scans`; `0` disables |
| `MAX_REQUEST_BODY_BYTES` | 65536 | Enforced via `Content-Length` |
| `MAX_URL_LENGTH` | 2048 | Also enforced by schema |
| Fetch timeouts / max bytes / redirects | see `.env.example` | SSRF-safe fetcher |
