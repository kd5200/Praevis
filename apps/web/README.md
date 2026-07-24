# Next.js dashboard for Praevis (working codename).

## Phase 3 capabilities

- Submit a URL for inspection
- View recent scans
- Inspect decision, risk/trust scores, findings, sanitized content, and provenance

## Run

```bash
# from repo root, with API + Postgres running
make api
make web
```

Open http://localhost:3000

`NEXT_PUBLIC_API_BASE_URL` defaults to `http://localhost:8000`.
