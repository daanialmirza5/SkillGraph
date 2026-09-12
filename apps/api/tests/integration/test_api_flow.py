from datetime import date

from tests.integration.conftest import register_and_login


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_register_login_and_get_profile(client):
    headers = register_and_login(client)
    resp = client.get("/api/profile", headers=headers)
    assert resp.status_code == 200


def test_unauthenticated_request_is_rejected(client):
    resp = client.get("/api/profile")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHENTICATED"


def test_full_evidence_to_gap_flow(client):
    headers = register_and_login(client, email="flow@example.com")

    project_resp = client.post(
        "/api/projects",
        headers=headers,
        json={"name": "API Service", "description": "A backend service.", "skill_ids": [client.python_skill_id], "complexity": 4},
    )
    assert project_resp.status_code == 201
    project_id = project_resp.json()["id"]

    ev_resp = client.post(
        "/api/evidence",
        headers=headers,
        json={
            "skill_id": client.python_skill_id, "type": "PROJECT", "title": "Built an API",
            "date": date.today().isoformat(), "verification_status": "SELF_REPORTED", "complexity": 5,
            "project_id": project_id,
        },
    )
    assert ev_resp.status_code == 201

    gap_resp = client.get(f"/api/roles/{client.role_id}/fit", headers=headers)
    assert gap_resp.status_code == 200
    body = gap_resp.json()
    assert body["readiness"] > 0

    audit_resp = client.get("/api/audit", headers=headers)
    actions = [e["action"] for e in audit_resp.json()]
    assert "PROJECT_CREATED" in actions
    assert "EVIDENCE_ADDED" in actions


def test_cross_user_data_is_isolated(client):
    headers_a = register_and_login(client, email="usera@example.com")
    headers_b = register_and_login(client, email="userb@example.com")

    client.post("/api/projects", headers=headers_a, json={"name": "User A Project", "description": "desc", "skill_ids": []})

    resp_b = client.get("/api/projects", headers=headers_b)
    assert resp_b.status_code == 200
    assert resp_b.json() == []

    resp_a = client.get("/api/projects", headers=headers_a)
    assert len(resp_a.json()) == 1


def test_invalid_evidence_type_is_rejected(client):
    headers = register_and_login(client, email="badtype@example.com")
    resp = client.post(
        "/api/evidence",
        headers=headers,
        json={"skill_id": client.python_skill_id, "type": "NOT_A_REAL_TYPE", "title": "x", "date": date.today().isoformat()},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_ENUM_VALUE"


def test_ai_analyst_responds_without_api_key(client):
    headers = register_and_login(client, email="ai@example.com")
    resp = client.post("/api/ai/analyze", headers=headers, json={"question": "What are my strongest skills?", "role_id": client.role_id})
    assert resp.status_code == 200
    body = resp.json()
    assert body["provider"] == "mock"
    assert "answer" in body
