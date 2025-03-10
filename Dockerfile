# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Create instance directory for SQLite database
RUN mkdir -p instance && chmod 777 instance

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Set environment variables for production
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV DATABASE_URL=sqlite:///resumerocket.db
ENV MAX_CONTENT_LENGTH=5242880

# Note: Secret environment variables should be set during deployment
# JINA_API_KEY, ANTHROPIC_API_KEY, and FLASK_SECRET_KEY should be
# set as secrets in fly.io, not hardcoded in the Dockerfile

# Create a startup script to initialize the database before starting the application
RUN echo '#!/bin/bash\n\
echo "Initializing database..."\n\
# Run the migration script to create database tables\n\
python migrate.py\n\
echo "Database initialized, starting server..."\n\
exec gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 60 main:app\n'\
> /app/start.sh && chmod +x /app/start.sh

# Run the startup script that initializes the database and starts the server
CMD ["/app/start.sh"]