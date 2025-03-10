# Database Migration Examples

This document provides examples of how to use the database migration utility.

## Add a new column

To add a new column to an existing table:

```bash
python scripts/db_migration.py add-column customized_resume original_ats_score FLOAT
```

## Create a database backup

Before making schema changes, it's a good idea to back up the database:

```bash
python scripts/db_migration.py backup
```

## Execute a SQL statement

To execute arbitrary SQL:

```bash
python scripts/db_migration.py execute-sql "UPDATE customized_resume SET original_ats_score = ats_score WHERE original_ats_score IS NULL"
```

## Apply a migration

To apply a migration defined in the migrations/versions directory:

```bash
python scripts/db_migration.py apply add_original_ats_score
```

## Creating a migration file

1. Create a new Python file in migrations/versions (e.g., migrations/versions/add_new_column.py)
2. Follow this template:

```python
"""Short description of the migration

Revision ID: add_new_column
Revises: previous_migration_name
Create Date: YYYY-MM-DD HH:MM:SS
"""

# revision identifiers, used by Alembic.
revision = 'add_new_column'
down_revision = 'previous_migration_name'
branch_labels = None
depends_on = None

# SQL statements to execute for this migration
sql_statements = [
    "ALTER TABLE table_name ADD COLUMN column_name COLUMN_TYPE",
    "UPDATE table_name SET column_name = default_value WHERE column_name IS NULL"
]

# This function is used by alembic if running through normal migration
def upgrade():
    pass  # Not used when running through our custom db_migration.py

# This function is used by our custom db_migration.py script
def custom_upgrade(execute_sql, add_column, copy_column_values):
    """Custom upgrade function that works with our db_migration utility"""
    # Add the column if it doesn't exist
    add_column('table_name', 'column_name', 'COLUMN_TYPE')
    
    # Add any other migration steps here
    execute_sql("UPDATE table_name SET column_name = 'default_value' WHERE column_name IS NULL")

def downgrade():
    """Not implemented - we don't support downgrades in our custom system"""
    pass
```

3. Apply the migration using `python scripts/db_migration.py apply add_new_column`