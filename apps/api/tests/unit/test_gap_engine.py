from app.engines.gap_engine import classify, compute_role_gap
from app.models.enums import MatchLevel, VerificationStatus
from tests.conftest import add_claimed_skill, add_evidence


def test_classify_bands():
    assert classify(0, has_evidence=False) == MatchLevel.MISSING
    assert classify(10, has_evidence=True) == MatchLevel.MISSING  # below WEAK_THRESHOLD even with evidence
    assert classify(20, has_evidence=True) == MatchLevel.WEAK_MATCH
    assert classify(50, has_evidence=True) == MatchLevel.PARTIAL_MATCH
    assert classify(80, has_evidence=True) == MatchLevel.STRONG_MATCH
    # Claiming a skill with a nonzero "score" but literally no evidence record must still be MISSING.
    assert classify(80, has_evidence=False) == MatchLevel.MISSING


def test_role_not_found_returns_none(db_session, sample_user):
    result = compute_role_gap(db_session, sample_user.id, role_id=9999)
    assert result is None


def test_no_evidence_yields_zero_readiness(db_session, sample_user, sample_role, sample_skills):
    result = compute_role_gap(db_session, sample_user.id, sample_role.id)
    assert result.readiness == 0.0
    assert len(result.missing) == 3


def test_strong_evidence_raises_readiness_and_classifies_strong(db_session, sample_user, sample_role, sample_skills):
    add_claimed_skill(db_session, sample_user, sample_skills["python"])
    for _ in range(4):
        add_evidence(db_session, sample_user, sample_skills["python"], complexity=5, verification=VerificationStatus.VERIFIED)

    result = compute_role_gap(db_session, sample_user.id, sample_role.id)
    python_gap = next(g for g in result.gaps if g.skill.name == "Python")
    assert python_gap.match == MatchLevel.STRONG_MATCH
    assert result.readiness > 0.0


def test_critical_skills_are_weighted_more_than_medium(db_session, sample_user, sample_role, sample_skills):
    # Cover only the CRITICAL skills strongly; MEDIUM (Docker) stays missing.
    add_claimed_skill(db_session, sample_user, sample_skills["python"])
    add_claimed_skill(db_session, sample_user, sample_skills["ml"])
    for skill_key in ("python", "ml"):
        for _ in range(4):
            add_evidence(db_session, sample_user, sample_skills[skill_key], complexity=5, verification=VerificationStatus.VERIFIED)

    result = compute_role_gap(db_session, sample_user.id, sample_role.id)
    # Both CRITICAL (weight 4) skills strong while the MEDIUM (weight 2) skill stays fully missing
    # should still yield well over half of the total weighted coverage.
    assert result.readiness > 55.0


def test_evidence_gap_detected_when_claimed_but_unsupported(db_session, sample_user, sample_role, sample_skills):
    add_claimed_skill(db_session, sample_user, sample_skills["docker"])
    result = compute_role_gap(db_session, sample_user.id, sample_role.id)
    docker_gap = next(g for g in result.gaps if g.skill.name == "Docker")
    assert docker_gap.is_evidence_gap is True
    assert docker_gap.match == MatchLevel.MISSING


def test_gaps_sorted_by_priority_descending(db_session, sample_user, sample_role, sample_skills):
    result = compute_role_gap(db_session, sample_user.id, sample_role.id)
    priorities = [g.priority_score for g in result.gaps]
    assert priorities == sorted(priorities, reverse=True)
