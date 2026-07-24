# API specification — Praevis

Versioned HTTP API under `/v1`. OpenAPI will be served by FastAPI once scan routes exist.

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

## Scans (Phase 2+)

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
    "redirect_chain": []
  }
}
```

## Statuses

`queued` | `validating` | `fetching` | `analyzing` | `sanitizing` | `completed` | `blocked` | `failed`

## Decisions

`allow` | `warn` | `block` — derived from findings via the deterministic scoring engine.

## Errors

Structured error codes will be expanded in Phase 5. Phase 1 health endpoints return JSON only.
