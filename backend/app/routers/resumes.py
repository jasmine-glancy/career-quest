from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Resume, User
from app.schemas.resume import ResumeCreate, ResumeRead

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
