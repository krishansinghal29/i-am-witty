"""add recall tables

Revision ID: e7a1c9d4b2f6
Revises: c3d4e5f6a7b8
Create Date: 2026-10-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e7a1c9d4b2f6"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Native Postgres enums for Recall. Declared with create_type=False so this
# migration owns the CREATE/DROP TYPE ordering explicitly; otherwise
# op.create_table would auto-emit CREATE TYPE and the type would leak (never
# dropped) on downgrade.
recall_cue_type = postgresql.ENUM(
    "reaction", "goal", name="recall_cue_type", create_type=False
)
recall_item_kind = postgresql.ENUM(
    "line", "concept", "routine", "focus", name="recall_item_kind", create_type=False
)
recall_item_status = postgresql.ENUM(
    "active", "paused", "archived", name="recall_item_status", create_type=False
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    recall_cue_type.create(bind, checkfirst=True)
    recall_item_kind.create(bind, checkfirst=True)
    recall_item_status.create(bind, checkfirst=True)

    op.create_table(
        "recall_cues",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("type", recall_cue_type, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_recall_cues")),
    )
    op.create_index(
        "recall_cues_text_lower_key",
        "recall_cues",
        [sa.text("lower(text)")],
        unique=True,
    )

    op.create_table(
        "recall_items",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("kind", recall_item_kind, nullable=False),
        sa.Column(
            "status",
            recall_item_status,
            server_default=sa.text("'active'"),
            nullable=False,
        ),
        sa.Column("cue_id", sa.UUID(), nullable=True),
        sa.Column("hint", sa.Text(), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("delivery_note", sa.Text(), nullable=True),
        sa.Column("question", sa.Text(), nullable=True),
        sa.Column("steps", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "scenarios", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("source", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["cue_id"],
            ["recall_cues.id"],
            name=op.f("fk_recall_items_cue_id_recall_cues"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_recall_items")),
    )
    op.create_index("recall_items_cue_idx", "recall_items", ["cue_id"], unique=False)
    op.create_index(
        "recall_items_kind_status_idx",
        "recall_items",
        ["kind", "status"],
        unique=False,
    )

    op.create_table(
        "recall_progress",
        sa.Column("learner_key", sa.Text(), nullable=False),
        sa.Column("item_id", sa.UUID(), nullable=False),
        sa.Column(
            "seen_count", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column("first_seen_on", sa.Date(), nullable=True),
        sa.Column("last_seen_on", sa.Date(), nullable=True),
        sa.Column("due_on", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["recall_items.id"],
            name=op.f("fk_recall_progress_item_id_recall_items"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "learner_key", "item_id", name=op.f("pk_recall_progress")
        ),
    )
    op.create_index(
        "recall_progress_learner_due_idx",
        "recall_progress",
        ["learner_key", "due_on"],
        unique=False,
    )

    op.create_table(
        "recall_checkins",
        sa.Column("learner_key", sa.Text(), nullable=False),
        sa.Column("item_id", sa.UUID(), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("done", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["recall_items.id"],
            name=op.f("fk_recall_checkins_item_id_recall_items"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "learner_key", "item_id", "local_date", name=op.f("pk_recall_checkins")
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("recall_checkins")
    op.drop_index("recall_progress_learner_due_idx", table_name="recall_progress")
    op.drop_table("recall_progress")
    op.drop_index("recall_items_kind_status_idx", table_name="recall_items")
    op.drop_index("recall_items_cue_idx", table_name="recall_items")
    op.drop_table("recall_items")
    op.drop_index("recall_cues_text_lower_key", table_name="recall_cues")
    op.drop_table("recall_cues")

    bind = op.get_bind()
    recall_item_status.drop(bind, checkfirst=True)
    recall_item_kind.drop(bind, checkfirst=True)
    recall_cue_type.drop(bind, checkfirst=True)
