from datetime import datetime, timezone

from app.models import AIAnalysis, Application, ApplicationStatus, Company, Job, Resume, ResumeVersion, User


def _make_user_and_job(db_session, user_name="Test User", user_email="applicant@example.com"):
    user = User(name=user_name, email=user_email)
    db_session.add(user)
    db_session.flush()

    company = Company(name="Test Co")
    db_session.add(company)
    db_session.flush()

    job = Job(company_id=company.company_id, title="Role")
    db_session.add(job)
    db_session.flush()

    return user, job


def _make_application(db_session, status=ApplicationStatus.SAVED, applied_at=None):
    user, job = _make_user_and_job(db_session)

    application = Application(user_id=user.user_id, job_id=job.job_id, status=status, applied_at=applied_at)
    db_session.add(application)
    db_session.commit()
    return application


# --- POST /applications ---


def test_create_application_success(client, db_session):
    user, job = _make_user_and_job(db_session)
    db_session.commit()

    response = client.post("/applications", json={"user_id": user.user_id, "job_id": job.job_id})

    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] == user.user_id
    assert body["job_id"] == job.job_id
    assert body["status"] == "saved"
    assert body["applied_at"] is None


def test_create_application_unknown_user_returns_404(client, db_session):
    _, job = _make_user_and_job(db_session)
    db_session.commit()

    response = client.post("/applications", json={"user_id": 9999, "job_id": job.job_id})

    assert response.status_code == 404


def test_create_application_unknown_job_returns_404(client, db_session):
    user, _ = _make_user_and_job(db_session)
    db_session.commit()

    response = client.post("/applications", json={"user_id": user.user_id, "job_id": 9999})

    assert response.status_code == 404


def test_create_application_unknown_resume_version_returns_404(client, db_session):
    user, job = _make_user_and_job(db_session)
    db_session.commit()

    response = client.post(
        "/applications", json={"user_id": user.user_id, "job_id": job.job_id, "resume_version_id": 9999}
    )

    assert response.status_code == 404


def test_create_application_resume_version_from_different_user_returns_400(client, db_session):
    owner, job = _make_user_and_job(db_session, user_name="Owner", user_email="owner@example.com")
    other_user = User(name="Other", email="other@example.com")
    db_session.add(other_user)
    db_session.flush()

    resume = Resume(user_id=owner.user_id, title="Owner's Resume")
    db_session.add(resume)
    db_session.flush()
    resume_version = ResumeVersion(resume_id=resume.resume_id, snapshot_json={"summary": "..."})
    db_session.add(resume_version)
    db_session.commit()

    response = client.post(
        "/applications",
        json={"user_id": other_user.user_id, "job_id": job.job_id, "resume_version_id": resume_version.resume_version_id},
    )

    assert response.status_code == 400


def test_create_application_with_own_resume_version_succeeds(client, db_session):
    user, job = _make_user_and_job(db_session)
    resume = Resume(user_id=user.user_id, title="My Resume")
    db_session.add(resume)
    db_session.flush()
    resume_version = ResumeVersion(resume_id=resume.resume_id, snapshot_json={"summary": "..."})
    db_session.add(resume_version)
    db_session.commit()

    response = client.post(
        "/applications",
        json={"user_id": user.user_id, "job_id": job.job_id, "resume_version_id": resume_version.resume_version_id},
    )

    assert response.status_code == 201
    assert response.json()["resume_version_id"] == resume_version.resume_version_id


# --- GET /applications ---


def test_list_applications_returns_job_and_company_info(client, db_session):
    user, job = _make_user_and_job(db_session)
    db_session.commit()
    client.post("/applications", json={"user_id": user.user_id, "job_id": job.job_id})

    response = client.get(f"/applications?user_id={user.user_id}")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["job_title"] == "Role"
    assert body[0]["company_name"] == "Test Co"
    assert body[0]["status"] == "saved"


