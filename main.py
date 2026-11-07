"""
FoxTrader-Pro Root ASGI Entrypoint
Used by Render, Vercel, Docker, and standard Cloud Deployment Platforms.
Exposes 'app' directly so 'uvicorn main:app' runs seamlessly from repository root.
"""

import os
import sys

# Ensure backend directory and root are in sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(1, ROOT_DIR)

# Import the FastAPI application instance from backend.main
from backend.main import app

if __name__ == "__main__":
    import uvicorn
    # Render and cloud environments provide PORT dynamically
    port = int(os.environ.get("PORT", 8088))
    # Always bind to 0.0.0.0 in cloud containers so health checks succeed
    host = "0.0.0.0"
    uvicorn.run("main:app", host=host, port=port, reload=False)
