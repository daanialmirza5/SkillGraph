import sys
from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import Base  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models import Evidence, Role, RoleSkill, Skill, SkillCategory, SkillRelationship, User, UserSkill  # noqa: E402
from app.models.enums import EvidenceType, Importance, RelationshipType, VerificationStatus  # noqa: E402


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def sample_skills(db_session):
    category = SkillCategory(name="Programming")
    db_session.add(category)
    db_session.flush()

    python = Skill(name="Python", category_id=category.id)
    docker = Skill(name="Docker", category_id=category.id)
    cicd = Skill(name="CI/CD", category_id=category.id)
    ml = Skill(name="Machine Learning", category_id=category.id)
    db_session.add_all([python, docker, cicd, ml])
    db_session.flush()

    db_session.add(SkillRelationship(from_skill_id=docker.id, to_skill_id=cicd.id, relationship_type=RelationshipType.PREREQUISITE_OF))
    db_session.commit()

    return {"python": python, "docker": docker, "cicd": cicd, "ml": ml}


@pytest.fixture()
def sample_user(db_session):
    user = User(email="test@example.com", name="Test User", hashed_password=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture()
def sample_role(db_session, sample_skills):
    role = Role(title="Test ML Engineer", category="AI/ML", description="Test role", level="Mid")
    db_session.add(role)
    db_session.flush()
    db_session.add_all([
        RoleSkill(role_id=role.id, skill_id=sample_skills["python"].id, importance=Importance.CRITICAL, min_capability_score=50),
        RoleSkill(role_id=role.id, skill_id=sample_skills["ml"].id, importance=Importance.CRITICAL, min_capability_score=50),
        RoleSkill(role_id=role.id, skill_id=sample_skills["docker"].id, importance=Importance.MEDIUM, min_capability_score=30),
    ])
    db_session.commit()
    return role


def add_claimed_skill(db_session, user, skill, claimed=True):
    db_session.add(UserSkill(user_id=user.id, skill_id=skill.id, claimed=claimed))
    db_session.commit()


def add_evidence(db_session, user, skill, ev_type=EvidenceType.PROJECT, complexity=4, verification=VerificationStatus.SELF_REPORTED, ev_date=None):
    ev = Evidence(
        user_id=user.id, skill_id=skill.id, type=ev_type, title=f"Evidence for {skill.name}",
        date=ev_date or date.today(), verification_status=verification, complexity=complexity,
    )
    db_session.add(ev)
    db_session.commit()
    return ev
