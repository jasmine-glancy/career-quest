"""add matched/missing skill tags to ai_analyses

Revision ID: add_skill_tags_to_ai_analysis
Revises: a1b2c3d4e5f6
Create Date: 2026-08-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_skill_tags_to_ai_analysis'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'ai_analyses',
        sa.Column('matched_skills_json', sa.JSON(), server_default=sa.text("'[]'::json"), nullable=False),
    )
    op.add_column(
        'ai_analyses',
        sa.Column('missing_skills_json', sa.JSON(), server_default=sa.text("'[]'::json"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column('ai_analyses', 'missing_skills_json')
    op.drop_column('ai_analyses', 'matched_skills_json')
