"""Add original_ats_score column to CustomizedResume

Revision ID: add_original_ats_score
Revises: pdf_cache_migration
Create Date: 2025-03-09 19:40:00

"""

# revision identifiers, used by Alembic.
revision = 'add_original_ats_score'
down_revision = 'pdf_cache_migration'
branch_labels = None
depends_on = None

# SQL statements to execute for this migration
sql_statements = [
    "ALTER TABLE customized_resume ADD COLUMN original_ats_score FLOAT",
    "UPDATE customized_resume SET original_ats_score = ats_score WHERE original_ats_score IS NULL"
]

# This function is used by alembic if running through normal migration
def upgrade():
    pass  # Not used when running through our custom db_migration.py

# This function is used by our custom db_migration.py script
def custom_upgrade(execute_sql, add_column, copy_column_values):
    """Custom upgrade function that works with our db_migration utility"""
    # Add the column if it doesn't exist
    add_column('customized_resume', 'original_ats_score', 'FLOAT')
    
    # Copy values from ats_score to original_ats_score where NULL
    copy_column_values('customized_resume', 'ats_score', 'original_ats_score')

def downgrade():
    """Not implemented - we don't support downgrades in our custom system"""
    pass