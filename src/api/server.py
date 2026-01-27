import sys
from pathlib import Path
# Add project root to path if needed
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

# Safe import of ssl_fix (optional dependency)
try:
    from scripts import ssl_fix
except ImportError:
    pass  # ssl_fix is optional

import json
import uuid
import uvicorn
from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from src.agents.agent import graph

app = FastAPI(
    title="StratGov AI Server",
    description="Strategic Governance Agent with LangGraph",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None
    model: str = "groq"
    temperature: float = 0.2
    max_tokens: int = 4096
    search_domains: Optional[List[str]] = None

async def stream_response(request: ChatRequest, thread_id: str):
    """Stream NDJSON with logs and response."""
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "messages": [HumanMessage(content=request.message)],
        "model": request.model,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
        "search_domains": request.search_domains or [],
        "query": request.message,
        "report": "",
        "resources": [],
        "logs": []
    }
    
    try:
        async for event in graph.astream(initial_state, config, stream_mode="updates"):
            for node_name, node_data in event.items():
                if "logs" in node_data:
                    for log in node_data["logs"]:
                        yield json.dumps({
                            "type": "log",
                            "message": log.message if hasattr(log, 'message') else str(log),
                            "node": node_name
                        }) + "\n"
                
                if "messages" in node_data:
                    for msg in node_data["messages"]:
                        if hasattr(msg, "content") and msg.content:
                            yield json.dumps({
                                "type": "answer",
                                "content": msg.content
                            }) + "\n"
                
                if "resources" in node_data and node_data["resources"]:
                    yield json.dumps({
                        "type": "resources",
                        "data": [{"url": r.url, "title": r.title} for r in node_data["resources"]]
                    }) + "\n"
                    
    except Exception as e:
        yield json.dumps({"type": "error", "message": str(e)}) + "\n"

@app.post("/api/chat")
async def chat(request: ChatRequest):
    thread_id = request.thread_id or str(uuid.uuid4())
    return StreamingResponse(
        stream_response(request, thread_id),
        media_type="application/x-ndjson"
    )

@app.get("/health")
async def health():
    return {"status": "active", "service": "StratGov_Agent", "version": "2.1.0"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
