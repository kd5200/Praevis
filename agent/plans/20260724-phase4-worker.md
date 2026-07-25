# Plan: Phase 4 — Worker execution

**Date:** 2026-07-24  
**Goal:** Async scan processing via Celery/Redis while keeping sync mode for demos.

## Steps

1. Add `process_existing_scan` service + Celery client enqueue helper in API.
2. Implement `praevis.worker.process_scan` task that reuses the API pipeline/persistence.
3. Enqueue on `wait_for_completion=false`; keep in-process path for `true`.
4. Tests: mock enqueue (queued), eager/direct process path completes.
5. Dashboard: async checkbox + client poller on in-progress detail pages.
6. Docs/STATUS/HANDOFF/run summary.

## Acceptance criteria

- [x] Async create returns quickly with `queued` (or progresses under worker/eager).
- [x] Worker task completes scan and persists results.
- [x] Sync mode unchanged.
- [x] Dashboard can poll until terminal status.
- [x] Tests/lint pass; agent docs updated.
