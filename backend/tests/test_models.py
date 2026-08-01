import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.models import (
    Application,
    ApplicationStatus,
    Company,
    Job,
    Note,
    Resume,
    ResumeVersion,
    Skill,
    User,
)


def _make_full_chain(db_session):
    user = User(name="Ada Lovelace", email="ada@example.com")
    db_session.add(user)
    db_session.flush()

    company = Company(name="Analytical Engines Inc")
    db_session.add(company)
    db_session.flush()

    job = Job(company_id=company.company_id, title="Mathematician", location="London")
    db_session.add(job)

    skill = Skill(name="Mathematics", category="domain")
    db_session.add(skill)
    job.skills.append(skill)

    resume = Resume(user_id=user.user_id, title="Ada's Resume")
    db_session.add(resume)
    db_session.flush()

    resume_version = ResumeVersion(resume_id=resume.resume_id, snapshot_json={"summary": "Mathematician"})
    resume_version.skills.append(skill)
    db_session.add(resume_version)
    db_session.flush()

    application = Application(
        user_id=user.user_id,
        job_id=job.job_id,
        resume_version_id=resume_version.resume_version_id,
        status=ApplicationStatus.APPLIED,
    )
    db_session.add(application)
    db_session.flush()

    note = Note(user_id=user.user_id, application_id=application.application_id, content="Interviewed.")
    db_session.add(note)
    db_session.commit()

    return {
        "user": user,
        "company": company,
        "job": job,
        "skill": skill,
        "resume": resume,
        "resume_version": resume_version,
        "application": application,
        "note": note,
    }


def test_full_chain_relationships_resolve(db_session):
    chain = _make_full_chain(db_session)

    assert chain["job"].company is chain["company"]
    assert chain["application"].user is chain["user"]
    assert chain["application"].job is chain["job"]
    assert chain["application"].resume_version is chain["resume_version"]
    assert chain["note"].application is chain["application"]
    assert chain["note"] in chain["application"].notes
    assert chain["skill"] in chain["job"].skills
    assert chain["skill"] in chain["resume_version"].skills
    assert chain["resume_version"] in chain["resume"].versions


def test_application_status_is_stored_lowercase(db_session):
    chain = _make_full_chain(db_session)

    raw_status = db_session.execute(
        text("SELECT status FROM applications WHERE application_id = :id"),
        {"id": chain["application"].application_id},
    ).scalar_one()

    assert raw_status == "applied"


def test_deleting_company_with_jobs_is_blocked(db_session):
    company = Company(name="Blocked Co")
    db_session.add(company)
    db_session.flush()

    job = Job(company_id=company.company_id, title="Some Role")
    db_session.add(job)
    db_session.commit()

    db_session.delete(company)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    assert db_session.get(Company, company.company_id) is not None
    assert db_session.get(Job, job.job_id) is not None


def test_deleting_user_cascades_resumes_applications_and_notes(db_session):
    chain = _make_full_chain(db_session)
    user_id = chain["user"].user_id
    resume_id = chain["resume"].resume_id
    application_id = chain["application"].application_id
    note_id = chain["note"].note_id
    job_id = chain["job"].job_id
    company_id = chain["company"].company_id

    db_session.delete(chain["user"])
    db_session.commit()

    assert db_session.get(User, user_id) is None
    assert db_session.get(Resume, resume_id) is None
    assert db_session.get(Application, application_id) is None
    assert db_session.get(Note, note_id) is None
    # The job and its company belong to the pipeline, not the applicant, and must survive.
    assert db_session.get(Job, job_id) is not None
    assert db_session.get(Company, company_id) is not None
