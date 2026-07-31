from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Company, Job
from app.schemas.job import JobCreate, JobRead

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobRead, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db)) -> Job:
    company = db.query(Company).filter(Company.name == payload.company_name).one_or_none()
    if company is None:
        company = Company(name=payload.company_name)
        db.add(company)
        db.flush()

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
