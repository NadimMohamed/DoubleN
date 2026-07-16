"""Add positions table

Revision ID: 005_add_positions_table
Revises: 003_add_exchange_connections_table
Create Date: 2026-07-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '005_add_positions_table'
down_revision = '003_exchanges'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Create the positionside enum type.
    position_side_enum = postgresql.ENUM(
        'long',
        'short',
        name='positionside',
        create_type=True,
    )
    position_side_enum.create(bind, checkfirst=True)

    # Create the positionstatus enum type.
    position_status_enum = postgresql.ENUM(
        'open',
        'closed',
        name='positionstatus',
        create_type=True,
    )
    position_status_enum.create(bind, checkfirst=True)

    # The "positions" table may already exist from a previous deployment
    # where the migration ran but the alembic_version table wasn't updated.
    # Guard table/index creation so this migration can be re-run safely.
    if not inspector.has_table('positions'):
        op.create_table(
            'positions',
            sa.Column('id', sa.String(36), nullable=False),
            sa.Column('user_id', sa.String(36), nullable=False),
            sa.Column('symbol', sa.String(20), nullable=False),
            sa.Column('side', postgresql.ENUM('long', 'short', name='positionside', create_type=False), nullable=False),
            sa.Column('quantity', sa.Float(), nullable=False),
            sa.Column('entry_price', sa.Float(), nullable=False),
            sa.Column('current_price', sa.Float(), nullable=False),
            sa.Column('leverage', sa.Float(), nullable=True, server_default='1.0'),
            sa.Column('stop_loss', sa.Float(), nullable=True),
            sa.Column('take_profit', sa.Float(), nullable=True),
            sa.Column('unrealized_pnl', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('unrealized_pnl_pct', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('realized_pnl', sa.Float(), nullable=True),
            sa.Column('status', postgresql.ENUM('open', 'closed', name='positionstatus', create_type=False), nullable=True, server_default='open'),
            sa.Column('opened_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now()),
            sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
        )

    existing_indexes = {
        index['name'] for index in inspector.get_indexes('positions')
    } if inspector.has_table('positions') else set()

    if 'ix_positions_user_id' not in existing_indexes:
        op.create_index('ix_positions_user_id', 'positions', ['user_id'])
    if 'ix_positions_symbol' not in existing_indexes:
        op.create_index('ix_positions_symbol', 'positions', ['symbol'])
    if 'ix_positions_status' not in existing_indexes:
        op.create_index('ix_positions_status', 'positions', ['status'])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table('positions'):
        existing_indexes = {
            index['name'] for index in inspector.get_indexes('positions')
        }
        if 'ix_positions_status' in existing_indexes:
            op.drop_index('ix_positions_status', table_name='positions')
        if 'ix_positions_symbol' in existing_indexes:
            op.drop_index('ix_positions_symbol', table_name='positions')
        if 'ix_positions_user_id' in existing_indexes:
            op.drop_index('ix_positions_user_id', table_name='positions')

        op.drop_table('positions')

    postgresql.ENUM(name='positionstatus').drop(bind, checkfirst=True)
    postgresql.ENUM(name='positionside').drop(bind, checkfirst=True)
