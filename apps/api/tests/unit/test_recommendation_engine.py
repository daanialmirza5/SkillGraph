from app.engines.recommendation_engine import recommend_project_for_role
from app.models.enums import VerificationStatus
from tests.conftest import add_claimed_skill, add_evidence


def test_no_gaps_yields_no_recommendation(db_session, sample_user, sample_role, sample_skills):
    for key in ("python", "ml", "docker"):
        add_claimed_skill(db_session, sample_user, sample_skills[key])
        for _ in range(4):
            add_evidence(db_session, sample_user, sample_skills[key], complexity=5, verification=VerificationStatus.VERIFIED)

    recs = recommend_project_for_role(db_session, sample_user.id, sample_role.id)
    assert recs == []


def test_recommendation_targets_missing_skills(db_session, sample_user, sample_role, sample_skills):
    # Python and ML strong, Docker missing -- Docker should show up in a recommendation if any template covers it.
    add_claimed_skill(db_session, sample_user, sample_skills["python"])
    add_claimed_skill(db_session, sample_user, sample_skills["ml"])
    for _ in range(3):
        add_evidence(db_session, sample_user, sample_skills["python"], complexity=5)
        add_evidence(db_session, sample_user, sample_skills["ml"], complexity=5)

    recs = recommend_project_for_role(db_session, sample_user.id, sample_role.id, top_n=3)
    assert len(recs) > 0
    assert any("Docker" in rec.closes_gap_skill_names for rec in recs)


def test_recommendation_role_not_found_returns_empty(db_session, sample_user):
    recs = recommend_project_for_role(db_session, sample_user.id, role_id=9999)
    assert recs == []
