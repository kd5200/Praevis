# Product vision — Praevis

**Codename:** Praevis (working name; branding should remain easy to replace).

## Refined position

Praevis is **provenance-preserving secure retrieval infrastructure for AI agents**.

Its primary function is to transform an untrusted external resource into useful, sanitized, traceable evidence that an AI agent can safely consume.

```text
AI agent requests an external resource
        ↓
Praevis validates the destination
        ↓
Praevis retrieves the resource in a controlled manner
        ↓
Praevis inspects cyber and AI-specific threats
        ↓
Praevis sanitizes and extracts useful content
        ↓
Praevis calculates content-risk and source-trust scores
        ↓
Praevis applies a versioned policy
        ↓
Praevis returns sanitized content, provenance and an audit receipt
```

In **enforced mode**, the agent must not directly consume unknown web content; it consumes only Praevis outputs.

## Problem

AI agents increasingly fetch untrusted web content and feed it into reasoning, tools, and memory. Direct consumption exposes agents to prompt injection, malicious HTML, SSRF-adjacent abuse when agents can request URLs, and opaque provenance.

## What Praevis is not (current milestone)

Do not expand the core toward these without an explicit ADR:

- A complete AI firewall platform
- A general MCP governance platform
- A full secure web gateway replacement
- A global browser-isolation provider
- A proprietary antivirus company
- A broad AI governance suite
- A complete agent identity platform
- A complete downstream agent-action security platform

Reusable work in those directions should be **isolated and deferred**, not deleted.

## MVP scope (delivered + optimization)

Vertical slice for URL retrieval:

1. Submit URL → validate/normalize → SSRF-safe fetch → extract/sanitize → rule-based prompt-injection detection → deterministic risk/trust scores → persist → API + minimal dashboard + optional worker.
2. Integrity receipt fields: original + sanitized content hashes (additive on `/v1/scans`).

Out of scope for the focused retrieval milestone: full multi-tenant SaaS, LLM classifiers, browser/JS execution, arbitrary file/API ingestion, production cloud infra, MCP as core domain.

## Long-term attachment points

Browser rendering, file processing, malware providers, MCP adapters, and agent-action controls can attach **around** the retrieval core via provider interfaces and framework adapters — they must not redefine the core domain model.

## Users

- AI agent runtimes and orchestration platforms
- Enterprise applications mediating agent browsing
- Developers integrating safe web retrieval into tools

## Success criteria

A local Docker Compose demo where submitting a malicious fixture URL yields a clear `block`/`warn` decision, findings with evidence, sanitized text, provenance, and integrity hashes — without contacting uncontrolled public sites in automated tests.
