from app.models import User


def test_create_resume_success(client, db_session):
    user = User(name="Grace Hopper", email="grace@example.com")
    db_session.add(user)
    db_session.commit()

    response = client.post("/resumes", json={"user_id": user.user_id, "title": "Compiler Resume"})

    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] == user.user_id
    assert body["title"] == "Compiler Resume"
    assert "resume_id" in body


def test_create_resume_unknown_user_returns_404(client):
    response = client.post("/resumes", json={"user_id": 9999, "title": "Ghost Resume"})

    assert response.status_code == 404


def test_list_resumes_returns_only_that_users_resumes(client, db_session):
    user_a = User(name="User A", email="a@example.com")
    user_b = User(name="User B", email="b@example.com")
    db_session.add_all([user_a, user_b])
    db_session.commit()

    client.post("/resumes", json={"user_id": user_a.user_id, "title": "A Resume 1"})
    client.post("/resumes", json={"user_id": user_a.user_id, "title": "A Resume 2"})
    client.post("/resumes", json={"user_id": user_b.user_id, "title": "B Resume"})

    response = client.get(f"/resumes?user_id={user_a.user_id}")

    assert response.status_code == 200
    titles = {r["title"] for r in response.json()}
    assert titles == {"A Resume 1", "A Resume 2"}


def test_list_resumes_missing_user_id_returns_422(client):
    response = client.get("/resumes")

    assert response.status_code == 422


def test_list_resumes_empty_for_user_with_none(client, db_session):
    user = User(name="Lonely User", email="lonely@example.com")
    db_session.add(user)
    db_session.commit()

    response = client.get(f"/resumes?user_id={user.user_id}")

    assert response.status_code == 200
    assert response.json() == []
