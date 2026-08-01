from app.models import Resume, ResumeVersion, User


def _make_resume(db_session):
    user = User(name="Versioned User", email="versioned@example.com")
    db_session.add(user)
    db_session.flush()

    resume = Resume(user_id=user.user_id, title="My Resume")
    db_session.add(resume)
    db_session.commit()
    return resume


def test_create_resume_version_success(client, db_session):
    resume = _make_resume(db_session)

    response = client.post(
        f"/resumes/{resume.resume_id}/versions",
        json={"snapshot_json": {"summary": "First draft"}},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["resume_id"] == resume.resume_id
    assert body["snapshot_json"] == {"summary": "First draft"}
    assert "resume_version_id" in body


def test_create_resume_version_unknown_resume_returns_404(client):
    response = client.post("/resumes/9999/versions", json={"snapshot_json": {}})

    assert response.status_code == 404


def test_list_resume_versions_returns_all_versions_in_order(client, db_session):
    resume = _make_resume(db_session)
    client.post(f"/resumes/{resume.resume_id}/versions", json={"snapshot_json": {"summary": "v1"}})
    client.post(f"/resumes/{resume.resume_id}/versions", json={"snapshot_json": {"summary": "v2"}})

    response = client.get(f"/resumes/{resume.resume_id}/versions")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert [v["snapshot_json"]["summary"] for v in body] == ["v1", "v2"]


def test_list_resume_versions_unknown_resume_returns_404(client):
    response = client.get("/resumes/9999/versions")

    assert response.status_code == 404


def test_list_resume_versions_empty_for_resume_with_none(client, db_session):
    resume = _make_resume(db_session)

    response = client.get(f"/resumes/{resume.resume_id}/versions")

    assert response.status_code == 200
    assert response.json() == []


def test_list_resume_versions_only_for_that_resume(client, db_session):
    resume_a = _make_resume(db_session)
    user_b = User(name="Other User", email="other@example.com")
    db_session.add(user_b)
    db_session.flush()
    resume_b = Resume(user_id=user_b.user_id, title="Other Resume")
    db_session.add(resume_b)
    db_session.commit()

    client.post(f"/resumes/{resume_a.resume_id}/versions", json={"snapshot_json": {"summary": "a"}})
    client.post(f"/resumes/{resume_b.resume_id}/versions", json={"snapshot_json": {"summary": "b"}})

    response = client.get(f"/resumes/{resume_a.resume_id}/versions")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["snapshot_json"]["summary"] == "a"
