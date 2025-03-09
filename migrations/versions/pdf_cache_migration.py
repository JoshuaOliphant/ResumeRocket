"""PDF Cache Migration

Revision ID: 0002
Revises: 0001
Create Date: 2025-03-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    # Create PDFCache table
    op.create_table('pdf_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('extracted_text', sa.Text(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_accessed', sa.DateTime(), nullable=True),
        sa.Column('hit_count', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('content_hash')
    )
    
    # Create index for faster lookups by content hash
    op.create_index(op.f('ix_pdf_cache_content_hash'), 'pdf_cache', ['content_hash'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_pdf_cache_content_hash'), table_name='pdf_cache')
    op.drop_table('pdf_cache')