# Project status

**Last updated:** 2026-07-24  
**Active phase:** Phase 3 — Dashboard (**complete**)  
**Codename:** Praevis (replaceable)

## Summary

Phase 3 adds a minimal operational Next.js dashboard: URL submission, recent scans list, and scan detail views (decision, risk/trust, findings, sanitized content, provenance). API CORS is enabled for the local web origin; the dashboard primarily uses server-side fetch / server actions.

## Completed

- Phase 1 foundation
- Phase 2 backend vertical slice
- Phase 3 dashboard (P3-01 … P3-04)

## In progress

- None

## Not started

- Phase 4: Worker job processing for async scans
- Phase 5: Hardening extras

## Environment notes

- Web: http://localhost:3000 (`make web`)
- API: http://localhost:8000 (`make api`)
- Postgres host port **15432**; Redis **6379**

## Blockers

None
