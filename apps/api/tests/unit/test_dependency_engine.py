from app.engines.dependency_engine import get_dependency_chain_for_target
from app.models.enums import RelationshipType
from app.models import SkillRelationship


def test_direct_prerequisite_chain(db_session, sample_skills):
    chain = get_dependency_chain_for_target(db_session, sample_skills["cicd"].id)
    names = [s.name for s in chain]
    assert names == ["Docker", "CI/CD"]


def test_no_prerequisites_returns_only_target(db_session, sample_skills):
    chain = get_dependency_chain_for_target(db_session, sample_skills["python"].id)
    assert [s.name for s in chain] == ["Python"]


def test_multi_hop_chain_is_ordered_furthest_first(db_session, sample_skills):
    # Add: Python -> Docker -> CI/CD (extending the existing Docker -> CI/CD edge)
    db_session.add(SkillRelationship(from_skill_id=sample_skills["python"].id, to_skill_id=sample_skills["docker"].id, relationship_type=RelationshipType.PREREQUISITE_OF))
    db_session.commit()

    chain = get_dependency_chain_for_target(db_session, sample_skills["cicd"].id)
    names = [s.name for s in chain]
    assert names.index("Python") < names.index("Docker") < names.index("CI/CD")
