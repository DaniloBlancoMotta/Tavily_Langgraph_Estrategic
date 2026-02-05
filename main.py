"""
Strategic AI Agent - Main Entry Point with AgentOps

This is the main entry point for the Strategic AI Agent.
Includes AgentOps for advanced observability and monitoring.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import AgentOps for observability
import agentops

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


def initialize_agentops():
    """Initialize AgentOps monitoring"""
    
    agentops_api_key = os.getenv("AGENTOPS_API_KEY")
    
    if agentops_api_key:
        print("🔍 Initializing AgentOps monitoring...")
        
        # Initialize AgentOps with langgraph tag
        agentops.init(
            api_key=agentops_api_key,
            default_tags=['langgraph', 'strategic-agent'],
            auto_start_session=True
        )
        
        print("✅ AgentOps initialized successfully")
        print(f"   Dashboard: https://app.agentops.ai/")
        return True
    else:
        print("⚠️  AgentOps API key not found in .env")
        print("   Set AGENTOPS_API_KEY to enable AgentOps monitoring")
        return False


def run_streamlit():
    """Run the Streamlit application"""
    import subprocess
    
    print("=" * 60)
    print("🎨 Starting StratGov AI Streamlit Interface")
    print("=" * 60)
    print()
    
    streamlit_app = project_root / "src" / "ui" / "streamlit_app.py"
    
    # Set environment variable for Python path
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    
    # Run streamlit
    subprocess.run(
        ["streamlit", "run", str(streamlit_app)],
        env=env
    )


def run_server():
    """Run the FastAPI server"""
    print("=" * 60)
    print("🚀 Starting StratGov AI API Server")
    print("=" * 60)
    print()
    
    # Import and run server
    from src.api.server import app
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


def main():
    """Main entry point"""
    
    print("\n")
    print("=" * 60)
    print("🤖 STRATEGIC AI AGENT")
    print("=" * 60)
    print()
    
    # Initialize AgentOps
    agentops_enabled = initialize_agentops()
    
    print()
    print("Available Modes:")
    print("  1. Streamlit UI (default)")
    print("  2. FastAPI Server")
    print()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = "streamlit"
    
    # Run appropriate mode
    if mode in ["streamlit", "ui", "1"]:
        run_streamlit()
    elif mode in ["server", "api", "2"]:
        run_server()
    else:
        print(f"❌ Unknown mode: {mode}")
        print("Usage: python main.py [streamlit|server]")
        sys.exit(1)


if __name__ == "__main__":
    main()
