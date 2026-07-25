# Handoff

**Updated:** 2026-07-25 (ADR-0012 + P6-02 integrity hashes)

## Recommended next task

**P6-03 — Sanitization transformation records**  
Extend `extract.sanitize_html` / `extract_content` to emit structured transformation records (e.g. `{type, target, reason, count}`), persist on the scan (JSON column or content metadata), and expose under `integrity.transformations` (or a sibling field). Keep the existing sanitize behavior; do not rewrite BeautifulSoup usage.

Alternatively, if security gaps are higher priority: **P6-07** expand SSRF/redirect regression tests before changing fetch.

## Verify environment

```bash
make up && make migrate
make api && make worker && make web   # separate terminals
make test
make test-security
```

## Notes for the next agent

- Read ADR-0012 before expanding scope. Preserve-first: reuse pipeline; evolve `/v1/scans` additively.
- `content_hash` / `integrity.original_content_hash` = raw body; `sanitized_content_hash` = sanitized plain text.
- Dashboard is low priority; API + integrity/provenance are highest leverage.
- Do not weaken SSRF checks or hit uncontrolled public sites in automated tests.
- Codename Praevis remains replaceable.
