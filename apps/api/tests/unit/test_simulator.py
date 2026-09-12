from app.engines.simulator import HypotheticalEvidence, simulate_role_readiness
from app.models import Evidence
from app.models.enums import EvidenceType, VerificationStatus


def test_simulation_does_not_persist_evidence(db_session, sample_user, sample_role, sample_skills):
    before_count = db_session.query(Evidence).count()

    hypothetical = [HypotheticalEvidence(skill_id=sample_skills["docker"].id, type=EvidenceType.PROJECT, complexity=5, verification_status=VerificationStatus.VERIFIED)]
    simulate_role_readiness(db_session, sample_user.id, sample_role.id, hypothetical)

    after_count = db_session.query(Evidence).count()
    assert before_count == after_count


def test_simulation_increases_readiness_for_covered_gap(db_session, sample_user, sample_role, sample_skills):
    before = simulate_role_readiness(db_session, sample_user.id, sample_role.id, [])
    hypothetical = [HypotheticalEvidence(skill_id=sample_skills["docker"].id, type=EvidenceType.PROJECT, complexity=5, verification_status=VerificationStatus.VERIFIED)]
    after = simulate_role_readiness(db_session, sample_user.id, sample_role.id, hypothetical)

    assert after.after_readiness > before.before_readiness
    assert after.delta > 0


def test_simulation_role_not_found(db_session, sample_user):
    result = simulate_role_readiness(db_session, sample_user.id, 9999, [])
    assert result is None
