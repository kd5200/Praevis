# AGENTS.md — Praevis

Working codename: **Praevis**. Treat branding as replaceable; prefer config constants over hard-coded product names in user-facing copy where practical.

## Mission

Praevis is **provenance-preserving secure retrieval infrastructure for AI agents**. Agents submit a URL (and later other artifact types) and receive sanitized content, security findings, provenance, integrity hashes, and a trust assessment before using that content in reasoning.

Core interaction:

```text
AI agent → Praevis secure retrieval → external internet resource
```

In enforced mode, the agent must not directly consume unknown web content.

## Before you change code

1. Read this file (`AGENTS.md`).
2. Read `agent/STATUS.md`.
3. Read `docs/DECISIONS.md`.
4. Read `docs/TASKS.md`.
5. Read docs relevant to the area you will touch.
6. Inspect existing tests before changing behavior.

Do not rely on chat history as project memory. Repository files are the durable source of truth.

## After every meaningful work session

1. Update `agent/STATUS.md`.
2. Update `docs/TASKS.md`.
3. Add architectural decisions to `docs/DECISIONS.md` when applicable.
4. Create a run summary under `agent/runs/`.
5. Document all tests executed and their results.
6. Record incomplete work honestly.
7. Leave a clear recommended next task in `agent/HANDOFF.md`.

## Agent boundaries

Agents **must**:

- Make small, reviewable changes.
- Preserve module boundaries (`apps/*`, `packages/*`, `tests/*`).
- Add tests for new behavior.
- Use typed interfaces.
- Avoid duplicating domain models; share via `packages/contracts` where practical.
- Avoid silently changing API contracts.
- Record important decisions.
- Run relevant linting and tests.
- Refuse to mark a task complete when acceptance criteria are not met.

Agents **must not**:

- Commit secrets.
- Disable security checks to make tests pass.
- Allow arbitrary outbound network requests without validation.
- Execute JavaScript from scanned pages in the initial fetch pipeline.
- Add an LLM dependency where deterministic rules are sufficient.
- Introduce major infrastructure without documenting the decision.
- Rewrite unrelated modules during a focused task.
- Claim that a command passed unless it was actually executed.

## Repository map

| Path | Purpose |
|------|---------|
| `apps/api` | FastAPI service |
| `apps/web` | Next.js dashboard |
| `apps/worker` | Background scan workers |
| `packages/contracts` | Shared API/domain contracts |
| `packages/sdk-python` | Python client SDK (stub) |
| `packages/sdk-typescript` | TypeScript client SDK (stub) |
| `packages/security-rules` | Versioned detector rules |
| `infrastructure/` | Docker, Terraform stubs, scripts |
| `docs/` | Product and engineering docs |
| `agent/` | Agent workflow, status, plans, runs |
| `tests/` | Cross-cutting fixtures and suites |

## Current milestone

See `docs/TASKS.md` and `agent/STATUS.md`. Complete phases in order; do not expand scope without updating those files.

## Security posture (non-negotiable)

The URL fetcher is the most sensitive component. SSRF defenses, redirect revalidation, timeouts, size limits, and content-type allowlists are required before any real outbound fetch ships. Tests must not depend on uncontrolled public websites.

## Further reading

- `agent/AGENTS.md` — agent operating notes
- `agent/WORKFLOW.md` — session workflow
- `docs/ARCHITECTURE.md` — system design
- `docs/SECURITY_MODEL.md` — threat model and controls
- `docs/API_SPEC.md` — HTTP API
- `docs/DECISIONS.md` — ADRs
- `docs/RUNBOOK.md` — local operations
