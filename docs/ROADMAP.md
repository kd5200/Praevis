# Roadmap

## Phase 1 — Repository foundation (current)

Monorepo, docs, API/web/worker skeletons, Compose (Postgres + Redis), Makefile, health endpoints, lint/typecheck/test wiring.

## Phase 2 — Backend vertical slice

Models + migrations, URL submit/normalize, SSRF-safe fetch (mocked in tests), extract/sanitize, prompt-injection rules, deterministic scoring, persist, API responses.

## Phase 3 — Dashboard

Submit URL, view status/decision/scores/findings/content/provenance, list recent scans.

## Phase 4 — Worker execution

Redis-backed jobs, async polling, keep sync mode for local testing.

## Phase 5 — Hardening

Security fixtures, regression tests, request limits, structured errors, logging/timing, docs/runbook polish.

## Later (post-MVP)

Object storage for raw artifacts, multi-tenant auth, additional content types (docs/files/APIs), optional LLM classifiers, production Terraform, metrics/tracing backends, SDKs beyond stubs.
