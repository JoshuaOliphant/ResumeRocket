"""
Migration file to add feedback loop related tables and columns
"""
import sqlite3
import logging

logger = logging.getLogger(__name__)

def upgrade():
    """Add feedback loop tables and columns to the database"""
    # Connect to the database
    conn = sqlite3.connect('resumerocket.db')
    cursor = conn.cursor()
    
    # Add feedback fields to CustomizedResume table
    cursor.execute("PRAGMA table_info(customized_resume)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Add user_rating column
    if 'user_rating' not in columns:
        cursor.execute('ALTER TABLE customized_resume ADD COLUMN user_rating INTEGER')
        logger.info("Added user_rating column to customized_resume table")
    
    # Add user_feedback column
    if 'user_feedback' not in columns:
        cursor.execute('ALTER TABLE customized_resume ADD COLUMN user_feedback TEXT')
        logger.info("Added user_feedback column to customized_resume table")
    
    # Add was_effective column
    if 'was_effective' not in columns:
        cursor.execute('ALTER TABLE customized_resume ADD COLUMN was_effective BOOLEAN')
        logger.info("Added was_effective column to customized_resume table")
    
    # Add interview_secured column
    if 'interview_secured' not in columns:
        cursor.execute('ALTER TABLE customized_resume ADD COLUMN interview_secured BOOLEAN')
        logger.info("Added interview_secured column to customized_resume table")
    
    # Add job_secured column
    if 'job_secured' not in columns:
        cursor.execute('ALTER TABLE customized_resume ADD COLUMN job_secured BOOLEAN')
        logger.info("Added job_secured column to customized_resume table")
    
    # Add feedback_date column
    if 'feedback_date' not in columns:
        cursor.execute('ALTER TABLE customized_resume ADD COLUMN feedback_date TIMESTAMP')
        logger.info("Added feedback_date column to customized_resume table")
    
    # Create CustomizationEvaluation table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customization_evaluation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customized_resume_id INTEGER,
        evaluation_text TEXT NOT NULL,
        metrics JSON NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        applied_to_model BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (customized_resume_id) REFERENCES customized_resume (id)
    )
    ''')
    logger.info("Created customization_evaluation table if it didn't exist")
    
    # Create OptimizationSuggestion table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS optimization_suggestion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        based_on_evaluations INTEGER NOT NULL,
        implemented BOOLEAN DEFAULT FALSE,
        implementation_date TIMESTAMP,
        implementation_notes TEXT
    )
    ''')
    logger.info("Created optimization_suggestion table if it didn't exist")
    
    # Create ABTest table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ab_test (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        variants JSON NOT NULL,
        start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_date TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        results JSON,
        winner VARCHAR(50)
    )
    ''')
    logger.info("Created ab_test table if it didn't exist")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

def downgrade():
    """This is a no-op as SQLite doesn't support dropping columns easily"""
    # SQLite doesn't support dropping columns without recreating the table
    logger.info("Downgrade not implemented - SQLite doesn't support dropping columns easily")
    pass 