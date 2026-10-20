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


def test_allow_has_no_threshold_met_reason() -> None:
    result = calculate_scores([], is_https=True, redirect_count=0)
    assert result.decision == "allow"
    reasons = result.explanation["decision_reasons"]
    assert any("no warn or block threshold was met" in r for r in reasons)


def test_critical_reason_names_detector() -> None:
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
    reasons = result.explanation["decision_reasons"]
    assert any(
        r.startswith("critical finding from detector pi-critical") for r in reasons
    )


def test_warn_reason_cites_thresholds() -> None:
    findings = [
        PipelineFinding(
            category="prompt_injection",
            severity="medium",
            detector="pi-warn",
            title="Warn",
            description="x",
            confidence=1.0,
        )
    ]
    result = calculate_scores(
        findings, is_https=True, redirect_count=0, warn_threshold=10, block_threshold=70
    )
    assert result.decision == "warn"
    assert result.risk_score == 18
    reasons = result.explanation["decision_reasons"]
    assert any(
        "meets the warn threshold (10)" in r and "not the block threshold (70)" in r
        for r in reasons
    )


def test_block_has_block_threshold_reason() -> None:
    findings = [
        PipelineFinding(
            category="prompt_injection",
            severity="high",
            detector=f"pi-high-{i}",
            title="High",
            description="x",
            confidence=1.0,
        )
        for i in range(3)
    ]
    result = calculate_scores(findings, is_https=True, redirect_count=0)
    assert result.decision == "block"
    assert result.risk_score >= 70
    reasons = result.explanation["decision_reasons"]
    assert any("meets the block threshold (70)" in r for r in reasons)
