"""
Script to apply database migrations
"""
import os
import logging
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, Float, String, JSON, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from app import app, db
from migrations.versions.add_original_ats_score import upgrade as upgrade_original_score
from migrations.versions.add_comparison_data import upgrade as upgrade_comparison_data
from migrations.versions.add_feedback_loop_tables import upgrade as upgrade_feedback_loop

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get database path from environment or use default
db_path = os.environ.get('DATABASE_URI', 'sqlite:///resumerocket.db')
logger.info(f"Using database at: {db_path}")

# Create engine and metadata
engine = create_engine(db_path)
metadata = MetaData()
metadata.reflect(bind=engine)

def add_column(engine, table_name, column):
    column_name = column.name
    column_type = column.type.compile(dialect=engine.dialect)
    try:
        with engine.connect() as conn:
            conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}'))
            conn.commit()
        logger.info(f"Added column {column_name} to {table_name}")
    except Exception as e:
        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
            logger.info(f"Column {column_name} already exists in {table_name}")
        else:
            logger.error(f"Error adding column {column_name} to {table_name}: {str(e)}")

def apply_migrations():
    """Apply database migrations"""
    try:
        logger.info("Starting migration process...")
        
        # Add new columns to the CustomizedResume table
        try:
            # Columns we need to add
            add_column(engine, 'customized_resume', Column('improvement', Float, nullable=True))
            add_column(engine, 'customized_resume', Column('confidence', Float, nullable=True))
            add_column(engine, 'customized_resume', Column('optimization_data', JSON, nullable=True))
            add_column(engine, 'customized_resume', Column('customization_level', String(20)))
            add_column(engine, 'customized_resume', Column('industry', String(50), nullable=True))
            add_column(engine, 'customized_resume', Column('title', String(200), nullable=True))
            add_column(engine, 'customized_resume', Column('selected_recommendations', JSON, nullable=True))
            add_column(engine, 'customized_resume', Column('recommendation_feedback', JSON, nullable=True))
            
            # Add streaming columns
            from sqlalchemy import Boolean, Integer
            add_column(engine, 'customized_resume', Column('is_placeholder', Boolean, default=False))
            add_column(engine, 'customized_resume', Column('streaming_progress', Integer, default=0))
            add_column(engine, 'customized_resume', Column('streaming_status', String(100), nullable=True))
            
            logger.info("Migration completed successfully!")
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Migration process failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    # Set environment variables if needed
    os.environ["JINA_API_KEY"] = "dummy"
    
    # Apply the migrations
    success = apply_migrations()
    
    if success:
        logger.info("Database migration completed successfully!")
    else:
        logger.error("Database migration failed!")
        sys.exit(1)