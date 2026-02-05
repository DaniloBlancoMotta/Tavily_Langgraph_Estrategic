"""
LangSmith Tracing Configuration
================================

Centralized setup for LangSmith observability with @traceable decorators.
Tracks agent execution, tool calls, and LLM invocations for debugging and evaluation.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client, traceable
from typing import Dict, Any, Optional

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

logger = logging.getLogger("LangSmith")

# Initialize LangSmith Client
def get_langsmith_client() -> Optional[Client]:
    """
    Get or create LangSmith client instance.
    
    Returns:
        Client instance if tracing is enabled, None otherwise
    """
    if not os.getenv("LANGCHAIN_TRACING_V2") == "true":
        logger.warning("LangSmith tracing is disabled. Set LANGCHAIN_TRACING_V2=true in .env")
        return None
    
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        logger.error("LANGCHAIN_API_KEY not found in environment")
        return None
    
    try:
        client = Client(api_key=api_key)
        project_name = os.getenv("LANGCHAIN_PROJECT", "default")
        logger.info(f"✅ LangSmith client initialized for project: {project_name}")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize LangSmith client: {e}")
        return None


# Export traceable decorator for easy import
__all__ = ["traceable", "get_langsmith_client"]


def log_tracing_status():
    """Log current LangSmith tracing configuration."""
    tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2") == "true"
    project = os.getenv("LANGCHAIN_PROJECT", "Not Set")
    endpoint = os.getenv("LANGCHAIN_ENDPOINT", "Not Set")
    
    if tracing_enabled:
        logger.info("=" * 60)
        logger.info("🔍 LangSmith Tracing: ENABLED")
        logger.info(f"📊 Project: {project}")
        logger.info(f"🌐 Endpoint: {endpoint}")
        logger.info("=" * 60)
    else:
        logger.warning("⚠️  LangSmith Tracing: DISABLED")
        logger.warning("   To enable, set LANGCHAIN_TRACING_V2=true in .env")


# Log status on module import
log_tracing_status()
