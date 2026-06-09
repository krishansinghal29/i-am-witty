"""add task_attempts.runtime_state

Persists the generated runtime context (prompt messages + assigned technique)
on the attempt at generate time, so the evaluator can read what the user
responded to at complete time without trusting a client-echoed prompt.

Revision ID: f1a2b3c4d5e6
Revises: d9f3a1b6c2e0
Create Date: 2026-06-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'd9f3a1b6c2e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'task_attempts',
        sa.Column(
            'runtime_state',
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column('task_attempts', 'runtime_state')
