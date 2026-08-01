from datetime import datetime

from pydantic import BaseModel


class AnalyzeFitRequest(BaseModel):
    user_id: int
    job_id: int
    resume_version_id: int


class AIAnalysisRead(BaseModel):
    analysis_id: int
    application_id: int
    match_score: int
    strengths_json: list[str]
    gaps_json: list[str]
    recommendations_json: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class OptimizeResumeRequest(BaseModel):
    user_id: int
    resume_version_id: int
    job_id: int


class ResumeEdit(BaseModel):
    section: str
    suggestion: str


class OptimizeResumeResponse(BaseModel):
    summary: str
    suggested_edits: list[ResumeEdit]
    missing_keywords: list[str]
