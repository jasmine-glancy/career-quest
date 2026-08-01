from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    analysis_id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.application_id"), nullable=False)
    match_score: Mapped[int] = mapped_column(Integer, nullable=False)
    strengths_json: Mapped[list] = mapped_column(JSON, nullable=False)
    gaps_json: Mapped[list] = mapped_column(JSON, nullable=False)
    recommendations_json: Mapped[list] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    application: Mapped["Application"] = relationship(back_populates="analyses")
