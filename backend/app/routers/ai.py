from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import AIAnalysis, Application, ApplicationStatus, Job, ResumeVersion, User
from app.schemas.ai_analysis import (
    AIAnalysisRead,
    AnalyzeFitRequest,
    OptimizeResumeRequest,
    OptimizeResumeResponse,
)
from app.services.ai_analysis import AIServiceError, generate_job_fit_analysis, generate_resume_optimization

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/analyze-fit", response_model=AIAnalysisRead, status_code=201)
def analyze_fit(payload: AnalyzeFitRequest, db: Session = Depends(get_db)) -> AIAnalysis:
    user = db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {payload.user_id} not found")

    job = db.get(Job, payload.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {payload.job_id} not found")

    resume_version = db.get(ResumeVersion, payload.resume_version_id)
    if resume_version is None:
        raise HTTPException(status_code=404, detail=f"Resume version {payload.resume_version_id} not found")
    if resume_version.resume.user_id != payload.user_id:
        raise HTTPException(
            status_code=400,
            detail=f"Resume version {payload.resume_version_id} does not belong to user {payload.user_id}",
        )

    application = (
        db.query(Application)
        .filter(Application.user_id == payload.user_id, Application.job_id == payload.job_id)
        .order_by(Application.created_at)
        .first()
    )
    if application is None:
        application = Application(
            user_id=payload.user_id,
            job_id=payload.job_id,
            resume_version_id=payload.resume_version_id,
            status=ApplicationStatus.SAVED,
        )
        db.add(application)
    else:
        application.resume_version_id = payload.resume_version_id
    db.commit()
    db.refresh(application)

    try:
        result = generate_job_fit_analysis(resume_version.snapshot_json, job.title, job.description)
    except AIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    analysis = AIAnalysis(
        application_id=application.application_id,
        match_score=result["match_score"],
        strengths_json=result["strengths"],
        gaps_json=result["gaps"],
        recommendations_json=result["recommendations"],
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


@router.post("/optimize-resume", response_model=OptimizeResumeResponse)
def optimize_resume(payload: OptimizeResumeRequest, db: Session = Depends(get_db)) -> OptimizeResumeResponse:
    user = db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {payload.user_id} not found")

    resume_version = db.get(ResumeVersion, payload.resume_version_id)
    if resume_version is None:
        raise HTTPException(status_code=404, detail=f"Resume version {payload.resume_version_id} not found")
    if resume_version.resume.user_id != payload.user_id:
        raise HTTPException(
            status_code=400,
            detail=f"Resume version {payload.resume_version_id} does not belong to user {payload.user_id}",
        )

    job = db.get(Job, payload.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {payload.job_id} not found")

    try:
        result = generate_resume_optimization(resume_version.snapshot_json, job.title, job.description)
    except AIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return OptimizeResumeResponse(**result)
