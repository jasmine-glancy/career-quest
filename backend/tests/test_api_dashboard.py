from app.models import AIAnalysis, Application, ApplicationStatus, Company, Job, User


def _make_user(db_session, name="Test User", email="applicant@example.com"):
    user = User(name=name, email=email)
    db_session.add(user)
    db_session.flush()
    return user


def _make_application(db_session, user, title="Role"):
    company = Company(name=f"{title} Co")
    db_session.add(company)
    db_session.flush()
    job = Job(company_id=company.company_id, title=title)
    db_session.add(job)
    db_session.flush()
    application = Application(user_id=user.user_id, job_id=job.job_id, status=ApplicationStatus.SAVED)
    db_session.add(application)
    db_session.flush()
    return application


def _add_analysis(db_session, application, matched=None, missing=None, match_score=75):
    analysis = AIAnalysis(
        application_id=application.application_id,
        match_score=match_score,
        strengths_json=[],
        gaps_json=[],
        recommendations_json=[],
        matched_skills_json=matched or [],
        missing_skills_json=missing or [],
    )
    db_session.add(analysis)
    db_session.commit()
    return analysis


def test_dashboard_empty_state_for_user_with_no_applications(client, db_session):
    user = _make_user(db_session)
    db_session.commit()

    response = client.get(f"/dashboard?user_id={user.user_id}")

    assert response.status_code == 200
    body = response.json()
    assert body == {"total_analyzed": 0, "strongest_skill": None, "biggest_gap": None}


def test_dashboard_empty_state_for_application_without_analysis(client, db_session):
    user = _make_user(db_session)
    _make_application(db_session, user)
    db_session.commit()

    response = client.get(f"/dashboard?user_id={user.user_id}")

    assert response.status_code == 200
    body = response.json()
    assert body == {"total_analyzed": 0, "strongest_skill": None, "biggest_gap": None}


def test_dashboard_single_analysis(client, db_session):
    user = _make_user(db_session)
    application = _make_application(db_session, user)
    _add_analysis(db_session, application, matched=["SQL", "Python"], missing=["AWS"])

    response = client.get(f"/dashboard?user_id={user.user_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["total_analyzed"] == 1
    assert body["strongest_skill"]["skill"] in {"SQL", "Python"}
    assert body["strongest_skill"]["count"] == 1
    assert body["strongest_skill"]["total_analyzed"] == 1
    assert body["biggest_gap"] == {"skill": "AWS", "count": 1, "total_analyzed": 1}


def test_dashboard_picks_the_most_common_skill_across_applications(client, db_session):
    user = _make_user(db_session)
    app_a = _make_application(db_session, user, title="Role A")
    app_b = _make_application(db_session, user, title="Role B")
    app_c = _make_application(db_session, user, title="Role C")
    _add_analysis(db_session, app_a, matched=["SQL"], missing=["AWS"])
    _add_analysis(db_session, app_b, matched=["SQL", "Python"], missing=["AWS"])
    _add_analysis(db_session, app_c, matched=["Python"], missing=["Kubernetes"])

    response = client.get(f"/dashboard?user_id={user.user_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["total_analyzed"] == 3
    assert body["strongest_skill"] == {"skill": "SQL", "count": 2, "total_analyzed": 3}
    assert body["biggest_gap"] == {"skill": "AWS", "count": 2, "total_analyzed": 3}


def test_dashboard_skill_repeated_within_one_analysis_counts_once(client, db_session):
    user = _make_user(db_session)
    application = _make_application(db_session, user)
    # A malformed/duplicated LLM response shouldn't inflate a single analysis's weight.
    _add_analysis(db_session, application, matched=["SQL", "SQL"], missing=[])

    response = client.get(f"/dashboard?user_id={user.user_id}")

    assert response.status_code == 200
    assert response.json()["strongest_skill"] == {"skill": "SQL", "count": 1, "total_analyzed": 1}


def test_dashboard_only_counts_latest_analysis_per_application(client, db_session):
    user = _make_user(db_session)
    application = _make_application(db_session, user)
    _add_analysis(db_session, application, matched=["SQL"], missing=["AWS"])
    # A re-run with a different result should replace, not add to, the first one.
    _add_analysis(db_session, application, matched=["Python"], missing=["Kubernetes"])

    response = client.get(f"/dashboard?user_id={user.user_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["total_analyzed"] == 1
    assert body["strongest_skill"] == {"skill": "Python", "count": 1, "total_analyzed": 1}
    assert body["biggest_gap"] == {"skill": "Kubernetes", "count": 1, "total_analyzed": 1}


def test_dashboard_unknown_user_returns_404(client):
    response = client.get("/dashboard?user_id=999999")

    assert response.status_code == 404
