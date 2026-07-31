from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models import Application, ApplicationStatus, Company, Job, Note, Resume, ResumeVersion, Skill, User


def seed() -> None:
    db = SessionLocal()
    try:
        user = User(name="Jasmine Glancy", email="jasmine@example.com")
        db.add(user)

        company = Company(name="Acme Corp", website="https://acme.example.com")
        db.add(company)
        db.flush()

        job = Job(
            company_id=company.company_id,
            title="Senior Backend Engineer",
            description="Build and scale our core platform APIs.",
            url="https://acme.example.com/careers/senior-backend-engineer",
            location="Remote",
        )
        db.add(job)

        python_skill = Skill(name="Python", category="language")
        sql_skill = Skill(name="SQL", category="language")
        fastapi_skill = Skill(name="FastAPI", category="framework")
        db.add_all([python_skill, sql_skill, fastapi_skill])
        job.skills.extend([python_skill, sql_skill, fastapi_skill])

        resume = Resume(user_id=user.user_id, title="Full Stack Engineer Resume")
        db.add(resume)
        db.flush()

        resume_version = ResumeVersion(
            resume_id=resume.resume_id,
            snapshot_json={
                "summary": "Full Stack engineer with 6 years building APIs and data pipelines.",
                "experience": [
                    {"company": "Previous Co", "title": "Backend Engineer", "years": 3},
                ],
                "skills": ["Python", "SQL", "FastAPI"],
            },
        )
        resume_version.skills.extend([python_skill, sql_skill, fastapi_skill])
        db.add(resume_version)
        db.flush()

        application = Application(
            user_id=user.user_id,
            job_id=job.job_id,
            resume_version_id=resume_version.resume_version_id,
            status=ApplicationStatus.APPLIED,
            applied_at=datetime.now(timezone.utc),
        )
        db.add(application)
        db.flush()

        note = Note(
            user_id=user.user_id,
            application_id=application.application_id,
            content="Recruiter said to expect a technical screen within a week.",
        )
        db.add(note)

        db.commit()
        print(
            f"Seeded user={user.user_id} company={company.company_id} job={job.job_id} "
            f"resume={resume.resume_id} resume_version={resume_version.resume_version_id} "
            f"application={application.application_id} note={note.note_id}"
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed()
