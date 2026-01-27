import os
import json
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from pydantic import BaseModel, Field
from state import Resource, LogEntry
from model import get_model

# Domínios confiáveis padrão
DEFAULT_TRUSTED_DOMAINS = [
    "mckinsey.com",
    "bcg.com",
    "bain.com", 
    "gartner.com", 
    "ey.com",
    "hbr.org",
    "mit.edu"
]

class SearchInput(BaseModel):
    query: str = Field(description="Query de busca.")

@tool("strategic_search", args_schema=SearchInput)
def strategic_search(query: str) -> str:
    """Ferramenta de busca estratégica."""
    return f"Search triggered for: {query}"

def search_node(state: dict) -> dict:
    """Nó de busca usando Tavily e retornando ToolMessage."""
    query = state.get("query", "")
    logs = state.get("logs", [])
    search_domains = state.get("search_domains", [])
    messages = state.get("messages", [])
    
    try:
        # Try to extract query from the last tool call
        if messages and hasattr(messages[-1], "tool_calls") and messages[-1].tool_calls:
            tool_call = messages[-1].tool_calls[0]
            if "args" in tool_call and "query" in tool_call["args"]:
                query = tool_call["args"]["query"]
                logs.append(LogEntry(message=f"Optimized Query: {query}", type="search"))
        
        # API Key validation
        if not os.getenv("TAVILY_API_KEY"):
            error_msg = "Error: TAVILY_API_KEY not configured in .env"
            logs.append(LogEntry(message=error_msg, type="error"))
            # Retorna erro para o LLM também
            return _create_tool_response(messages, error_msg, [], logs)
        
        if not search_domains:
            search_domains = DEFAULT_TRUSTED_DOMAINS
            logs.append(LogEntry(message="Using default domains", type="config"))
        
        clean_domains = [d.replace("site:", "") for d in search_domains]
        logs.append(LogEntry(message=f"Searching via Tavily in {len(clean_domains)} sources...", type="search"))
        
        search = TavilySearchResults(
            max_results=10,
            include_domains=clean_domains,
            search_depth="advanced"
        )
        
        resources = []
        try:
            results = search.invoke(query)
            
            # Debug parsing
            if isinstance(results, str):
                # If plain string returned, try to parse or wrap it
                try:
                    # Sometimes it returns a JSON string
                    results = json.loads(results)
                except:
                    # Or just treat as single content
                    results = [{"url": "search_result", "title": "Search Result", "content": results}]
            
            for res in results:
                if isinstance(res, str):
                    resources.append(Resource(
                        url="unknown",
                        title="Search Snippet",
                        description=res[:500]
                    ))
                elif isinstance(res, dict):
                    resources.append(Resource(
                        url=res.get("url", "unknown"),
                        title=res.get("title", "No Title"),
                        description=res.get("content", "")[:500]
                    ))
            
            logs.append(LogEntry(message=f"Found {len(resources)} resources via Tavily", type="search"))
            
        except Exception as e:
            error_msg = f"Tavily search error: {str(e)}"
            logs.append(LogEntry(message=error_msg, type="error"))
            return _create_tool_response(messages, error_msg, [], logs)

        return _create_tool_response(messages, f"Found {len(resources)} resources.", resources, logs)
        
    except Exception as e:
        error_msg = f"Critical Error in Search Node: {str(e)}"
        logs.append(LogEntry(message=error_msg, type="error"))
        return _create_tool_response(messages, error_msg, [], logs)

def _create_tool_response(messages, content, resources, logs):
    """Helper para criar ToolMessages correspondentes."""
    last_msg = messages[-1]
    tool_messages = []
    
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
        for tc in last_msg.tool_calls:
            tool_messages.append(ToolMessage(
                content=content,
                tool_call_id=tc["id"],
                name=tc["name"]
            ))
            
    return {"resources": resources, "logs": logs, "messages": tool_messages}
