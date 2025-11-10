"""add is_admin column to users

Revision ID: 001
Revises: 
Create Date: 2025-11-10

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if column exists before adding (for idempotency)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'is_admin' not in columns:
        op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=True, server_default='false'))
        # Update existing rows to have is_admin = false
        op.execute("UPDATE users SET is_admin = false WHERE is_admin IS NULL")
        # Make column non-nullable after setting defaults
        op.alter_column('users', 'is_admin', nullable=False)


def downgrade() -> None:
    op.drop_column('users', 'is_admin')
