from datetime import datetime

from pydantic import BaseModel


class JobCreate(BaseModel):
    company_name: str
    title: str
    description: str | None = None
    url: str | None = None
    location: str | None = None


class JobRead(BaseModel):
    job_id: int
    company_id: int
    title: str
    description: str | None
    url: str | None
    location: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
