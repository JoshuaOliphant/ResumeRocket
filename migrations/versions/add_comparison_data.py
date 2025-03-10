"""
Migration file to add comparison_data, added_keywords_count, and changes_count columns
"""
import sqlite3
import logging

logger = logging.getLogger(__name__)

def upgrade():
    """Add the comparison data columns to the CustomizedResume table"""
    # Connect to the database
    conn = sqlite3.connect('resumerocket.db')
    cursor = conn.cursor()
    
    # Check if comparison_data column already exists
    cursor.execute("PRAGMA table_info(customized_resume)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Add comparison_data column (JSON type)
    if 'comparison_data' not in columns:
        cursor.execute('ALTER TABLE customized_resume ADD COLUMN comparison_data JSON')
        logger.info("Added comparison_data column to customized_resume table")
    
    # Add added_keywords_count column (INTEGER type with default 0)
    if 'added_keywords_count' not in columns:
        cursor.execute('ALTER TABLE customized_resume ADD COLUMN added_keywords_count INTEGER DEFAULT 0')
        logger.info("Added added_keywords_count column to customized_resume table")
    
    # Add changes_count column (INTEGER type with default 0)
    if 'changes_count' not in columns:
        cursor.execute('ALTER TABLE customized_resume ADD COLUMN changes_count INTEGER DEFAULT 0')
        logger.info("Added changes_count column to customized_resume table")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

def downgrade():
    """This is a no-op as SQLite doesn't support dropping columns easily"""
    # SQLite doesn't support dropping columns without recreating the table
    logger.info("Downgrade not implemented - SQLite doesn't support dropping columns easily")
    pass 