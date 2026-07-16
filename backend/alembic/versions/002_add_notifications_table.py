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
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Create the notificationtype enum type. This is the ONLY migration
    # that should create this type (create_type=True + explicit .create()
    # call with checkfirst=True). All later migrations that reference
    # NotificationType must build their ENUM with create_type=False so
    # they reuse the existing Postgres type instead of trying to create
    # it again (which raises "type notificationtype already exists").
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
        create_type=False
    )
    notification_type_enum.create(op.get_bind(), checkfirst=True)

    # Separate ENUM instance for the column definition below with
    # create_type=False, so that op.create_table doesn't also try to
    # (re)create the type — it was already created explicitly above.
    notification_type_column_enum = postgresql.ENUM(
        'price_alert',
        'trend_alert',
        'signal_alert',
        'position_alert',
        'margin_alert',
        'disconnection_alert',
        'error_alert',
        'info',
        name='notificationtype',
        create_type=False
    )

    # Create notifications table
    if not inspector.has_table('notifications'):
        op.create_table(
            'notifications',
            sa.Column('id', sa.String(36), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('type', notification_type_column_enum, nullable=False),
            sa.Column('title', sa.String(255), nullable=False),
            sa.Column('message', sa.Text(), nullable=False),
            sa.Column('symbol', sa.String(20), nullable=True),
            sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
            sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

    # Re-inspect in case the table was just created, to get an accurate index list
    existing_indexes = {
        index['name'] for index in inspector.get_indexes('notifications')
    } if inspector.has_table('notifications') else set()

    # Create indexes
    if 'ix_notifications_user_id' not in existing_indexes:
        op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    if 'ix_notifications_type' not in existing_indexes:
        op.create_index('ix_notifications_type', 'notifications', ['type'])
    if 'ix_notifications_symbol' not in existing_indexes:
        op.create_index('ix_notifications_symbol', 'notifications', ['symbol'])
    if 'ix_notifications_is_read' not in existing_indexes:
        op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])
    if 'ix_notifications_created_at' not in existing_indexes:
        op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table('notifications'):
        existing_indexes = {
            index['name'] for index in inspector.get_indexes('notifications')
        }

        # Drop indexes
        if 'ix_notifications_created_at' in existing_indexes:
            op.drop_index('ix_notifications_created_at', table_name='notifications')
        if 'ix_notifications_is_read' in existing_indexes:
            op.drop_index('ix_notifications_is_read', table_name='notifications')
        if 'ix_notifications_symbol' in existing_indexes:
            op.drop_index('ix_notifications_symbol', table_name='notifications')
        if 'ix_notifications_type' in existing_indexes:
            op.drop_index('ix_notifications_type', table_name='notifications')
        if 'ix_notifications_user_id' in existing_indexes:
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
