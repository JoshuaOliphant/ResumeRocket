"""Initial migration

Revision ID: 0001
Create Date: 2024-03-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create tables
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    op.create_table('job_description',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('customized_resume',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('original_content', sa.Text(), nullable=False),
        sa.Column('customized_content', sa.Text(), nullable=False),
        sa.Column('job_description_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('ats_score', sa.Float(), nullable=True),
        sa.Column('matching_keywords', sa.JSON(), nullable=True),
        sa.Column('missing_keywords', sa.JSON(), nullable=True),
        sa.Column('file_format', sa.String(length=10), nullable=True),
        sa.Column('original_bytes', sa.LargeBinary(), nullable=True),
        sa.ForeignKeyConstraint(['job_description_id'], ['job_description.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('customized_resume')
    op.drop_table('job_description')
    op.drop_table('user') 