"""Deterministic risk/trust scoring engine."""

from __future__ import annotations

from typing import Any

from praevis_api.pipeline.types import PipelineFinding, ScoreResult

CATEGORY_WEIGHTS: dict[str, float] = {
    "prompt_injection": 1.0,
    "ssrf": 1.0,
    "redirect": 0.6,
    "content": 0.5,
    "transport": 0.4,
    "policy": 0.7,
}

SEVERITY_MULTIPLIERS: dict[str, float] = {
    "info": 2.0,
    "low": 8.0,
    "medium": 18.0,
    "high": 32.0,
    "critical": 48.0,
}

MAX_RISK = 100
BASE_TRUST = 80


def _finding_contribution(finding: PipelineFinding) -> float:
    weight = CATEGORY_WEIGHTS.get(finding.category, 0.5)
    severity = SEVERITY_MULTIPLIERS.get(finding.severity, 10.0)
    confidence = max(0.0, min(finding.confidence, 1.0))
    return weight * severity * confidence


def calculate_scores(
    findings: list[PipelineFinding],
    *,
    is_https: bool,
    redirect_count: int,
    block_threshold: int = 70,
    warn_threshold: int = 40,
) -> ScoreResult:
    contributions: list[dict[str, Any]] = []
    raw_risk = 0.0
    for finding in findings:
        value = _finding_contribution(finding)
        raw_risk += value
        contributions.append(
            {
                "detector": finding.detector,
                "category": finding.category,
                "severity": finding.severity,
                "confidence": finding.confidence,
                "contribution": round(value, 2),
            }
        )

    risk = int(min(MAX_RISK, round(raw_risk)))

    trust = BASE_TRUST
    if is_https:
        trust += 5  # transport hygiene bonus only; not a trustworthiness claim
    else:
        trust -= 15
    trust -= min(20, redirect_count * 4)
    trust -= int(risk * 0.6)
    trust = int(max(0, min(100, trust)))

    if risk >= block_threshold or any(f.severity == "critical" for f in findings):
        decision = "block"
    elif risk >= warn_threshold:
        decision = "warn"
    else:
        decision = "allow"

    explanation = {
        "category_weights": CATEGORY_WEIGHTS,
        "severity_multipliers": SEVERITY_MULTIPLIERS,
        "contributions": contributions,
        "raw_risk": round(raw_risk, 2),
        "risk_score": risk,
        "trust_score": trust,
        "trust_assumptions": [
            "HTTPS alone does not imply the domain is trustworthy.",
            "Trust reflects confidence in safely consuming this retrieval.",
            "Absence of findings is not zero residual risk.",
        ],
        "thresholds": {"warn": warn_threshold, "block": block_threshold},
        "decision": decision,
    }
    return ScoreResult(
        risk_score=risk, trust_score=trust, decision=decision, explanation=explanation
    )
