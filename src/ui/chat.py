import logging
from langchain_core.messages import SystemMessage, AIMessage

logger = logging.getLogger("StratGov_Agent")
from src.agents.state import AgentState, LogEntry
from src.tools.model import get_model
from src.tools.search import strategic_search

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
    
    try:
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
        
    except Exception as e:
        error_msg = f"Primary model ({model_name}) failed: {str(e)}"
        logger.error(error_msg)
        logs.append(LogEntry(message=error_msg, type="warning"))
        
        # Fallback Logic
        fallback_map = {
            "groq": "mixtral",       # Llama -> Mixtral
            "llama": "mixtral",      # Llama -> Mixtral
            "mixtral": "groq",       # Mixtral -> Llama
            "kimi": "groq"           # Kimi -> Llama
        }
        
        # Determine fallback model name (internal key, not full ID)
        current_key = "groq" # Default assumption
        if "mixtral" in model_name or "mixtral" == model_name: current_key = "mixtral"
        elif "kimi" in model_name: current_key = "kimi"
        elif "llama" in model_name: current_key = "llama"
        
        fallback_key = fallback_map.get(current_key, "groq")
        
        # Prevent infinite loop if fallback is same as current (generic safety)
        if fallback_key == current_key:
             fallback_key = "mixtral" if current_key == "groq" else "groq"

        logs.append(LogEntry(message=f"🔄 Switching to fallback model: {fallback_key.upper()}...", type="info"))
        
        try:
            fallback_llm = get_model(
                model_name=fallback_key,
                temperature=temperature,
                max_tokens=max_tokens
            )
            fallback_llm_with_tools = fallback_llm.bind_tools(tools)
            
            response = fallback_llm_with_tools.invoke(messages)
            
            # Add note about fallback usage
            if isinstance(response.content, str):
                response.content += f"\n\n*(Generated via fallback model: {fallback_key})*"
            
            return {"messages": [response], "logs": logs}
            
        except Exception as e2:
            critical_msg = f"Critical: Fallback model ({fallback_key}) also failed: {str(e2)}"
            logger.error(critical_msg, exc_info=True)
            logs.append(LogEntry(message=critical_msg, type="error"))
            
            # Return graceful error message
            fallback_response = AIMessage(
                content=f"⚠️ **System Unavailable**: Both primary and backup AI models are currently unresponsive.\n\nError: `{str(e2)}`\n\nPlease try again later."
            )
            return {"messages": [fallback_response], "logs": logs}

def route_tools(state: AgentState) -> str:
    """Roteamento baseado em tool calls."""
    last_message = state["messages"][-1]
    
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "search"
    
    return "end"
