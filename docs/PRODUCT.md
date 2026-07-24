# Product vision — Praevis

**Codename:** Praevis (working name; branding should remain easy to replace).

## Problem

AI agents increasingly fetch untrusted web content and feed it into reasoning, tools, and memory. Direct consumption exposes agents to prompt injection, malicious HTML, SSRF-adjacent abuse when agents can request URLs, and opaque provenance.

## Solution

Praevis is a **security gateway** between AI agents (and enterprise apps/developers) and untrusted external information.

```text
AI agent → Praevis security gateway → external internet resource
```

Submit a URL; receive sanitized content, security findings, provenance, and a trust assessment **before** the content is used in AI reasoning.

In **enforced mode**, the agent must not directly consume unknown web content.

## MVP scope

Vertical slice for URL inspection:

1. Submit URL → validate/normalize → SSRF-safe fetch → extract/sanitize → rule-based prompt-injection detection → deterministic risk/trust scores → persist → API + minimal dashboard.

Out of scope for MVP: full multi-tenant SaaS, LLM classifiers, browser/JS execution, arbitrary file/API ingestion, production cloud infra.

## Long-term vision

Reusable trust and security layer for AI agents consuming websites, documents, files, APIs, feeds, and other external data.

## Users

- AI agent runtimes and orchestration platforms
- Enterprise applications mediating agent browsing
- Developers integrating safe web retrieval into tools

## Success for MVP

A local Docker Compose demo where submitting a malicious fixture URL yields a clear `block`/`warn` decision, findings with evidence, sanitized text, and provenance — without contacting uncontrolled public sites in automated tests.
