# Security model — Praevis

## Trust boundary

External HTTP(S) responses and redirect chains are **untrusted**. Praevis sits between the agent and the network so agents consume only gateway outputs (sanitized text, findings, scores, provenance).

## Fetch defenses (required)

Deny or fail closed on:

- localhost / loopback
- private IPv4/IPv6, link-local, multicast, reserved ranges
- cloud metadata endpoints
- malformed URLs, unsupported schemes (allow **HTTP/HTTPS only**)
- embedded credentials
- excessive redirects; public→private redirects
- DNS rebinding (resolve before connect; revalidate each redirect)
- oversized / slow responses
- unsupported content types

Strict connection/read timeouts, response size limits, redirect limits, content-type allowlist, identifiable User-Agent.

**Do not execute remote JavaScript** in the initial fetch pipeline.

## Prompt-injection detection

Rules-based detectors in `packages/security-rules` before any LLM classifier. Findings must include evidence and matched rule id.

## Sanitization

Remove scripts, event handlers, iframes, forms, embeds, unsafe URLs, and hidden content where appropriate. Primary AI-consumable output is plain text; optional restricted sanitized HTML. Preserve provenance (source URL, content hash).

## Scoring

Deterministic, explainable risk and trust scores (category weights, severity multipliers, confidence, caps). Decisions: `allow` | `warn` | `block`. No opaque ML for MVP scoring.

### Assumptions (initial)

- HTTPS alone does **not** imply trustworthiness.
- Absence of findings does not mean zero residual risk.
- Trust score reflects confidence in safely consuming this retrieval, not global domain reputation.

## Testing

Automated tests must not rely on uncontrolled public websites. Use fixture servers or mocked HTTP transports. Malicious fixtures live under `tests/malicious-pages/` and `tests/fixtures/`.
