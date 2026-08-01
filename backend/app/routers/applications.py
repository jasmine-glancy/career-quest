from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Application, ApplicationStatus
from app.schemas.application import ApplicationRead, ApplicationStatusUpdate

router = APIRouter(prefix="/applications", tags=["applications"])


@router.patch("/{application_id}/status", response_model=ApplicationRead)
def update_application_status(
    application_id: int, payload: ApplicationStatusUpdate, db: Session = Depends(get_db)
) -> Application:
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail=f"Application {application_id} not found")

    application.status = payload.status
    if payload.status == ApplicationStatus.APPLIED and application.applied_at is None:
        application.applied_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(application)
    return application
