from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Resume, ResumeVersion, User
from app.schemas.resume import ResumeCreate, ResumeRead
from app.schemas.resume_version import ResumeVersionCreate, ResumeVersionRead

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("", response_model=ResumeRead, status_code=201)
def create_resume(payload: ResumeCreate, db: Session = Depends(get_db)) -> Resume:
    user = db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {payload.user_id} not found")

    resume = Resume(user_id=payload.user_id, title=payload.title)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("", response_model=list[ResumeRead])
def list_resumes(user_id: int, db: Session = Depends(get_db)) -> list[Resume]:
    return db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.created_at).all()


@router.post("/{resume_id}/versions", response_model=ResumeVersionRead, status_code=201)
def create_resume_version(
    resume_id: int, payload: ResumeVersionCreate, db: Session = Depends(get_db)
) -> ResumeVersion:
    resume = db.get(Resume, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail=f"Resume {resume_id} not found")

    version = ResumeVersion(resume_id=resume_id, snapshot_json=payload.snapshot_json)
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


@router.get("/{resume_id}/versions", response_model=list[ResumeVersionRead])
def list_resume_versions(resume_id: int, db: Session = Depends(get_db)) -> list[ResumeVersion]:
    resume = db.get(Resume, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail=f"Resume {resume_id} not found")

    return (
        db.query(ResumeVersion)
        .filter(ResumeVersion.resume_id == resume_id)
        .order_by(ResumeVersion.created_at)
        .all()
    )
