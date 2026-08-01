from datetime import datetime

from pydantic import BaseModel

from app.models import ApplicationStatus


class ApplicationCreate(BaseModel):
    user_id: int
    job_id: int
    resume_version_id: int | None = None


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationRead(BaseModel):
    application_id: int
    user_id: int
    job_id: int
    resume_version_id: int | None
    status: ApplicationStatus
    applied_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplicationListItem(BaseModel):
    application_id: int
    job_id: int
    job_title: str
    company_name: str
    resume_version_id: int | None
    status: ApplicationStatus
    applied_at: datetime | None
    created_at: datetime
