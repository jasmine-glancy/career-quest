import app.routers.ai as ai_router
from app.models import AIAnalysis, Application, ApplicationStatus, Company, Job, Resume, ResumeVersion, User
from app.schemas.ai_analysis import JobFitAnalysisResult, OptimizeResumeResponse
from app.services.ai_analysis import AIServiceError

ANALYSIS_RESULT = JobFitAnalysisResult(
    match_score=82,
    strengths=["Strong SQL"],
    gaps=["No AWS"],
    recommendations=["Add AWS"],
    matched_skills=["SQL"],
    missing_skills=["AWS"],
)

OPTIMIZE_RESULT = OptimizeResumeResponse(
    summary="Solid overall fit.",
    suggested_edits=[{"section": "Experience", "suggestion": "Add metrics."}],
    missing_keywords=["dbt"],
)


def _make_user_and_job(db_session, user_name="Test User", user_email="applicant@example.com"):
    user = User(name=user_name, email=user_email)
    db_session.add(user)
    db_session.flush()

    company = Company(name="Test Co")
    db_session.add(company)
    db_session.flush()

    job = Job(company_id=company.company_id, title="Role", description="Do things")
    db_session.add(job)
    db_session.flush()

    return user, job


def _make_resume_version(db_session, user, snapshot=None):
    resume = Resume(user_id=user.user_id, title="My Resume")
    db_session.add(resume)
    db_session.flush()
    version = ResumeVersion(resume_id=resume.resume_id, snapshot_json=snapshot or {"summary": "..."})
    db_session.add(version)
    db_session.commit()
    return version


# --- POST /ai/analyze-fit ---


