"""Add streaming columns to CustomizedResume table

This migration adds columns needed for the streaming resume customization feature.
"""

# SQL statements to be executed
sql_statements = [
    "ALTER TABLE customized_resume ADD COLUMN is_placeholder BOOLEAN DEFAULT FALSE",
    "ALTER TABLE customized_resume ADD COLUMN streaming_progress INTEGER DEFAULT 0",
    "ALTER TABLE customized_resume ADD COLUMN streaming_status VARCHAR(100)"
]

def custom_upgrade(execute_sql, add_column, copy_column_values):
    """
    Apply the migration using the provided utility functions.
    """
    # Add columns one by one to handle any errors more gracefully
    add_column('customized_resume', 'is_placeholder', 'BOOLEAN DEFAULT FALSE')
    add_column('customized_resume', 'streaming_progress', 'INTEGER DEFAULT 0')
    add_column('customized_resume', 'streaming_status', 'VARCHAR(100)')
    
    # Execute any custom update queries if needed
    # For example, setting default values for existing rows
    execute_sql("UPDATE customized_resume SET is_placeholder = FALSE WHERE is_placeholder IS NULL")
    execute_sql("UPDATE customized_resume SET streaming_progress = 100 WHERE streaming_progress IS NULL")