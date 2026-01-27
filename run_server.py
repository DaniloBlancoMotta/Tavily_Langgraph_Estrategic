"""
Strategic AI Agent - Backend Server Launcher
Adds project root to Python path and starts the FastAPI server
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run the server
if __name__ == "__main__":
    from src.api.server import app
    import uvicorn
    
    print("=" * 60)
    print("🚀 Starting StratGov AI Backend Server")
    print("=" * 60)
    print()
    print("📍 Server: http://localhost:8000")
    print("📍 API Docs: http://localhost:8000/docs")
    print("📍 Health: http://localhost:8000/health")
    print()
    print("Press CTRL+C to stop")
    print("=" * 60)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