def test_analyze_fit_creates_application_when_none_exists(client, db_session, monkeypatch):
    monkeypatch.setattr(ai_router, "generate_job_fit_analysis", lambda *a, **k: ANALYSIS_RESULT)
    user, job = _make_user_and_job(db_session)
    version = _make_resume_version(db_session, user)

    response = client.post(
        "/ai/analyze-fit",
        json={"user_id": user.user_id, "job_id": job.job_id, "resume_version_id": version.resume_version_id},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["match_score"] == 82
    assert body["strengths_json"] == ["Strong SQL"]
    assert body["gaps_json"] == ["No AWS"]
    assert body["recommendations_json"] == ["Add AWS"]
    assert body["matched_skills_json"] == ["SQL"]
    assert body["missing_skills_json"] == ["AWS"]

    application = db_session.query(Application).filter(Application.user_id == user.user_id).one()
    assert application.job_id == job.job_id
    assert application.resume_version_id == version.resume_version_id
    assert application.status == ApplicationStatus.SAVED
    assert application.application_id == body["application_id"]


def test_analyze_fit_reuses_and_updates_existing_application(client, db_session, monkeypatch):
    monkeypatch.setattr(ai_router, "generate_job_fit_analysis", lambda *a, **k: ANALYSIS_RESULT)
    user, job = _make_user_and_job(db_session)
    version = _make_resume_version(db_session, user)
    application = Application(user_id=user.user_id, job_id=job.job_id, status=ApplicationStatus.APPLIED)
    db_session.add(application)
    db_session.commit()
    application_id = application.application_id

    response = client.post(
        "/ai/analyze-fit",
        json={"user_id": user.user_id, "job_id": job.job_id, "resume_version_id": version.resume_version_id},
    )

    assert response.status_code == 201
    assert response.json()["application_id"] == application_id
    assert db_session.query(Application).filter(Application.user_id == user.user_id).count() == 1

    db_session.refresh(application)
    assert application.resume_version_id == version.resume_version_id
    assert application.status == ApplicationStatus.APPLIED


def test_analyze_fit_unknown_user_returns_404(client, db_session):
    _, job = _make_user_and_job(db_session)
    db_session.commit()

    response = client.post("/ai/analyze-fit", json={"user_id": 9999, "job_id": job.job_id, "resume_version_id": 1})

    assert response.status_code == 404


def test_analyze_fit_unknown_job_returns_404(client, db_session):
    user, _ = _make_user_and_job(db_session)
    db_session.commit()

    response = client.post(
        "/ai/analyze-fit", json={"user_id": user.user_id, "job_id": 9999, "resume_version_id": 1}
    )

    assert response.status_code == 404


def test_analyze_fit_unknown_resume_version_returns_404(client, db_session):
    user, job = _make_user_and_job(db_session)
    db_session.commit()

    response = client.post(
        "/ai/analyze-fit", json={"user_id": user.user_id, "job_id": job.job_id, "resume_version_id": 9999}
    )

    assert response.status_code == 404


def test_analyze_fit_resume_version_from_different_user_returns_400(client, db_session):
    owner, job = _make_user_and_job(db_session, user_name="Owner", user_email="owner@example.com")
    other_user = User(name="Other", email="other@example.com")
    db_session.add(other_user)
    db_session.commit()
    version = _make_resume_version(db_session, owner)

    response = client.post(
        "/ai/analyze-fit",
        json={
            "user_id": other_user.user_id,
            "job_id": job.job_id,
            "resume_version_id": version.resume_version_id,
        },
    )

    assert response.status_code == 400


def test_analyze_fit_returns_502_when_ai_service_fails(client, db_session, monkeypatch):
    def _boom(*args, **kwargs):
        raise AIServiceError("OpenAI request failed")

    monkeypatch.setattr(ai_router, "generate_job_fit_analysis", _boom)
    user, job = _make_user_and_job(db_session)
    version = _make_resume_version(db_session, user)

    response = client.post(
        "/ai/analyze-fit",
        json={"user_id": user.user_id, "job_id": job.job_id, "resume_version_id": version.resume_version_id},
    )

    assert response.status_code == 502
    # tracking still persists even though the analysis call failed
    assert db_session.query(Application).filter(Application.user_id == user.user_id).count() == 1
    assert db_session.query(AIAnalysis).count() == 0


def test_analyze_fit_rerun_keeps_analysis_history(client, db_session, monkeypatch):
    monkeypatch.setattr(ai_router, "generate_job_fit_analysis", lambda *a, **k: ANALYSIS_RESULT)
    user, job = _make_user_and_job(db_session)
    version = _make_resume_version(db_session, user)
    payload = {"user_id": user.user_id, "job_id": job.job_id, "resume_version_id": version.resume_version_id}

    client.post("/ai/analyze-fit", json=payload)
    client.post("/ai/analyze-fit", json=payload)

    assert db_session.query(AIAnalysis).count() == 2


# --- POST /ai/optimize-resume ---


def test_optimize_resume_success(client, db_session, monkeypatch):
    monkeypatch.setattr(ai_router, "generate_resume_optimization", lambda *a, **k: OPTIMIZE_RESULT)
    user, job = _make_user_and_job(db_session)
    version = _make_resume_version(db_session, user)

    response = client.post(
        "/ai/optimize-resume",
        json={"user_id": user.user_id, "resume_version_id": version.resume_version_id, "job_id": job.job_id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "Solid overall fit."
    assert body["suggested_edits"] == [{"section": "Experience", "suggestion": "Add metrics."}]
    assert body["missing_keywords"] == ["dbt"]


def test_optimize_resume_unknown_user_returns_404(client, db_session):
    user, job = _make_user_and_job(db_session)
    version = _make_resume_version(db_session, user)

    response = client.post(
        "/ai/optimize-resume",
        json={"user_id": 9999, "resume_version_id": version.resume_version_id, "job_id": job.job_id},
    )

    assert response.status_code == 404


def test_optimize_resume_unknown_resume_version_returns_404(client, db_session):
    user, job = _make_user_and_job(db_session)
    db_session.commit()

    response = client.post(
        "/ai/optimize-resume", json={"user_id": user.user_id, "resume_version_id": 9999, "job_id": job.job_id}
    )

    assert response.status_code == 404


def test_optimize_resume_unknown_job_returns_404(client, db_session):
    user, _ = _make_user_and_job(db_session)
    version = _make_resume_version(db_session, user)

    response = client.post(
        "/ai/optimize-resume",
        json={"user_id": user.user_id, "resume_version_id": version.resume_version_id, "job_id": 9999},
    )

    assert response.status_code == 404


def test_optimize_resume_resume_version_from_different_user_returns_400(client, db_session):
    owner, job = _make_user_and_job(db_session, user_name="Owner", user_email="owner@example.com")
    other_user = User(name="Other", email="other@example.com")
    db_session.add(other_user)
    db_session.commit()
    version = _make_resume_version(db_session, owner)

    response = client.post(
        "/ai/optimize-resume",
        json={
            "user_id": other_user.user_id,
            "resume_version_id": version.resume_version_id,
            "job_id": job.job_id,
        },
    )

    assert response.status_code == 400


def test_optimize_resume_returns_502_when_ai_service_fails(client, db_session, monkeypatch):
    def _boom(*args, **kwargs):
        raise AIServiceError("OpenAI request failed")

    monkeypatch.setattr(ai_router, "generate_resume_optimization", _boom)
    user, job = _make_user_and_job(db_session)
    version = _make_resume_version(db_session, user)

    response = client.post(
        "/ai/optimize-resume",
        json={"user_id": user.user_id, "resume_version_id": version.resume_version_id, "job_id": job.job_id},
    )

    assert response.status_code == 502


def test_analyze_fit_reuses_earliest_application_when_duplicates_exist(client, db_session, monkeypatch):
    # POST /applications has no uniqueness constraint on (user_id, job_id), so a user
    # can legitimately end up tracking the same job twice. The get-or-create lookup
    # in analyze_fit must not crash (MultipleResultsFound) when that happens.
    monkeypatch.setattr(ai_router, "generate_job_fit_analysis", lambda *a, **k: ANALYSIS_RESULT)
    user, job = _make_user_and_job(db_session)
    version = _make_resume_version(db_session, user)
    first = Application(user_id=user.user_id, job_id=job.job_id, status=ApplicationStatus.SAVED)
    db_session.add(first)
    db_session.commit()
    second = Application(user_id=user.user_id, job_id=job.job_id, status=ApplicationStatus.SAVED)
    db_session.add(second)
    db_session.commit()

    response = client.post(
        "/ai/analyze-fit",
        json={"user_id": user.user_id, "job_id": job.job_id, "resume_version_id": version.resume_version_id},
    )

    assert response.status_code == 201
    assert response.json()["application_id"] == first.application_id
