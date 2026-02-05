from typing import Annotated, List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

class Resource(BaseModel):
    """Resource found in search."""
    url: str
    title: str
    description: str
    content: Optional[str] = None

class LogEntry(BaseModel):
    """Log entry for streaming."""
    message: str
    type: str = "info"  # info, search, download, error, config

class AgentState(TypedDict):
    """Agent state with UX configuration."""
    messages: Annotated[list[AnyMessage], add_messages]
    model: str
    temperature: float
    max_tokens: int
    search_domains: List[str]
    query: str
    report: str
    resources: List[Resource]
    logs: List[LogEntry]
    iteration_count: int = 0
