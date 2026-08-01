from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ResumeVersionCreate(BaseModel):
    snapshot_json: dict[str, Any]


class ResumeVersionRead(BaseModel):
    resume_version_id: int
    resume_id: int
    snapshot_json: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
