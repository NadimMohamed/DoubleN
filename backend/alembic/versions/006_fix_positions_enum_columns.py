"""Fix incomplete positions table missing enum columns

Revision ID: 006_fix_positions_enum_columns
Revises: 005_add_positions_table
Create Date: 2026-07-19 00:00:00.000000

Migration 005 creates the "positions" table in two steps: first the base
table, then the "side" and "status" enum columns via op.add_column(). If a
previous deployment was interrupted between those two steps, Alembic still
recorded 005 as complete, leaving behind a "positions" table that is missing
the "side" and/or "status" columns. Because 005's column-creation logic is
guarded by "if 'side' not in existing_columns", re-running 005 does nothing
in that scenario, and the incomplete table persists forever.

This migration detects that specific broken state and repairs it: if the
"positions" table exists but is missing "side" and/or "status", it is
dropped and recreated from scratch with the full, correct schema. If the
table is already correct (or doesn't exist), this migration creates it
fresh, so `alembic upgrade head` always ends with a complete table.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_fix_positions_enum_columns'
down_revision = '005_add_positions_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table('positions'):
        existing_columns = {
            column['name'] for column in inspector.get_columns('positions')
        }
        if 'side' not in existing_columns or 'status' not in existing_columns:
            # The table exists but is missing one (or both) of the
            # required enum columns - a leftover from a partially-applied
            # 005 migration. Drop the existing indexes/table so we can
            # recreate it cleanly below.
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
            inspector = sa.inspect(bind)

    if not inspector.has_table('positions'):
        # Ensure the enum types exist with the correct lowercase labels.
        # 005 already creates/repairs these types, but guard here too in
        # case this migration ever needs to run against a database where
        # 005 didn't get that far.
        enum_names = {enum['name'] for enum in inspector.get_enums()}

        if 'positionside' not in enum_names:
            postgresql.ENUM('long', 'short', name='positionside').create(bind, checkfirst=True)

        if 'positionstatus' not in enum_names:
            postgresql.ENUM('open', 'closed', name='positionstatus').create(bind, checkfirst=True)

        op.create_table(
            'positions',
            sa.Column('id', sa.String(36), nullable=False),
            sa.Column('user_id', sa.String(36), nullable=False),
            sa.Column('symbol', sa.String(20), nullable=False),
            sa.Column('quantity', sa.Float(), nullable=False),
            sa.Column('entry_price', sa.Float(), nullable=False),
            sa.Column('current_price', sa.Float(), nullable=False),
            sa.Column('leverage', sa.Float(), nullable=True, server_default='1.0'),
            sa.Column('stop_loss', sa.Float(), nullable=True),
            sa.Column('take_profit', sa.Float(), nullable=True),
            sa.Column('unrealized_pnl', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('unrealized_pnl_pct', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('realized_pnl', sa.Float(), nullable=True),
            sa.Column('opened_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now()),
            sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column(
                'side',
                postgresql.ENUM('long', 'short', name='positionside', create_type=False),
                nullable=False,
                server_default='long',
            ),
            sa.Column(
                'status',
                postgresql.ENUM('open', 'closed', name='positionstatus', create_type=False),
                nullable=True,
                server_default='open',
            ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
        )

        op.create_index('ix_positions_user_id', 'positions', ['user_id'])
        op.create_index('ix_positions_symbol', 'positions', ['symbol'])
        op.create_index('ix_positions_status', 'positions', ['status'])


def downgrade() -> None:
    # No-op: this migration only repairs a broken 005 outcome. Downgrading
    # to 005 would re-introduce the ambiguity this migration exists to fix.
    pass
