"""Scoring engine unit tests."""

from praevis_api.pipeline.score import calculate_scores
from praevis_api.pipeline.types import PipelineFinding


def test_no_findings_allow() -> None:
    result = calculate_scores([], is_https=True, redirect_count=0)
    assert result.decision == "allow"
    assert result.risk_score == 0
    assert result.trust_score >= 70
    assert "contributions" in result.explanation


def test_critical_finding_blocks() -> None:
    findings = [
        PipelineFinding(
            category="prompt_injection",
            severity="critical",
            detector="pi-test",
            title="Critical",
            description="x",
            confidence=1.0,
        )
    ]
    result = calculate_scores(findings, is_https=True, redirect_count=0)
    assert result.decision == "block"
    assert result.risk_score >= 40
    assert result.explanation["contributions"][0]["detector"] == "pi-test"


def test_medium_finding_can_warn() -> None:
    findings = [
        PipelineFinding(
            category="prompt_injection",
            severity="medium",
            detector="pi-med",
            title="Med",
            description="x",
            confidence=1.0,
        )
    ]
    result = calculate_scores(
        findings, is_https=False, redirect_count=2, warn_threshold=10, block_threshold=70
    )
    assert result.decision in {"warn", "block", "allow"}
    assert result.risk_score == 18


def test_allow_has_no_threshold_reason() -> None:
    findings = [
        PipelineFinding(
            category="transport",
            severity="low",
            detector="transport-low",
            title="Low",
            description="x",
            confidence=1.0,
        )
    ]
    result = calculate_scores(findings, is_https=True, redirect_count=0)
    assert result.decision == "allow"
    assert result.explanation["decision_reasons"] == [
        "no warn or block threshold met"
    ]


def test_warn_reason_crossed_warn_not_block() -> None:
    findings = [
        PipelineFinding(
            category="prompt_injection",
            severity="high",
            detector="pi-high",
            title="High",
            description="x",
            confidence=1.0,
        ),
        PipelineFinding(
            category="ssrf",
            severity="high",
            detector="ssrf-high",
            title="High",
            description="x",
            confidence=1.0,
        ),
    ]
    result = calculate_scores(findings, is_https=True, redirect_count=0)
    assert result.decision == "warn"
    assert result.risk_score == 64
    assert result.explanation["decision_reasons"] == [
        "risk score 64 crossed the warn threshold 40 but not the block threshold 70"
    ]


def test_numeric_block_reason_crossed_block_threshold() -> None:
    findings = [
        PipelineFinding(
            category="prompt_injection",
            severity="high",
            detector=f"pi-{i}",
            title="High",
            description="x",
            confidence=1.0,
        )
        for i in range(3)
    ]
    result = calculate_scores(findings, is_https=True, redirect_count=0)
    assert result.decision == "block"
    assert result.risk_score == 96
    assert result.explanation["decision_reasons"] == [
        "risk score 96 crossed the block threshold 70"
    ]


def test_critical_below_block_threshold_blocks_with_only_critical_reason() -> None:
    findings = [
        PipelineFinding(
            category="prompt_injection",
            severity="critical",
            detector="pi-critical",
            title="Critical",
            description="x",
            confidence=1.0,
        )
    ]
    result = calculate_scores(findings, is_https=True, redirect_count=0)
    assert result.decision == "block"
    assert result.risk_score < 70
    assert result.explanation["decision_reasons"] == [
        "critical finding pi-critical forced the block"
    ]
