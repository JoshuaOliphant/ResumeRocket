# ResumeRocket Deployment Guide

This guide explains how to deploy the ResumeRocket application to fly.io.

## Prerequisites

1. Install the Fly CLI:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. Log in to Fly:
   ```bash
   fly auth login
   ```

## Deployment Steps

1. **Initialize your Fly app** (skip if you've already done this):
   ```bash
   fly launch
   ```
   - When asked if you want to deploy now, select "No"
   - The CLI will generate a `fly.toml` file

2. **Create a persistent volume for the database**:
   ```bash
   fly volumes create resumerocket_data --size 1
   ```

3. **Set your secret environment variables**:
   ```bash
   fly secrets set JINA_API_KEY=your_jina_api_key \
                  ANTHROPIC_API_KEY=your_anthropic_api_key \
                  FLASK_SECRET_KEY=your_secure_random_key
   ```

4. **Deploy your application**:
   ```bash
   fly deploy
   ```

5. **Allocate an IP address** (first deployment only):
   ```bash
   fly ips allocate-v4
   ```

## Monitoring and Management

- **View logs**:
  ```bash
  fly logs
  ```

- **Connect to the app's shell**:
  ```bash
  fly ssh console
  ```

- **Scale your app** (if needed):
  ```bash
  fly scale count 2  # Increase to 2 instances
  ```

## Database Management

The SQLite database is stored on a persistent volume at `/app/instance/resumerocket.db`.

### Database Initialization

The application has been configured to automatically create all necessary database tables on startup using the `migrate.py` script. This script runs as part of the container's startup process and ensures your database schema is properly created.

### Database Backup and Restore

To backup your database:
```bash
fly ssh sftp get /app/instance/resumerocket.db ./backup.db
```

To restore a database from backup:
```bash
fly ssh sftp put ./backup.db /app/instance/resumerocket.db
```

### Troubleshooting Database Issues

If you encounter database errors, you can:

1. Connect to the container and manually run migrations:
   ```bash
   fly ssh console
   cd /app
   python migrate.py
   ```

2. Verify the database file exists and has proper permissions:
   ```bash
   fly ssh console
   ls -la /app/instance/
   ```

3. Check that the database contains the expected tables:
   ```bash
   fly ssh console
   cd /app
   sqlite3 /app/instance/resumerocket.db '.tables'
   ```

## Troubleshooting

- If your app fails to start, check the logs with `fly logs`
- To restart your app: `fly apps restart`
- To check the status of your app: `fly status`

## Important Notes

- The app is configured to auto-scale to zero when not in use to save costs
- First request after scaling from zero may be slow as the app boots up
- Your API keys are stored as secrets and not visible in deployment files