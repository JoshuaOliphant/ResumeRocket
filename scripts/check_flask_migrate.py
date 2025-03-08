#!/usr/bin/env python
"""
Check Flask-Migrate Installation

This simple script checks if Flask-Migrate is installed and displays its version.
Run this before using the migration features to ensure proper installation.

Usage:
    python scripts/check_flask_migrate.py
"""

import sys
import importlib.metadata

def check_flask_migrate():
    try:
        # Try to import flask_migrate
        import flask_migrate
        
        # Get the version
        try:
            version = importlib.metadata.version('flask-migrate')
            print(f"✅ Flask-Migrate is installed (version {version})")
            print("You are ready to use the database migration features.")
            return True
        except importlib.metadata.PackageNotFoundError:
            print("⚠️ Flask-Migrate is importable but version info not found.")
            print("You should still be able to use the migration features.")
            return True
            
    except ImportError:
        print("❌ Flask-Migrate is not installed.")
        print("\nPlease install it with one of these commands:")
        print("    uv pip install flask-migrate")
        print("    or")
        print("    pip install flask-migrate")
        return False

if __name__ == "__main__":
    success = check_flask_migrate()
    sys.exit(0 if success else 1) 