"""add recall item audience

Revision ID: b5e2d7c1a9f3
Revises: e7a1c9d4b2f6
Create Date: 2026-10-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b5e2d7c1a9f3"
down_revision: Union[str, Sequence[str], None] = "e7a1c9d4b2f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Created explicitly (create_type=False) so downgrade can drop it, as in the
# add_recall_tables migration.
recall_audience = postgresql.ENUM(
    "everyone", "admin", name="recall_audience", create_type=False
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    recall_audience.create(bind, checkfirst=True)
    op.add_column(
        "recall_items",
        sa.Column(
            "audience",
            recall_audience,
            server_default=sa.text("'everyone'"),
            nullable=False,
        ),
    )
    # Focus check-ins are the owner's personal habits: admin-only from now on.
    op.execute("UPDATE recall_items SET audience = 'admin' WHERE kind = 'focus'")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("recall_items", "audience")
    recall_audience.drop(op.get_bind(), checkfirst=True)
