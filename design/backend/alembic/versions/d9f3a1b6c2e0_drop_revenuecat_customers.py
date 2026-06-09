"""drop revenuecat_customers

The customer-link table backed an unused identity model (Option B). The app now
uses Option A everywhere: the RevenueCat app user id IS the backend app_user_id
(a UUID), so no separate link row is needed.

Revision ID: d9f3a1b6c2e0
Revises: 78ee3f88ac90
Create Date: 2026-06-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd9f3a1b6c2e0'
down_revision: Union[str, Sequence[str], None] = '78ee3f88ac90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop the now-unused revenuecat_customers table."""
    op.drop_table('revenuecat_customers')


def downgrade() -> None:
    """Recreate the revenuecat_customers table."""
    op.create_table(
        'revenuecat_customers',
        sa.Column('app_user_id', sa.UUID(), nullable=False),
        sa.Column('revenuecat_app_user_id', sa.Text(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ['app_user_id'],
            ['app_users.id'],
            name=op.f('fk_revenuecat_customers_app_user_id_app_users'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint(
            'app_user_id', name=op.f('pk_revenuecat_customers')
        ),
        sa.UniqueConstraint(
            'revenuecat_app_user_id',
            name=op.f('uq_revenuecat_customers_revenuecat_app_user_id'),
        ),
    )
