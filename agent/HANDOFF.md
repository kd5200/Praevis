# Handoff

**Updated:** 2026-07-24 (Phase 5 complete — initial MVP milestone done)

## Recommended next task

Post-MVP: pick from `docs/ROADMAP.md` later items — e.g. encrypted object storage for raw artifacts, auth/multi-tenant, distributed rate limiting, production Terraform modules, or SDK expansion. Alternatively run a full local demo rehearsal and capture gaps.

## Verify environment

```bash
make up && make migrate
make api && make worker && make web   # separate terminals
make test
make test-security
```

## Notes for the next agent

- Initial Phases 1–5 acceptance criteria are met per `docs/TASKS.md`.
- Security fixtures live under `tests/malicious-pages/`.
- API errors use `{error:{code,message,request_id}}`.
- Do not weaken SSRF checks or hit uncontrolled public sites in automated tests.
- Codename Praevis remains replaceable.
