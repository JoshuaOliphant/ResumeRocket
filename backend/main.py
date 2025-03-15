import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import app directly
from app import app

if __name__ == "__main__":
    try:
        # Use port 8080 to avoid conflict with AirPlay on macOS which uses port 5000
        port = int(os.environ.get("PORT", 8080))
        app.run(host="0.0.0.0", port=port, debug=True)
    except Exception as e:
        logger.error(f"Error running application: {str(e)}")
        raise
