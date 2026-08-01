from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Company, Job
from app.schemas.job import JobCreate, JobRead

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _get_or_create_company(db: Session, company_name: str) -> Company:
    normalized = company_name.strip()
    company = db.query(Company).filter(func.lower(Company.name) == normalized.lower()).one_or_none()
    if company is not None:
        return company

    company = Company(name=normalized)
    db.add(company)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        company = db.query(Company).filter(func.lower(Company.name) == normalized.lower()).one_or_none()
        if company is None:
            raise
    return company


@router.post("", response_model=JobRead, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db)) -> Job:
    company = _get_or_create_company(db, payload.company_name)

    job = Job(
        company_id=company.company_id,
        title=payload.title,
        description=payload.description,
        url=payload.url,
        location=payload.location,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
