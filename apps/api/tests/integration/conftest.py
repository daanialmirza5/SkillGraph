import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Role, RoleSkill, Skill, SkillCategory  # noqa: E402
from app.models.enums import Importance  # noqa: E402


@pytest.fixture()
def client():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    session = TestingSessionLocal()
    category = SkillCategory(name="Programming")
    session.add(category)
    session.flush()
    python = Skill(name="Python", category_id=category.id)
    session.add(python)
    session.flush()
    role = Role(title="Backend Engineer", category="Software Engineering", description="Test role", level="Mid")
    session.add(role)
    session.flush()
    session.add(RoleSkill(role_id=role.id, skill_id=python.id, importance=Importance.CRITICAL, min_capability_score=50))
    session.commit()
    python_skill_id = python.id
    role_id = role.id
    session.close()

    with TestClient(app) as test_client:
        test_client.python_skill_id = python_skill_id
        test_client.role_id = role_id
        yield test_client

    app.dependency_overrides.clear()


def register_and_login(client, email="user1@example.com", password="TestPass123!") -> dict:
    client.post("/api/auth/register", json={"email": email, "password": password, "name": "Test User"})
    resp = client.post("/api/auth/login", data={"username": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
