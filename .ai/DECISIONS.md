# Engineering Decisions

These choices are accepted. Do not undo them unless a task explicitly records a new decision in `docs/DECISIONS.md`.

## Decision: Praevis is secure retrieval, not a broad AI security platform

Status: accepted
Date: 2026-07-25
Context: The MVP was described as an AI security gateway. Broader firewall, MCP, browser-isolation, and agent-action scope was pulling the product apart.
Decision: Own destination validation, controlled fetch, deterministic AI-content inspection, sanitization, dual scores, provenance, and a framework-neutral HTTP API. Defer the rest. Evolve `/v1/scans` additively; do not replace working modules to match a preferred name.
Consequences: Keep flat `risk_score` / `trust_score` until a versioned change adds nested scores beside them. Do not delete the dashboard or worker.

## Decision: Do not execute page JavaScript

Status: accepted
Date: 2026-07-24
Context: Fetched HTML is untrusted.
Decision: Parse with BeautifulSoup and lxml. Never run scripts from scanned pages in the fetch pipeline.
Consequences: JS-rendered sites may look incomplete. That is acceptable for this milestone.

## Decision: SSRF checks fail closed

Status: accepted
Date: 2026-07-24
Context: The fetcher is the most sensitive component.
Decision: Allow only `http`, `https`, and local `fixture://`. Reject embedded credentials. Block loopback, private, link-local, reserved, and cloud-metadata targets. Revalidate every redirect. Enforce timeouts, size limits, and a content-type allowlist.
Consequences: Do not weaken a check to make a test pass. Do not follow redirects with the HTTP client’s automatic redirect mode.

## Decision: Deterministic detectors, not an LLM

Status: accepted
Date: 2026-07-24
Context: Findings must be explainable and testable.
Decision: Prompt-injection detection is regex rules in `packages/security-rules`. Scoring is deterministic weights in `pipeline/score.py`.
Consequences: Do not add an LLM dependency for detection or scoring while rules suffice.

## Decision: Raw bodies stay out of Postgres

Status: accepted
Date: 2026-07-24
Context: Unrestricted raw HTML in the primary database is a retention and exposure risk.
Decision: Store sanitized text and metadata in Postgres. Store raw bytes through `RawArtifactStore` (`memory` in tests, local filesystem for MVP).
Consequences: Do not insert full raw HTML into scan rows.

## Decision: One pipeline for API and worker

Status: accepted
Date: 2026-07-24
Context: Duplicating stages would drift.
Decision: Celery task `praevis.worker.process_scan` calls `process_existing_scan`. Sync mode runs in-process when `wait_for_completion` is true.
Consequences: Change pipeline behavior in `apps/api`, not by forking it in `apps/worker`.

## Decision: In-process rate limit and structured errors

Status: accepted
Date: 2026-07-24
Context: MVP hardening without a distributed limiter.
Decision: Sliding-window limit in process. Errors are `{error:{code,message,request_id}}`.
Consequences: Do not replace this with Redis limits unless a task says so.

## Decision: Postgres host port 15432

Status: accepted
Date: 2026-07-24
Context: Local machines often already bind 5432.
Decision: Compose maps host `POSTGRES_PORT` (default 15432) to container 5432. `DATABASE_URL` uses `localhost:15432`.
Consequences: Do not change the default host port without updating `.env.example`.

## Decision: Codename is temporary

Status: accepted
Date: 2026-07-24
Context: Praevis may be renamed.
Decision: Treat the name as replaceable in user-facing copy. Package paths may still say `praevis`.
Consequences: Do not spend a task on a rename unless asked.
