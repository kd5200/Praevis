# Agent workflow

## Standard loop

```text
orient → plan → implement → test → document → handoff
```

### Orient

Read `AGENTS.md`, `agent/STATUS.md`, `docs/DECISIONS.md`, `docs/TASKS.md`, and area-specific docs. Inspect tests that cover the behavior you will change.

### Plan

For multi-step work, write `agent/plans/<date>-<slug>.md` with scope, steps, acceptance criteria, and out-of-scope items.

### Implement

- Keep diffs reviewable.
- Respect package boundaries.
- Prefer deterministic security rules over LLMs in early phases.
- Never weaken SSRF or safety checks to green tests.

### Test

Run the narrowest meaningful suite first, then broader checks when touching shared surfaces:

```bash
make test
make test-security   # when security paths change
make lint
make typecheck
```

Record exact commands and outcomes in the run summary. Do not claim pass without execution.

### Document

Update:

- `agent/STATUS.md` — what is true now
- `docs/TASKS.md` — task progress
- `docs/DECISIONS.md` — new ADRs
- `agent/HANDOFF.md` — next recommended task
- `agent/runs/<...>.md` — this session

### Handoff

End with one clear next task, known blockers, and how to verify the environment (`make setup`, `make dev`, health checks).
