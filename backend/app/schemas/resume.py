from datetime import datetime

from pydantic import BaseModel


class ResumeCreate(BaseModel):
    user_id: int
    title: str


class ResumeRead(BaseModel):
    resume_id: int
    user_id: int
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}
