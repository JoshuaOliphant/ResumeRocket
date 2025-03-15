import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the app
from backend.app import app

if __name__ == "__main__":
    # Use port 8080 to avoid conflict with AirPlay on macOS which uses port 5000
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)