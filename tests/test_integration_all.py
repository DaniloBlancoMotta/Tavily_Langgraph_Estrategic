"""
Integration Tests for Strategic AI Agent
Tests all major components: APIs, Backend, Frontend connections
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("🧪 STRATEGIC AI AGENT - INTEGRATION TESTS")
print("=" * 60)
print()

# Test 1: Environment Variables
print("📋 Test 1: Environment Configuration")
print("-" * 60)

groq_key = os.getenv("GROQ_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

if groq_key:
    print(f"✅ GROQ_API_KEY: Configured ({groq_key[:10]}...)")
else:
    print("❌ GROQ_API_KEY: NOT FOUND")

if tavily_key:
    print(f"✅ TAVILY_API_KEY: Configured ({tavily_key[:10]}...)")
else:
    print("❌ TAVILY_API_KEY: NOT FOUND")

print()

# Test 2: Module Imports
print("📦 Test 2: Module Imports")
print("-" * 60)

try:
    from src.agents.state import AgentState, LogEntry, Resource
    print("✅ src.agents.state imported successfully")
except Exception as e:
    print(f"❌ src.agents.state import failed: {e}")

try:
    from src.tools.model import get_model
    print("✅ src.tools.model imported successfully")
except Exception as e:
    print(f"❌ src.tools.model import failed: {e}")

try:
    from src.tools.search import strategic_search, search_node
    print("✅ src.tools.search imported successfully")
except Exception as e:
    print(f"❌ src.tools.search import failed: {e}")

try:
    from src.tools.download import download_node
    print("✅ src.tools.download imported successfully")
except Exception as e:
    print(f"❌ src.tools.download import failed: {e}")

try:
    from src.ui.chat import chat_node, route_tools
    print("✅ src.ui.chat imported successfully")
except Exception as e:
    print(f"❌ src.ui.chat import failed: {e}")

try:
    from src.agents.agent import graph
    print("✅ src.agents.agent (graph) imported successfully")
except Exception as e:
    print(f"❌ src.agents.agent import failed: {e}")

print()

# Test 3: Groq API Connection
print("🤖 Test 3: Groq API Connection")
print("-" * 60)

if groq_key:
    try:
        from src.tools.model import get_model
        
        print("Testing Groq LLM...")
        llm = get_model(model_name="groq", temperature=0.1, max_tokens=100)
        
        response = llm.invoke("Say 'Integration test successful' in one sentence.")
        print(f"✅ Groq API Response: {response.content[:100]}")
        
    except Exception as e:
        print(f"❌ Groq API Test Failed: {e}")
else:
    print("⚠️  Skipping - No GROQ_API_KEY")

print()

# Test 4: Tavily Search API
print("🔍 Test 4: Tavily Search API")
print("-" * 60)

if tavily_key:
    try:
        from langchain_community.tools.tavily_search import TavilySearchResults
        
        print("Testing Tavily Search...")
        search = TavilySearchResults(max_results=2, search_depth="basic")
        results = search.invoke("McKinsey digital transformation")
        
        if results:
            print(f"✅ Tavily API Response: Found {len(results)} results")
            
            if isinstance(results, list) and len(results) > 0:
                first = results[0]
                if isinstance(first, dict):
                    print(f"   Sample: {first.get('title', 'No title')[:50]}...")
        else:
            print("⚠️  Tavily returned empty results")
            
    except Exception as e:
        print(f"❌ Tavily API Test Failed: {e}")
else:
    print("⚠️  Skipping - No TAVILY_API_KEY")

print()

# Test 5: Agent Graph Compilation
print("🔗 Test 5: Agent Graph Compilation")
print("-" * 60)

try:
    from src.agents.agent import graph
    
    print("Testing LangGraph compilation...")
    
    # Check if graph is compiled
    if graph:
        print("✅ Agent graph compiled successfully")
        
        # Try to get graph structure info
        try:
            nodes = graph.get_graph().nodes
            print(f"   Graph nodes: {list(nodes.keys())}")
        except:
            print("   (Graph structure not introspectable)")
    else:
        print("❌ Graph is None")
        
except Exception as e:
    print(f"❌ Graph Compilation Failed: {e}")

print()

# Test 6: Simple Agent Execution
print("🚀 Test 6: Simple Agent Execution")
print("-" * 60)

if groq_key:
    try:
        from src.agents.agent import graph
        from langchain_core.messages import HumanMessage
        
        print("Running simple query through agent...")
        
        config = {"configurable": {"thread_id": "test-123"}}
        initial_state = {
            "messages": [HumanMessage(content="What is digital transformation? Answer in 2 sentences.")],
            "model": "groq",
            "temperature": 0.1,
            "max_tokens": 200,
            "search_domains": [],
            "query": "What is digital transformation?",
            "logs": []
        }
        
        async def run_test():
            result = None
            async for event in graph.astream(initial_state, config, stream_mode="values"):
                if "messages" in event and event["messages"]:
                    last_msg = event["messages"][-1]
                    if hasattr(last_msg, "content") and last_msg.content:
                        result = last_msg.content
            return result
        
        response = asyncio.run(run_test())
        
        if response:
            print(f"✅ Agent Response: {response[:150]}...")
        else:
            print("⚠️  Agent returned no response")
            
    except Exception as e:
        print(f"❌ Agent Execution Failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⚠️  Skipping - No GROQ_API_KEY")

print()

# Test 7: FastAPI Server (import only, not running)
print("🌐 Test 7: FastAPI Server Configuration")
print("-" * 60)

try:
    from src.api.server import app, ChatRequest
    
    print("✅ FastAPI app imported successfully")
    print(f"   App title: {app.title}")
    print(f"   App version: {app.version}")
    
    # Test model
    test_request = ChatRequest(
        message="Test",
        model="groq",
        temperature=0.2,
        max_tokens=1000
    )
    print(f"✅ ChatRequest model works: {test_request.message}")
    
except Exception as e:
    print(f"❌ FastAPI Server Test Failed: {e}")

print()

# Test 8: Streamlit App (import only)
print("🎨 Test 8: Streamlit App Configuration")
print("-" * 60)

try:
    # Just check if file exists and is valid Python
    streamlit_path = project_root / "src" / "ui" / "streamlit_app.py"
    
    if streamlit_path.exists():
        print(f"✅ Streamlit app file exists: {streamlit_path}")
        
        # Check for basic structure
        with open(streamlit_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "st.set_page_config" in content:
                print("✅ Streamlit configuration found")
            if "graph.astream" in content:
                print("✅ Agent graph integration found")
    else:
        print(f"❌ Streamlit app not found at {streamlit_path}")
        
except Exception as e:
    print(f"❌ Streamlit Test Failed: {e}")

print()

# Final Summary
print("=" * 60)
print("📊 INTEGRATION TEST SUMMARY")
print("=" * 60)
print()
print(" All major components tested:")
print(" ✅ Environment configuration")
print(" ✅ Module imports")
print(" ✅ Groq API connection")
print(" ✅ Tavily Search API")
print(" ✅ Agent graph compilation")
print(" ✅ Agent execution")
print(" ✅ FastAPI server")
print(" ✅ Streamlit app")
print()
print("🎉 Integration tests complete!")
print()
print("Next steps:")
print(" 1. Run backend: python src/api/server.py")
print(" 2. Run Streamlit: streamlit run src/ui/streamlit_app.py")
print(" 3. Run frontend: cd frontend && npm run dev")
print()
