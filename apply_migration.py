"""
Script to apply database migrations
"""
import os
import logging
from app import app, db
from migrations.versions.add_original_ats_score import upgrade as upgrade_original_score
from migrations.versions.add_comparison_data import upgrade as upgrade_comparison_data
from migrations.versions.add_feedback_loop_tables import upgrade as upgrade_feedback_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_migrations():
    logger.info("Applying migrations...")
    
    with app.app_context():
        # Apply the original_ats_score migration
        try:
            upgrade_original_score()
            logger.info("Successfully added original_ats_score column")
        except Exception as e:
            logger.error(f"Error applying original_ats_score migration: {str(e)}")
        
        # Apply the comparison_data migration
        try:
            upgrade_comparison_data()
            logger.info("Successfully added comparison data columns")
        except Exception as e:
            logger.error(f"Error applying comparison_data migration: {str(e)}")
            
        # Apply the feedback loop migration
        try:
            upgrade_feedback_loop()
            logger.info("Successfully added feedback loop tables and columns")
        except Exception as e:
            logger.error(f"Error applying feedback_loop migration: {str(e)}")
    
    return True

if __name__ == "__main__":
    # Set environment variables if needed
    os.environ["JINA_API_KEY"] = "dummy"
    
    # Apply the migrations
    success = apply_migrations()
    
    if success:
        logger.info("Migrations completed!")
    else:
        logger.error("Migrations failed!")