# Migration Guide: Moving to Flask-Migrate

This guide helps you transition from the old direct database creation approach to using Flask-Migrate for database management.

## Why Flask-Migrate?

Flask-Migrate (based on Alembic) provides several advantages:

- Track changes to your database schema over time
- Apply migrations incrementally
- Roll back changes if needed
- Work effectively in teams where multiple developers might change the schema
- Better approach for production environments

## Migration Steps

### Step 1: Update Dependencies

First, make sure you have the latest dependencies installed:

```bash
# Using UV (recommended for speed)
uv pip install flask-migrate

# Or if using pip directly:
pip install flask-migrate
```

You can verify that Flask-Migrate is correctly installed by running:

```bash
python scripts/check_flask_migrate.py
```

### Step 2: Backup Your Data

It's always good practice to back up your database before making significant changes. 
We've created a script to help with this process:

```bash
python scripts/migrate_data.py
```

This script will:
1. Backup your current database
2. Check if tables already exist
   - If tables exist: Stamp the database with the initial migration (no changes made)
   - If tables don't exist but the file exists: Create new tables using migrations
   - If the database is empty: Create fresh tables with migrations
3. Handle any errors and restore from backup if needed

> **Note**: The script is designed to handle multiple scenarios, including empty databases, databases with tables, and databases with some unrecognized tables. It will automatically take the appropriate action based on the current state of your database.

### Step 3: Initialize the Database

If you prefer to start fresh or the migration script didn't work for you:

```bash
# Move or delete the old database (if it exists)
mv instance/app.db instance/app.db.old

# Run the initial migration
flask --app app db upgrade
```

### Step 4: Verify Everything Works

Start the application and verify that everything works as expected:

```bash
# Using Python directly
python main.py

# Or using Flask
flask --app app run
```

## Troubleshooting

### Migration Script Fails

If the migration script fails, you can:

1. Restore from the backup created by the script (check the script output for the backup location)
2. Manually create the database by running:
   ```bash
   flask --app app db upgrade
   ```

### "Table Already Exists" Error

If you get an error like `sqlite3.OperationalError: table user already exists` when running migrations:

1. This means you're trying to create tables that already exist in your database
2. You can manually stamp your database with the current migration:
   ```bash
   flask --app app db stamp 0001
   ```
   This tells Flask-Migrate that your database is already at this migration level without making changes

3. Alternatively, run the migration script which will handle this automatically:
   ```bash
   python scripts/migrate_data.py
   ```

### Database Tables Not Created

Make sure you're running the migrations correctly:

```bash
flask --app app db current  # Check current migration status
flask --app app db upgrade  # Apply migrations
```

### Error "Can't Locate Revision"

If you see an error like "Can't locate revision identified by '0001'", make sure the migrations directory is properly set up:

```bash
ls -la migrations/versions/  # Should contain migration files
```

### "No Such Table" Error

If you get an error like `Error reading old database: no such table: user` when running the migration script:

1. This happens when the database file exists, but doesn't contain the expected tables
2. The updated migration script should handle this automatically by:
   - Checking for empty databases
   - Creating new tables with migrations if needed
   - Backing up any existing data

3. If you still encounter this issue, you can start fresh:
   ```bash
   # Rename or remove the existing database
   mv instance/resumerocket.db instance/resumerocket.db.old
   
   # Run migrations to create a new database
   flask --app app db upgrade
   ```

## Future Schema Changes

When you make changes to your models in the future:

1. Update your model classes in `models.py`
2. Generate a migration:
   ```bash
   flask --app app db migrate -m "Description of changes"
   ```
3. Review the generated migration script in `migrations/versions/`
4. Apply the migration:
   ```bash
   flask --app app db upgrade
   ``` 