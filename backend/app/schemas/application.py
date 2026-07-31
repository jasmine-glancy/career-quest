from datetime import datetime

from pydantic import BaseModel

from app.models import ApplicationStatus


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
