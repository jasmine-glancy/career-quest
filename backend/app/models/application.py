import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ApplicationStatus(str, enum.Enum):
    SAVED = "saved"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"


ALLOWED_STATUS_TRANSITIONS: dict[ApplicationStatus, frozenset[ApplicationStatus]] = {
    ApplicationStatus.SAVED: frozenset({ApplicationStatus.APPLIED, ApplicationStatus.REJECTED}),
    ApplicationStatus.APPLIED: frozenset({ApplicationStatus.INTERVIEWING, ApplicationStatus.REJECTED}),
    ApplicationStatus.INTERVIEWING: frozenset({ApplicationStatus.OFFER, ApplicationStatus.REJECTED}),
    ApplicationStatus.OFFER: frozenset(),
    ApplicationStatus.REJECTED: frozenset(),
}


class Application(Base):
    __tablename__ = "applications"

    application_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.job_id"), nullable=False)
    resume_version_id: Mapped[int | None] = mapped_column(ForeignKey("resume_versions.resume_version_id"))
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status", values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
        default=ApplicationStatus.SAVED,
    )
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="applications")
    job: Mapped["Job"] = relationship(back_populates="applications")
    resume_version: Mapped["ResumeVersion | None"] = relationship(back_populates="applications")
    notes: Mapped[list["Note"]] = relationship(back_populates="application", cascade="all, delete-orphan")
    analyses: Mapped[list["AIAnalysis"]] = relationship(back_populates="application", cascade="all, delete-orphan")
