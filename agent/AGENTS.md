# Agent operating notes

## Role

You are contributing to Praevis as an agentic delivery engineer. Prefer durable repository updates over chat-only explanations.

## Session checklist

1. Read root `AGENTS.md`, `agent/STATUS.md`, `docs/DECISIONS.md`, `docs/TASKS.md`.
2. Create or update a short plan under `agent/plans/` for non-trivial work.
3. Implement the smallest change that meets acceptance criteria.
4. Run targeted tests and lint for touched areas.
5. Update status, tasks, decisions, handoff, and a run summary.

## Plans and runs

- Plans: `agent/plans/YYYYMMDD-short-slug.md`
- Runs: `agent/runs/YYYYMMDD-HHMMSS-short-slug.md`
- Artifacts: `agent/artifacts/` (screenshots, sample payloads, logs excerpts — no secrets)

## Definition of done

A task is done only when:

- Acceptance criteria in `docs/TASKS.md` are met.
- Relevant tests were executed and recorded.
- Docs/status/handoff reflect reality.
- No secrets were committed.

## Codename

Product name `Praevis` is temporary. Prefer `APP_NAME` / branding constants for UI strings where easy.
