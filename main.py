#!/usr/bin/env python
"""
Production entry point for ResumeRocket.
In production, the frontend is served as static files from a separate process or CDN.
This file starts only the Flask backend API service.
"""
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the app
from backend.app import app

if __name__ == "__main__":
    # Use Gunicorn/uwsgi in production instead of this direct runner
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)