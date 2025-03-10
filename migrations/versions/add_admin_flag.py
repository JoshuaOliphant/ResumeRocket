"""Add is_admin field to User table

Revision ID: add_admin_flag
Revises: add_feedback_loop_tables
Create Date: 2023-03-09 21:05:00

"""
from sqlalchemy import Column, Boolean
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = 'add_admin_flag'
down_revision = 'add_feedback_loop_tables'
branch_labels = None
depends_on = None


def upgrade():
    """Add is_admin field to User table."""
    op.add_column('user', sa.Column('is_admin', sa.Boolean(), nullable=True, server_default='0'))
    
    # Make the first user (you) an admin
    op.execute("UPDATE user SET is_admin = 1 WHERE id = 1")


def downgrade():
    """Remove is_admin field from User table."""
    op.drop_column('user', 'is_admin') 