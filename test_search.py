import os
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from search import search_node

load_dotenv()

# Mock message with tool call
mock_msg = AIMessage(
    content="Calling check...",
    tool_calls=[{"name": "strategic_search", "args": {"query": "Strategic trends AI 2025"}, "id": "test_id_123"}]
)

# Mock state
state = {
    "query": "Strategic trends AI 2025",
    "logs": [],
    "search_domains": [], # Trigger default domains
    "messages": [mock_msg]
}

print("Running search test with default domains...")
result = search_node(state)

with open("search_results_log.txt", "w", encoding="utf-8") as f:
    f.write("Resources found:\n")
    for res in result.get("resources", []):
        f.write(f"- {res.url}\n  Desc: {res.description}\n")
    
    f.write("\nLogs:\n")
    for log in result.get("logs", []):
        f.write(f"[{log.type}] {log.message}\n")

print("Done. Check search_results_log.txt")
