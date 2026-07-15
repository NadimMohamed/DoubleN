"""Add exchange_connections table

Revision ID: 003_add_exchange_connections_table
Revises: 002_add_notifications_table
Create Date: 2026-07-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_exchange_connections_table'
down_revision = '002_add_notifications_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'exchange_connections',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('exchange', sa.String(50), nullable=False),
        sa.Column('api_key_encrypted', sa.Text(), nullable=False),
        sa.Column('api_secret_encrypted', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_connected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_exchange_connections_user_id', 'exchange_connections', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_exchange_connections_user_id', table_name='exchange_connections')
    op.drop_table('exchange_connections')
