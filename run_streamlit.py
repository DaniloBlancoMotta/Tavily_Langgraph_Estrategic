"""
Strategic AI Agent - Streamlit App Launcher  
Adds project root to Python path and starts Streamlit
"""

import sys
from pathlib import Path
import subprocess

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    print("=" * 60)
    print("🎨 Starting StratGov AI Streamlit Interface")
    print("=" * 60)
    print()
    
    streamlit_app = project_root / "src" / "ui" / "streamlit_app.py"
    
    # Set environment variable for Python path
    import os
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    
    # Run streamlit
    subprocess.run(
        ["streamlit", "run", str(streamlit_app)],
        env=env
    )
