from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.associations import job_skills, resume_version_skills


class Skill(Base):
    __tablename__ = "skills"

    skill_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    category: Mapped[str | None] = mapped_column(String(100))

    resume_versions: Mapped[list["ResumeVersion"]] = relationship(
        secondary=resume_version_skills, back_populates="skills"
    )
    jobs: Mapped[list["Job"]] = relationship(secondary=job_skills, back_populates="skills")
