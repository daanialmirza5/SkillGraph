from datetime import date, timedelta

from app.engines.capability_scoring import (
    EvidenceInput,
    compute_capability,
    confidence_for,
    level_for_score,
    recency_multiplier,
)
from app.models.enums import CapabilityLevel, ConfidenceLevel, EvidenceType, VerificationStatus


def test_no_evidence_yields_zero_foundational():
    result = compute_capability([])
    assert result.score == 0.0
    assert result.level == CapabilityLevel.FOUNDATIONAL
    assert result.confidence == ConfidenceLevel.LOW


def test_recency_multiplier_decays_with_age():
    today = date(2026, 1, 1)
    recent = recency_multiplier(today - timedelta(days=30), as_of=today)
    old = recency_multiplier(today - timedelta(days=800), as_of=today)
    assert recent == 1.0
    assert old < recent


def test_work_experience_scores_higher_than_course_for_equal_complexity():
    today = date.today()
    work = EvidenceInput(type=EvidenceType.WORK_EXPERIENCE, date=today, complexity=3, verification_status=VerificationStatus.SELF_REPORTED)
    course = EvidenceInput(type=EvidenceType.COURSE, date=today, complexity=3, verification_status=VerificationStatus.SELF_REPORTED)
    work_result = compute_capability([work])
    course_result = compute_capability([course])
    assert work_result.score > course_result.score


def test_verified_scores_higher_than_unverified():
    today = date.today()
    verified = EvidenceInput(type=EvidenceType.PROJECT, date=today, complexity=3, verification_status=VerificationStatus.VERIFIED)
    unverified = EvidenceInput(type=EvidenceType.PROJECT, date=today, complexity=3, verification_status=VerificationStatus.UNVERIFIED)
    assert compute_capability([verified]).score > compute_capability([unverified]).score


def test_more_evidence_increases_score_but_with_diminishing_returns():
    today = date.today()
    one_item = [EvidenceInput(type=EvidenceType.PROJECT, date=today, complexity=4, verification_status=VerificationStatus.SELF_REPORTED)]
    two_items = one_item + [EvidenceInput(type=EvidenceType.PROJECT, date=today, complexity=4, verification_status=VerificationStatus.SELF_REPORTED)]

    score_one = compute_capability(one_item).score
    score_two = compute_capability(two_items).score
    marginal_gain = score_two - score_one

    assert score_two > score_one
    # The second identical item must contribute less than the first (diminishing returns),
    # so the marginal gain is smaller than the first item's own score.
    assert marginal_gain < score_one


def test_score_is_capped_at_100():
    today = date.today()
    many_items = [
        EvidenceInput(type=EvidenceType.WORK_EXPERIENCE, date=today, complexity=5, verification_status=VerificationStatus.VERIFIED)
        for _ in range(20)
    ]
    result = compute_capability(many_items)
    assert result.score <= 100.0


def test_level_bands_are_ordered_correctly():
    assert level_for_score(90) == CapabilityLevel.EXPERT_LIKE
    assert level_for_score(70) == CapabilityLevel.STRONG
    assert level_for_score(50) == CapabilityLevel.PRACTICAL
    assert level_for_score(25) == CapabilityLevel.DEVELOPING
    assert level_for_score(5) == CapabilityLevel.FOUNDATIONAL


def test_confidence_requires_multiple_or_verified_evidence():
    today = date.today()
    single_unverified = [EvidenceInput(type=EvidenceType.COURSE, date=today, complexity=2, verification_status=VerificationStatus.UNVERIFIED)]
    assert confidence_for(single_unverified) == ConfidenceLevel.LOW

    single_verified = [EvidenceInput(type=EvidenceType.PROJECT, date=today, complexity=3, verification_status=VerificationStatus.VERIFIED)]
    assert confidence_for(single_verified) == ConfidenceLevel.MEDIUM

    three_with_one_verified = single_verified + [
        EvidenceInput(type=EvidenceType.COURSE, date=today, complexity=2, verification_status=VerificationStatus.SELF_REPORTED),
        EvidenceInput(type=EvidenceType.COURSE, date=today, complexity=2, verification_status=VerificationStatus.SELF_REPORTED),
    ]
    assert confidence_for(three_with_one_verified) == ConfidenceLevel.HIGH