def test_list_applications_only_for_that_user(client, db_session):
    user_a, job = _make_user_and_job(db_session, user_name="User A", user_email="a@example.com")
    user_b = User(name="User B", email="b@example.com")
    db_session.add(user_b)
    db_session.commit()

    client.post("/applications", json={"user_id": user_a.user_id, "job_id": job.job_id})
    client.post("/applications", json={"user_id": user_b.user_id, "job_id": job.job_id})

    response = client.get(f"/applications?user_id={user_a.user_id}")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_applications_missing_user_id_returns_422(client):
    response = client.get("/applications")

    assert response.status_code == 422


# --- PATCH /applications/{id}/status ---


def test_patch_status_to_applied_sets_applied_at(client, db_session):
    application = _make_application(db_session, status=ApplicationStatus.SAVED)

    response = client.patch(f"/applications/{application.application_id}/status", json={"status": "applied"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "applied"
    assert body["applied_at"] is not None


def test_patch_status_does_not_overwrite_existing_applied_at(client, db_session):
    original_applied_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    application = _make_application(db_session, status=ApplicationStatus.APPLIED, applied_at=original_applied_at)

    response = client.patch(f"/applications/{application.application_id}/status", json={"status": "interviewing"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "interviewing"
    assert body["applied_at"].startswith("2026-01-01")


def test_patch_status_non_applied_transition_leaves_applied_at_null(client, db_session):
    application = _make_application(db_session, status=ApplicationStatus.SAVED)

    response = client.patch(f"/applications/{application.application_id}/status", json={"status": "rejected"})

    assert response.status_code == 200
    assert response.json()["applied_at"] is None


def test_patch_status_unknown_application_returns_404(client):
    response = client.patch("/applications/999999/status", json={"status": "applied"})

    assert response.status_code == 404


def test_patch_status_invalid_value_returns_422(client, db_session):
    application = _make_application(db_session)

    response = client.patch(f"/applications/{application.application_id}/status", json={"status": "bogus"})

    assert response.status_code == 422


def test_patch_status_illegal_skip_returns_409(client, db_session):
    application = _make_application(db_session, status=ApplicationStatus.APPLIED)

    response = client.patch(f"/applications/{application.application_id}/status", json={"status": "offer"})

    assert response.status_code == 409
    assert response.json()["detail"] == "Cannot transition application from 'applied' to 'offer'"


def test_patch_status_terminal_state_rejects_further_transitions(client, db_session):
    application = _make_application(db_session, status=ApplicationStatus.OFFER)

    response = client.patch(f"/applications/{application.application_id}/status", json={"status": "rejected"})

    assert response.status_code == 409


def test_patch_status_no_op_same_status_succeeds(client, db_session):
    application = _make_application(db_session, status=ApplicationStatus.OFFER)

    response = client.patch(f"/applications/{application.application_id}/status", json={"status": "offer"})

    assert response.status_code == 200
    assert response.json()["status"] == "offer"


def test_patch_status_full_valid_pipeline_walk(client, db_session):
    application = _make_application(db_session, status=ApplicationStatus.SAVED)
    app_id = application.application_id

    for status in ["applied", "interviewing", "offer"]:
        response = client.patch(f"/applications/{app_id}/status", json={"status": status})
        assert response.status_code == 200, response.json()
        assert response.json()["status"] == status


# --- GET /applications/{id}/analysis ---


def test_get_latest_analysis_returns_most_recent(client, db_session):
    application = _make_application(db_session)
    older = AIAnalysis(
        application_id=application.application_id,
        match_score=50,
        strengths_json=["a"],
        gaps_json=["b"],
        recommendations_json=["c"],
    )
    db_session.add(older)
    db_session.commit()
    newer = AIAnalysis(
        application_id=application.application_id,
        match_score=90,
        strengths_json=["x"],
        gaps_json=["y"],
        recommendations_json=["z"],
    )
    db_session.add(newer)
    db_session.commit()

    response = client.get(f"/applications/{application.application_id}/analysis")

    assert response.status_code == 200
    body = response.json()
    assert body["analysis_id"] == newer.analysis_id
    assert body["match_score"] == 90


def test_get_latest_analysis_404_when_none_exists(client, db_session):
    application = _make_application(db_session)

    response = client.get(f"/applications/{application.application_id}/analysis")

    assert response.status_code == 404


def test_get_latest_analysis_404_when_application_missing(client):
    response = client.get("/applications/999999/analysis")

    assert response.status_code == 404
