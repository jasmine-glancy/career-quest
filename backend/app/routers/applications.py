from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.deps import get_db
from app.models import ALLOWED_STATUS_TRANSITIONS, AIAnalysis, Application, ApplicationStatus, Job, ResumeVersion, User
from app.schemas.ai_analysis import AIAnalysisRead
from app.schemas.application import (
    ApplicationCreate,
    ApplicationListItem,
    ApplicationRead,
    ApplicationStatusUpdate,
)

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationRead, status_code=201)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)) -> Application:
    user = db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {payload.user_id} not found")

    job = db.get(Job, payload.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {payload.job_id} not found")

    if payload.resume_version_id is not None:
        resume_version = db.get(ResumeVersion, payload.resume_version_id)
        if resume_version is None:
            raise HTTPException(status_code=404, detail=f"Resume version {payload.resume_version_id} not found")
        if resume_version.resume.user_id != payload.user_id:
            raise HTTPException(
                status_code=400,
                detail=f"Resume version {payload.resume_version_id} does not belong to user {payload.user_id}",
            )

    application = Application(
        user_id=payload.user_id,
        job_id=payload.job_id,
        resume_version_id=payload.resume_version_id,
        status=ApplicationStatus.SAVED,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("", response_model=list[ApplicationListItem])
def list_applications(user_id: int, db: Session = Depends(get_db)) -> list[ApplicationListItem]:
    applications = (
        db.query(Application)
        .options(joinedload(Application.job).joinedload(Job.company))
        .filter(Application.user_id == user_id)
        .order_by(Application.created_at)
        .all()
    )
    return [
        ApplicationListItem(
            application_id=a.application_id,
            job_id=a.job_id,
            job_title=a.job.title,
            company_name=a.job.company.name,
            resume_version_id=a.resume_version_id,
            status=a.status,
            applied_at=a.applied_at,
            created_at=a.created_at,
        )
        for a in applications
    ]


@router.patch("/{application_id}/status", response_model=ApplicationRead)
def update_application_status(
    application_id: int, payload: ApplicationStatusUpdate, db: Session = Depends(get_db)
) -> Application:
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail=f"Application {application_id} not found")

    if payload.status != application.status:
        if payload.status not in ALLOWED_STATUS_TRANSITIONS[application.status]:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Cannot transition application from '{application.status.value}' "
                    f"to '{payload.status.value}'"
                ),
            )
        application.status = payload.status
        if payload.status == ApplicationStatus.APPLIED and application.applied_at is None:
            application.applied_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(application)
    return application


@router.get("/{application_id}/analysis", response_model=AIAnalysisRead)
def get_latest_analysis(application_id: int, db: Session = Depends(get_db)) -> AIAnalysis:
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail=f"Application {application_id} not found")

    analysis = (
        db.query(AIAnalysis)
        .filter(AIAnalysis.application_id == application_id)
        .order_by(AIAnalysis.created_at.desc(), AIAnalysis.analysis_id.desc())
        .first()
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail=f"No analysis yet for application {application_id}")
    return analysis
