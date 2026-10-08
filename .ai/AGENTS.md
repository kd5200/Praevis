# Agent Instructions

Work from this directory’s briefs (`PRODUCT.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `STATUS.md`) and the assigned task. Do not treat `.ai/TASKS.md` as the queue.

## Coding conventions

- Match the existing style: typed Python, `from __future__ import annotations`, small functions, dataclasses in `pipeline/types.py`.
- Keep changes small and limited to the task. Do not rename packages or rewrite a working module for taste.
- Put HTTP models in `praevis_api.schemas`. Do not invent a second copy in `packages/contracts` until a task says to.
- User-facing product name should stay easy to replace. Internal package names may stay `praevis`.

## How to change the pipeline

- Edit stages under `apps/api/src/praevis_api/pipeline/` and orchestration in `services/scans.py`.
- The worker must keep calling the API pipeline. Do not duplicate stages in `apps/worker`.
- Preserve sync `wait_for_completion: true`. Do not move the whole pipeline to Celery.
- API changes are additive. Keep existing response fields unless the task says to remove them.
- New persisted columns need an Alembic revision after `0003_transformations`.

## Testing requirements

- Add or update tests for behavior changes. Security changes need `@pytest.mark.security` coverage.
- Use fixtures or `httpx.MockTransport`. Never depend on uncontrolled public sites.
- From the repo root: `python3 -m pytest -q` for the suite you touched, and `make test-security` when SSRF, fetch, or detectors change.
- Do not claim a command passed unless you ran it and saw the result.
- Do not weaken or delete a security assertion to get green.

## What you must not touch

- Do not disable SSRF checks, redirect revalidation, timeouts, size limits, or the content-type allowlist.
- Do not execute JavaScript from scanned pages.
- Do not add an LLM for detection or scoring.
- Do not store unrestricted raw HTML in Postgres.
- Do not commit `.env`, credentials, `var/artifacts/`, or local session notes.
- Do not force-push, rewrite published history, or change branch protection.
- Do not expand into MCP governance, browser isolation, billing, auth, or a second SDK unless the assigned task says so.
- Dashboard polish is out of scope unless the task is specifically about the dashboard.

## Security

- Fail closed on destination and fetch errors.
- Do not log secrets or full page bodies.
- Stay inside this repository.
