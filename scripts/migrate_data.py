#!/usr/bin/env python
"""
Data Migration Script - Helps transfer data from old to new database

This script backs up the old database and helps initialize a new database
using Flask-Migrate. It copies data from the old database to the new one.

Usage:
    python scripts/migrate_data.py
    
Make sure Flask-Migrate is installed before running:
    uv pip install flask-migrate
    or
    pip install flask-migrate
"""

import os
import sys
import shutil
import sqlite3
import datetime
from pathlib import Path

# Add parent directory to path to import app
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Wait to import app until after we've added project_root to the path
try:
    from app import app, db
    from flask_migrate import upgrade, stamp
    from sqlalchemy import inspect
except ImportError as e:
    print(f"Error importing application: {e}")
    print("\nMake sure Flask-Migrate is installed:")
    print("    uv pip install flask-migrate")
    print("    or")
    print("    pip install flask-migrate")
    sys.exit(1)

def backup_database():
    """Backup the existing database file"""
    with app.app_context():
        # Get database path (assuming SQLite)
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if not db_uri.startswith('sqlite:///'):
            print("This script only works with SQLite databases!")
            return False
            
        db_path = db_uri.replace('sqlite:///', '')
        if not db_path:
            print("Could not determine database path")
            return False
            
        # Convert to absolute path if relative
        if not os.path.isabs(db_path):
            db_path = os.path.join(project_root, db_path)
            
        # Check if the file exists
        if not os.path.exists(db_path):
            print(f"Database file does not exist: {db_path}")
            return False
            
        # Create backup with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}.backup_{timestamp}"
        try:
            shutil.copy2(db_path, backup_path)
            print(f"Database backed up to: {backup_path}")
            return db_path
        except Exception as e:
            print(f"Error backing up database: {e}")
            return False

def get_data_from_old_db(db_path):
    """Extract data from the old database"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Get users
        users = list(conn.execute("SELECT * FROM user").fetchall())
        
        # Get job descriptions
        job_descriptions = list(conn.execute("SELECT * FROM job_description").fetchall())
        
        # Get customized resumes
        customized_resumes = list(conn.execute("SELECT * FROM customized_resume").fetchall())
        
        conn.close()
        
        return {
            'users': users,
            'job_descriptions': job_descriptions,
            'customized_resumes': customized_resumes
        }
    except Exception as e:
        print(f"Error reading old database: {e}")
        return None

def check_tables_exist():
    """Check if expected tables already exist in the database"""
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        expected_tables = ['user', 'job_description', 'customized_resume']
        
        # Check if all expected tables exist
        exists = all(table in existing_tables for table in expected_tables)
        
        if exists:
            print("All expected tables already exist in the database.")
        else:
            missing = [t for t in expected_tables if t not in existing_tables]
            print(f"Some tables are missing: {missing}")
            
        return exists

def main():
    """Main migration function"""
    print("Starting database migration...")
    
    # Backup old database
    db_path = backup_database()
    if not db_path:
        print("Backup failed, aborting migration.")
        return
    
    print("Checking if tables already exist...")
    tables_exist = check_tables_exist()
    
    if tables_exist:
        print("Existing tables found. Stamping current database as initial migration...")
        with app.app_context():
            # Stamp the database with the initial migration ID
            # so Alembic knows it's already at this revision
            stamp('0001')  # Use the revision ID from your initial migration
            print("Database has been stamped with initial migration.")
            print("\nYou can now continue using the application with Flask-Migrate.")
            print("For future model changes, use: flask --app app db migrate -m 'description'")
        return
    
    # If tables don't exist, we have two options:
    # 1. If it's a new database, just run migrations
    # 2. If it's an old database, try to extract data first
    
    # Try to check if it's an existing database with data
    try:
        print("Checking if database has existing data...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Try to list all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = cursor.fetchall()
        conn.close()
        
        if not existing_tables or len(existing_tables) == 0:
            print("No tables found in database. Creating fresh database with migrations...")
            with app.app_context():
                try:
                    upgrade()
                    print("Database created successfully with migrations!")
                    print("\nYou can now run the application with the new migration-based database.")
                except Exception as e:
                    print(f"Error during migration: {e}")
            return
    except Exception as e:
        print(f"Error checking database: {e}")
        print("Proceeding with assumption that this is a fresh database...")
        with app.app_context():
            try:
                upgrade()
                print("Database created successfully with migrations!")
                print("\nYou can now run the application with the new migration-based database.")
            except Exception as e:
                print(f"Error during migration: {e}")
        return
    
    # If we reach here, the database has tables but not our expected ones
    # Try to extract data from the old db
    print("Extracting data from old database...")
    old_data = get_data_from_old_db(db_path)
    if not old_data:
        print("No data to migrate or tables are in unexpected format.")
        print("Creating fresh database with migrations...")
        
        # Rename old database
        os.rename(db_path, f"{db_path}.old")
        print(f"Renamed old database to {db_path}.old")
        
        with app.app_context():
            try:
                print("Running database migrations...")
                upgrade()
                print("Database created successfully with migrations!")
                print("\nYou can now run the application with the new migration-based database.")
                print(f"If you need to restore the old database, the backup is available at: {db_path}.backup_*")
            except Exception as e:
                print(f"Error during migration: {e}")
                print("\nRestoring backup from before migration...")
                # Try to restore the backup if the migration failed
                latest_backup = max(Path(db_path).parent.glob(f"{Path(db_path).name}.backup_*"), key=os.path.getctime)
                shutil.copy2(latest_backup, db_path)
                print(f"Restored database from {latest_backup}")
                print("Please check the error message and try again after fixing the issue.")
        return
        
    # If we have data, proceed with the migration
    # Rename old database
    os.rename(db_path, f"{db_path}.old")
    print(f"Renamed old database to {db_path}.old")
    
    with app.app_context():
        try:
            print("Running database migrations...")
            upgrade()
            
            print("Data migration is complete!")
            print("\nYou can now run the application with the new migration-based database.")
            print(f"If you need to restore the old database, the backup is available at: {db_path}.backup_*")
        except Exception as e:
            print(f"Error during migration: {e}")
            print("\nRestoring backup from before migration...")
            # Try to restore the backup if the migration failed
            latest_backup = max(Path(db_path).parent.glob(f"{Path(db_path).name}.backup_*"), key=os.path.getctime)
            shutil.copy2(latest_backup, db_path)
            print(f"Restored database from {latest_backup}")
            print("Please check the error message and try again after fixing the issue.")

if __name__ == "__main__":
    main() 