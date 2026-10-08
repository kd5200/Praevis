# Product

Praevis is provenance-preserving secure retrieval infrastructure for AI agents.

An agent submits an untrusted URL. Praevis validates the destination, fetches it under limits, inspects cyber and AI-specific threats, sanitizes the page, scores content risk and source trust, and returns sanitized text plus an audit receipt. In enforced mode the agent must consume only that receipt, not the raw page.

The working name is replaceable. Prefer config constants over hard-coded product names in user-facing copy.

## Who it is for

- Agent runtimes and orchestration platforms that must not let agents browse the open web directly
- Enterprise applications that mediate agent research and need an allow / warn / block decision plus provenance
- Developers integrating safe URL retrieval into tools (HTTP API first; framework adapters later)

Primary buyers are agent platforms and mid-market or enterprise teams running many agents behind one policy. A self-hosted personal agent can call the same API, but that is not the product center.

## What the product does today

`POST /v1/scans` with a URL (sync by default) returns:

- Decision: `allow`, `warn`, or `block`
- Flat `risk_score` and `trust_score` plus an explanation
- Findings from deterministic prompt-injection rules
- Sanitized text (and restricted HTML)
- Provenance: requested, normalized, and final URL, redirects, retrieval time
- Integrity: original body hash, sanitized text hash, and sanitization transformation records

`fixture://<filename>` loads local demo pages and does not touch the public internet.

## Out of scope

Do not expand the core into these without an explicit new decision:

- A complete AI firewall, MCP governance platform, or secure-web-gateway replacement
- Browser isolation or executing JavaScript from scanned pages
- A proprietary antivirus or threat-intel network
- Agent identity, downstream tool authorization, billing, or multi-tenant admin
- LLM classifiers where a deterministic rule is enough
- File, email, or API ingestion beyond HTML and plain text
- Shipping both SDKs or a framework-specific core

Those ideas may attach later as adapters around the retrieval API. They must not redefine the domain.
