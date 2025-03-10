#!/usr/bin/env python3
"""
Database migration utility for ResumeRocket

This script provides utilities for database migrations that are more complex than
simply creating new tables. Use this when you need to add columns, modify data,
or perform other database schema changes that SQLAlchemy's create_all() can't handle.
"""

import os
import sys
import logging
import argparse
import sqlite3
import importlib.util
from datetime import datetime
from pathlib import Path

# Add the parent directory to path so we can import app
sys.path.append(str(Path(__file__).parent.parent))

from app import app, db

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_path():
    """Extract the SQLite database path from the Flask app configuration"""
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if not db_uri or not db_uri.startswith('sqlite:///'):
        logger.error(f"Database URI is not a valid SQLite URI: {db_uri}")
        return None
    
    # Strip sqlite:/// prefix to get the file path
    return db_uri.replace('sqlite:///', '')

def execute_sql(sql_statements, params=None):
    """Execute raw SQL statements on the database"""
    db_path = get_db_path()
    if not db_path:
        return False
    
    logger.info(f"Executing SQL on database: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Execute each statement
        if isinstance(sql_statements, list):
            for stmt in sql_statements:
                logger.info(f"Executing: {stmt}")
                cursor.execute(stmt)
        else:
            logger.info(f"Executing: {sql_statements}")
            if params:
                cursor.execute(sql_statements, params)
            else:
                cursor.execute(sql_statements)
        
        # Commit changes
        conn.commit()
        logger.info("SQL execution successful")
        
        return True
    except Exception as e:
        logger.error(f"Error executing SQL: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def add_column(table_name, column_name, column_type):
    """Add a column to an existing table if it doesn't exist"""
    logger.info(f"Adding column {column_name} ({column_type}) to table {table_name}")
    
    # First check if the column already exists
    check_sql = f"PRAGMA table_info({table_name})"
    db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(check_sql)
        columns = cursor.fetchall()
        
        # Check if column exists
        column_exists = any(col[1] == column_name for col in columns)
        
        if column_exists:
            logger.info(f"Column {column_name} already exists in table {table_name}")
            return True
        
        # Add the column
        add_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        return execute_sql(add_sql)
    except Exception as e:
        logger.error(f"Error checking or adding column: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def copy_column_values(table_name, source_column, target_column):
    """Copy values from one column to another where target is NULL"""
    logger.info(f"Copying values from {source_column} to {target_column} in table {table_name}")
    
    update_sql = f"""
    UPDATE {table_name}
    SET {target_column} = {source_column}
    WHERE {target_column} IS NULL
    """
    
    return execute_sql(update_sql)

def apply_migration(migration_name=None):
    """Apply a specific migration from the migrations/versions directory"""
    if not migration_name:
        logger.error("No migration name specified")
        return False
    
    # Construct path to migration file
    migrations_dir = Path(__file__).parent.parent / 'migrations' / 'versions'
    migration_file = migrations_dir / f"{migration_name}.py"
    
    if not migration_file.exists():
        logger.error(f"Migration file {migration_file} does not exist")
        return False
    
    logger.info(f"Applying migration from {migration_file}")
    
    try:
        # Load the module
        spec = importlib.util.spec_from_file_location(migration_name, migration_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check if it has upgrade function
        if not hasattr(module, 'upgrade'):
            logger.error(f"Migration file {migration_file} does not have an upgrade function")
            return False
        
        # Apply migration using direct sqlite operations instead of alembic
        # This is necessary because we're not using alembic's context manager
        with app.app_context():
            if hasattr(module, 'custom_upgrade'):
                # Custom upgrade function that takes our utility functions
                module.custom_upgrade(
                    execute_sql=execute_sql,
                    add_column=add_column,
                    copy_column_values=copy_column_values
                )
            else:
                # Execute SQL statements defined in the migration, if any
                if hasattr(module, 'sql_statements'):
                    for stmt in module.sql_statements:
                        execute_sql(stmt)
        
        logger.info(f"Migration {migration_name} applied successfully")
        return True
    except Exception as e:
        logger.error(f"Error applying migration {migration_name}: {str(e)}")
        return False

def create_backup():
    """Create a backup of the database before migrations"""
    db_path = get_db_path()
    if not db_path:
        return False
    
    backup_path = f"{db_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    logger.info(f"Creating database backup at {backup_path}")
    
    try:
        # Connect to source database
        source_conn = sqlite3.connect(db_path)
        
        # Connect to backup database
        backup_conn = sqlite3.connect(backup_path)
        
        # Backup
        source_conn.backup(backup_conn)
        
        # Close connections
        source_conn.close()
        backup_conn.close()
        
        logger.info("Database backup created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database backup: {str(e)}")
        return False

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Database migration utility for ResumeRocket')
    
    # Add commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # add-column command
    add_column_parser = subparsers.add_parser('add-column', help='Add a column to a table')
    add_column_parser.add_argument('table', help='Table name')
    add_column_parser.add_argument('column', help='Column name')
    add_column_parser.add_argument('type', help='Column type (e.g., TEXT, INTEGER, FLOAT)')
    
    # apply command
    apply_parser = subparsers.add_parser('apply', help='Apply a specific migration')
    apply_parser.add_argument('migration', help='Migration name (without .py extension)')
    
    # backup command
    subparsers.add_parser('backup', help='Create a database backup')
    
    # execute-sql command
    execute_parser = subparsers.add_parser('execute-sql', help='Execute a SQL statement')
    execute_parser.add_argument('sql', help='SQL statement to execute')
    
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_args()
    
    if args.command == 'add-column':
        success = add_column(args.table, args.column, args.type)
    elif args.command == 'apply':
        success = apply_migration(args.migration)
    elif args.command == 'backup':
        success = create_backup()
    elif args.command == 'execute-sql':
        success = execute_sql(args.sql)
    else:
        logger.error("No command specified. Use -h for help.")
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    # Fix for Jina API Key
    if "JINA_API_KEY" not in os.environ:
        os.environ["JINA_API_KEY"] = "dummy"
        
    sys.exit(main())