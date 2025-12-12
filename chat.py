from langchain_core.messages import SystemMessage, AIMessage
from state import AgentState, LogEntry
from model import get_model
from search import strategic_search

SYSTEM_PROMPT = """You are StratGov AI, a Senior Strategy & Governance Consultant.
Your goal is to provide comprehensive, deep, and actionable strategic advice.

RESPONSE GUIDELINES:
1. **Structure**: Use Markdown headers (##, ###) to organize the answer into logical topics.
2. **Depth**: Provide detailed explanations, not just summaries. Aim for long, analytical responses.
3. **Evidence-Based**: Strictly use the provided search context. Cite sources inline or at the end.
4. **Professional Tone**: Use executive, consulting-style language (McKinsey/Gartner style).
5. **Formatting**: Use bullet points, bold text for emphasis, and clear paragraphs.

If you don't have enough information, explicitly ask for more context or suggest a new search."""

tools = [strategic_search]

def chat_node(state: AgentState) -> dict:
    """Nó principal de chat usando configurações do estado."""
    messages = state["messages"]
    logs = state.get("logs", [])
    resources = state.get("resources", [])
    
    # Configurações de UX
    model_name = state.get("model", "groq")
    temperature = state.get("temperature", 0.2)
    max_tokens = state.get("max_tokens", 4096)
    search_domains = state.get("search_domains", [])

    # Injeta system prompt
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    
    # Injeta restrição de domínio se houver
    if search_domains:
        domain_list = ", ".join(search_domains)
        messages.append(SystemMessage(content=f"STRICT CONSTRAINT: You are restricted to using information ONLY from the following sources: {domain_list}. Do not cite or hallucinate information from other sources."))
    
    # Adiciona contexto de recursos
    if resources:
        context = "\n".join([f"- {r.title}: {r.description}" for r in resources])
        messages.append(SystemMessage(content=f"Recursos disponíveis (Use estas informações):\n{context}"))
    
    # Instancia modelo com configs
    llm = get_model(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )
    llm_with_tools = llm.bind_tools(tools)
    
    logs.append(LogEntry(message=f"Generating response ({model_name}, T={temperature})", type="info"))
    
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response], "logs": logs}

def route_tools(state: AgentState) -> str:
    """Roteamento baseado em tool calls."""
    last_message = state["messages"][-1]
    
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "search"
    
    return "end"
