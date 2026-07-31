from sqlalchemy import Column, ForeignKey, Table

from app.db.base import Base

resume_version_skills = Table(
    "resume_version_skills",
    Base.metadata,
    Column("resume_version_id", ForeignKey("resume_versions.resume_version_id"), primary_key=True),
    Column("skill_id", ForeignKey("skills.skill_id"), primary_key=True),
)

job_skills = Table(
    "job_skills",
    Base.metadata,
    Column("job_id", ForeignKey("jobs.job_id"), primary_key=True),
    Column("skill_id", ForeignKey("skills.skill_id"), primary_key=True),
)
