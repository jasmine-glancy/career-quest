"""add ai_analyses table

Revision ID: a1b2c3d4e5f6
Revises: 61d64e2fed70
Create Date: 2026-08-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '61d64e2fed70'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ai_analyses',
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('match_score', sa.Integer(), nullable=False),
        sa.Column('strengths_json', sa.JSON(), nullable=False),
        sa.Column('gaps_json', sa.JSON(), nullable=False),
        sa.Column('recommendations_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.application_id'], ),
        sa.PrimaryKeyConstraint('analysis_id'),
    )


def downgrade() -> None:
    op.drop_table('ai_analyses')
