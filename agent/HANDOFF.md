# Handoff

**Updated:** 2026-07-24 (Phase 3 complete)

## Recommended next task

**Phase 4 — Worker execution:** Enqueue scans on Redis/Celery when `wait_for_completion=false`, process the pipeline in `apps/worker`, support status polling from API/dashboard, keep sync mode for local demos.

## Verify environment

```bash
make up && make migrate
make api    # terminal 1
make web    # terminal 2
# open http://localhost:3000
make test
```

## Notes for the next agent

- Dashboard lives in `apps/web` (`/` and `/scans/[scanId]`).
- Submit uses a server action calling `POST /v1/scans` with `wait_for_completion=true`.
- Async queued scans still need Phase 4 worker wiring before the UI should advertise async mode.
- Do not point automated tests at uncontrolled public websites.
- Codename Praevis remains replaceable via `NEXT_PUBLIC_APP_NAME` / `APP_NAME`.
