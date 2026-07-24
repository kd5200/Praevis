"""Rules-based prompt-injection detector."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from praevis_api.pipeline.extract import find_hidden_text_snippets
from praevis_api.pipeline.types import PipelineFinding


@dataclass(frozen=True, slots=True)
class DetectorRule:
    id: str
    category: str
    severity: str
    title: str
    description: str
    pattern: re.Pattern[str]
    remediation: str
    confidence: float


@lru_cache
def load_rules(path: str) -> tuple[DetectorRule, ...]:
    catalog_path = Path(path)
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    rules: list[DetectorRule] = []
    for item in data.get("rules", []):
        rules.append(
            DetectorRule(
                id=item["id"],
                category=item["category"],
                severity=item["severity"],
                title=item["title"],
                description=item["description"],
                pattern=re.compile(item["pattern"]),
                remediation=item.get("remediation", ""),
                confidence=float(item.get("confidence", 0.8)),
            )
        )
    return tuple(rules)


def _match_text(
    text: str, rules: tuple[DetectorRule, ...], *, source: str
) -> list[PipelineFinding]:
    findings: list[PipelineFinding] = []
    for rule in rules:
        match = rule.pattern.search(text)
        if not match:
            continue
        evidence = match.group(0)
        if len(evidence) > 240:
            evidence = evidence[:237] + "..."
        prefix = f"[{source}] " if source else ""
        findings.append(
            PipelineFinding(
                category=rule.category,
                severity=rule.severity,
                detector=rule.id,
                title=rule.title,
                description=f"{prefix}{rule.description}",
                evidence=evidence,
                remediation=rule.remediation,
                confidence=rule.confidence,
            )
        )
    return findings


def run_security_detectors(
    *,
    text: str,
    raw_html: str | None,
    rules_path: str,
) -> list[PipelineFinding]:
    rules = load_rules(rules_path)
    findings = _match_text(text, rules, source="visible_text")

    if raw_html:
        hidden = find_hidden_text_snippets(raw_html)
        for snippet in hidden:
            hidden_matches = _match_text(snippet, rules, source="hidden_content")
            for finding in hidden_matches:
                finding.title = f"Hidden content: {finding.title}"
                # Bump severity presentation via description note; keep severity from rule.
                findings.append(finding)
            if snippet and not hidden_matches:
                # Hidden text without a specific rule still warrants a content finding when
                # it looks instruction-like.
                if re.search(r"(?i)ignore|system|assistant|secret|tool|command", snippet):
                    findings.append(
                        PipelineFinding(
                            category="prompt_injection",
                            severity="medium",
                            detector="pi-hidden-suspicious",
                            title="Suspicious hidden text",
                            description="Page contains hidden text with instruction-like language.",
                            evidence=snippet[:240],
                            remediation="Strip hidden nodes before AI consumption.",
                            confidence=0.7,
                        )
                    )
    return findings
