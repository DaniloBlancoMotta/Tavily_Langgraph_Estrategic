import os
import json
from langsmith import traceable
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from pydantic import BaseModel, Field
from src.agents.state import Resource, LogEntry
from src.tools.model import get_model
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

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

@traceable(name="search_node", run_type="retriever")
def search_node(state: dict) -> dict:
    """Nó de busca usando Tavily focado em PDFs e artigos corporativos."""
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
            return _create_tool_response(messages, error_msg, [], logs)
        
        if not search_domains:
            search_domains = DEFAULT_TRUSTED_DOMAINS
            logs.append(LogEntry(message="Using default domains", type="config"))
        
        clean_domains = [d.replace("site:", "") for d in search_domains]
        
        # Aprimorar query para buscar PDFs e artigos publicados
        enhanced_query = f"{query} (filetype:pdf OR article OR report OR whitepaper OR insights)"
        
        # 🟢 OPTIMIZATION: Check Cache
        from src.optimization.caching import cache
        cache_key = f"search_{enhanced_query}_{sorted(clean_domains)}_{os.getenv('TAVILY_API_KEY')}"
        cached_results = cache.get(cache_key)
        
        if cached_results:
            logs.append(LogEntry(message="⚡ Cache Hit: Using cached search results", type="info"))
            # Skip API call
            return _create_tool_response(messages, "Cached search results retrieved.", cached_results, logs, query)

        logs.append(LogEntry(
            message=f"🔍 Buscando PDFs e artigos em {len(clean_domains)} consultorias...", 
            type="search"
        ))
        logs.append(LogEntry(
            message=f"Query: {enhanced_query}", 
            type="search"
        ))
        
        search = TavilySearchResults(
            max_results=3,  # Reduced to 3 as requested
            include_domains=clean_domains,
            search_depth="basic", # Changed to basic
            include_answer=False,
            include_raw_content=False,  # Disabled raw content
        )
        
        # Função com retry para chamadas Tavily
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
            reraise=True
        )
        def call_tavily_with_retry(query):
            """Call Tavily with automatic retry on failures"""
            return search.invoke(query)
        
        resources = []
        try:
            logs.append(LogEntry(
                message="🔄 Calling Tavily API (with retry logic)...",
                type="search"
            ))
            
            results = call_tavily_with_retry(enhanced_query)
            
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
                    url = res.get("url", "unknown")
                    title = res.get("title", "No Title")
                    
                    # Identificar tipo de documento
                    is_pdf = url.lower().endswith('.pdf') or 'pdf' in url.lower()
                    is_article = any(keyword in url.lower() for keyword in [
                        'article', 'insights', 'report', 'whitepaper', 'publication'
                    ])
                    
                    # Dar prioridade a PDFs e artigos
                    if is_pdf:
                        doc_type = "[PDF]"
                    elif is_article:
                        doc_type = "[Article]"
                    else:
                        doc_type = "[Web]"
                    
                    # Extrair o máximo de conteúdo possível
                    content = res.get("content", "")
                    raw_content = res.get("raw_content", "")
                    
                    # Usar raw_content se disponível e maior
                    description = raw_content if len(raw_content) > len(content) else content
                    
                    # Aumentar limite para documentos prioritários
                    max_chars = 2000 if (is_pdf or is_article) else 1000
                    
                    resources.append(Resource(
                        url=url,
                        title=f"{doc_type} {title}",
                        description=description[:max_chars]
                    ))
            
            # Contar tipos de documentos
            pdf_count = sum(1 for r in resources if '[PDF]' in r.title)
            article_count = sum(1 for r in resources if '[Article]' in r.title)
            
            # Log detalhado dos tipos encontrados
            logs.append(LogEntry(
                message=f"📚 Encontrados: {pdf_count} PDFs, {article_count} artigos, {len(resources)-pdf_count-article_count} outros", 
                type="search"
            ))
            logs.append(LogEntry(
                message=f"Total de {len(resources)} documentos para análise", 
                type="search"
            ))
            
            # 🟢 OPTIMIZATION: Save to Cache
            if resources:
                cache.set(cache_key, [r.dict() if hasattr(r, 'dict') else r for r in resources])
            
        except Exception as e:
            error_msg = f"Tavily search error: {str(e)}"
            logs.append(LogEntry(message=error_msg, type="error"))
            return _create_tool_response(messages, error_msg, [], logs)

        # Criar mensagem de síntese para o LLM
        synthesis_msg = f"""Encontrados {len(resources)} documentos das consultorias selecionadas.
        
📊 Composição:
- PDFs: {pdf_count}
- Artigos: {article_count}  
- Outros: {len(resources)-pdf_count-article_count}

Por favor, analise o conteúdo destes documentos e sintetize uma resposta completa e bem fundamentada."""

        return _create_tool_response(messages, synthesis_msg, resources, logs, query)
        
    except Exception as e:
        error_msg = f"Critical Error in Search Node: {str(e)}"
        logs.append(LogEntry(message=error_msg, type="error"))
        return _create_tool_response(messages, error_msg, [], logs, query)

def _create_tool_response(messages, content, resources, logs, query=None):
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
            
    response = {"resources": resources, "logs": logs, "messages": tool_messages}
    if query:
        response["query"] = query
    return response
