from pydantic import BaseModel


class SkillInsight(BaseModel):
    skill: str
    count: int
    total_analyzed: int


class DashboardRead(BaseModel):
    total_analyzed: int
    strongest_skill: SkillInsight | None
    biggest_gap: SkillInsight | None
