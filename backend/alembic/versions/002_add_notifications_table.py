"""Add notifications table

Revision ID: 002_add_notifications_table
Revises: 001_initial
Create Date: 2026-07-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '002_add_notifications_table'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the notificationtype enum type
    notification_type_enum = postgresql.ENUM(
        'price_alert',
        'trend_alert',
        'signal_alert',
        'position_alert',
        'margin_alert',
        'disconnection_alert',
        'error_alert',
        'info',
        name='notificationtype',
        create_type=True
    )
    notification_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('type', notification_type_enum, nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('symbol', sa.String(20), nullable=True),
        sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_type', 'notifications', ['type'])
    op.create_index('ix_notifications_symbol', 'notifications', ['symbol'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_notifications_created_at', table_name='notifications')
    op.drop_index('ix_notifications_is_read', table_name='notifications')
    op.drop_index('ix_notifications_symbol', table_name='notifications')
    op.drop_index('ix_notifications_type', table_name='notifications')
    op.drop_index('ix_notifications_user_id', table_name='notifications')
    
    # Drop table
    op.drop_table('notifications')
    
    # Drop enum type
    notification_type_enum = postgresql.ENUM(
        'price_alert',
        'trend_alert',
        'signal_alert',
        'position_alert',
        'margin_alert',
        'disconnection_alert',
        'error_alert',
        'info',
        name='notificationtype'
    )
    notification_type_enum.drop(op.get_bind(), checkfirst=True)
