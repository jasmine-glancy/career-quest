from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.deps import get_db
from app.models import AIAnalysis, Application, User
from app.schemas.dashboard import DashboardRead, SkillInsight

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _latest_analysis(application: Application) -> AIAnalysis | None:
    if not application.analyses:
        return None
    return max(application.analyses, key=lambda analysis: (analysis.created_at, analysis.analysis_id))


@router.get("", response_model=DashboardRead)
def get_dashboard(user_id: int, db: Session = Depends(get_db)) -> DashboardRead:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    applications = (
        db.query(Application)
        .filter(Application.user_id == user_id)
        .options(joinedload(Application.analyses))
        .all()
    )
    latest_analyses = [a for a in (_latest_analysis(app_) for app_ in applications) if a is not None]

    total_analyzed = len(latest_analyses)
    matched_counts: Counter[str] = Counter()
    missing_counts: Counter[str] = Counter()
    for analysis in latest_analyses:
        matched_counts.update({skill.strip() for skill in analysis.matched_skills_json if skill.strip()})
        missing_counts.update({skill.strip() for skill in analysis.missing_skills_json if skill.strip()})

    strongest_skill = None
    if matched_counts:
        skill, count = matched_counts.most_common(1)[0]
        strongest_skill = SkillInsight(skill=skill, count=count, total_analyzed=total_analyzed)

    biggest_gap = None
    if missing_counts:
        skill, count = missing_counts.most_common(1)[0]
        biggest_gap = SkillInsight(skill=skill, count=count, total_analyzed=total_analyzed)

    return DashboardRead(
        total_analyzed=total_analyzed,
        strongest_skill=strongest_skill,
        biggest_gap=biggest_gap,
    )
