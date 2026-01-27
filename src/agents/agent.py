import logging
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from src.agents.state import AgentState
from src.ui.chat import chat_node, route_tools
from src.tools.search import search_node, strategic_search
from src.tools.download import download_node
# from rag_search import rag_search_node  # NEW: RAG integration (Files missing, commented out)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StratGov_Agent")


builder = StateGraph(AgentState)

builder.add_node("chat", chat_node)
builder.add_node("search", search_node)
builder.add_node("download", download_node)
builder.add_node("tools", ToolNode([strategic_search]))

# Edges and Flow
builder.add_edge(START, "chat")
builder.add_conditional_edges(
    "chat",
    route_tools,
    {
        "search": "search",
        "end": END
    }
)
builder.add_edge("search", "download")
builder.add_edge("download", "chat")
builder.add_edge("tools", "chat")

# Memory and Checkpointing
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

logger.info("StratGov Graph compiled successfully")
