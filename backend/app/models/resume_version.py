from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.associations import resume_version_skills


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    resume_version_id: Mapped[int] = mapped_column(primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.resume_id"), nullable=False)
    snapshot_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    resume: Mapped["Resume"] = relationship(back_populates="versions")
    applications: Mapped[list["Application"]] = relationship(back_populates="resume_version")
    skills: Mapped[list["Skill"]] = relationship(secondary=resume_version_skills, back_populates="resume_versions")
