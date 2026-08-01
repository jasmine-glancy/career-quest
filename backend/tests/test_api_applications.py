from datetime import datetime, timezone

from app.models import Application, ApplicationStatus, Company, Job, User


def _make_application(db_session, status=ApplicationStatus.SAVED, applied_at=None):
    user = User(name="Test User", email="applicant@example.com")
    db_session.add(user)
    db_session.flush()

    company = Company(name="Test Co")
    db_session.add(company)
    db_session.flush()

    job = Job(company_id=company.company_id, title="Role")
    db_session.add(job)
    db_session.flush()

    application = Application(user_id=user.user_id, job_id=job.job_id, status=status, applied_at=applied_at)
    db_session.add(application)
    db_session.commit()
    return application


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

    response = client.patch(f"/applications/{application.application_id}/status", json={"status": "interviewing"})

    assert response.status_code == 200
    assert response.json()["applied_at"] is None


def test_patch_status_unknown_application_returns_404(client):
    response = client.patch("/applications/999999/status", json={"status": "applied"})

    assert response.status_code == 404


def test_patch_status_invalid_value_returns_422(client, db_session):
    application = _make_application(db_session)

    response = client.patch(f"/applications/{application.application_id}/status", json={"status": "bogus"})

    assert response.status_code == 422
