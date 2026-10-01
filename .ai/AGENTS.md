# Agent Instructions

## Coding conventions

- Prefer clear, explicit code over clever abstractions.
- Match existing project style and naming.

## Architecture constraints

- Respect boundaries described in ARCHITECTURE.md and DECISIONS.md.
- Do not introduce new frameworks without an explicit task requiring them.

## Allowed changes

- Implement the CURRENT ASSIGNED TASK in the smallest reasonable change set.
- Update tests when behavior changes.

## Prohibited changes

- Do not rewrite architecture documents unless the task explicitly requires it.
- Do not force-push, merge PRs, or modify default-branch protection.
- Do not commit secrets, credentials, or environment dumps.

## Testing requirements

- Run the project validation command when available.
- Do not claim tests passed without evidence.

## Security requirements

- Never log or commit API keys, tokens, or private keys.
- Stay inside the assigned workspace.
