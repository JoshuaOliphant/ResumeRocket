#!/usr/bin/env python3
"""
Database migration script for ResumeRocket

This script ensures all database tables are created and up to date.
Run this script whenever the database schema changes.
"""

import os
import logging
from app import app, db
from models import User, JobDescription, CustomizedResume, PDFCache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with required tables."""
    try:
        with app.app_context():
            logger.info("Creating database tables...")
            db.create_all()
            logger.info("Database tables created successfully!")
            
            # Check if tables exist by querying them
            table_count = 0
            try:
                User.query.first()
                table_count += 1
                logger.info("User table exists")
            except Exception as e:
                logger.error(f"User table check failed: {e}")
                
            try:
                JobDescription.query.first()
                table_count += 1
                logger.info("JobDescription table exists")
            except Exception as e:
                logger.error(f"JobDescription table check failed: {e}")
                
            try:
                CustomizedResume.query.first()
                table_count += 1
                logger.info("CustomizedResume table exists")
            except Exception as e:
                logger.error(f"CustomizedResume table check failed: {e}")
                
            try:
                PDFCache.query.first()
                table_count += 1
                logger.info("PDFCache table exists")
            except Exception as e:
                logger.error(f"PDFCache table check failed: {e}")
                
            logger.info(f"Verified {table_count} tables exist")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    logger.info("Starting database migration...")
    init_db()
    logger.info("Database migration completed!")