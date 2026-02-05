import asyncio
import re
import httpx
from langsmith import traceable
from bs4 import BeautifulSoup
from pypdf import PdfReader
from io import BytesIO
from src.agents.state import LogEntry
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@traceable(name="extract_text_from_pdf", run_type="parser")
def extract_text_from_pdf(pdf_bytes: bytes, query: str = "") -> str:
    """Extrai apenas seções relevantes de um PDF baseado na query."""
    try:
        pdf_file = BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        
        relevant_chunks = []
        query_terms = [t.lower() for t in query.split()] if query else []
        
        # Limitar a 30 páginas para análise
        max_pages = min(30, len(reader.pages))
        
        scored_pages = []
        
        for page_num in range(max_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            if not text:
                continue
                
            # Score page based on query terms
            if query_terms:
                text_lower = text.lower()
                score = sum(1 for term in query_terms if term in text_lower)
            else:
                score = 1 # Keep all if no query (up to limit)
                
            scored_pages.append((score, page_num, text))
            
        # Filter and Sort: Get top 3 most relevant pages, or first 3 if no query
        # Sort by score desc, then page_num
        scored_pages.sort(key=lambda x: x[0], reverse=True)
        top_pages = scored_pages[:3]
        
        # Re-sort by page number to keep reading flow
        top_pages.sort(key=lambda x: x[1])
        
        summary_text = []
        for score, num, text in top_pages:
            if score > 0 or not query:
                # Basic cleaning
                clean_text = " ".join(text.split())
                summary_text.append(f"[Page {num+1} - Relevance Score: {score}]\n{clean_text[:1500]}...") # Truncate per page
        
        final_text = "\n\n".join(summary_text)
        
        if not final_text:
            return "[PDF processado mas nenhum conteúdo relevante encontrado para a query]"
            
        # 🟢 OPTIMIZATION: Distill content using LLM
        # Instead of returning raw text chunks, we summarize them
        try:
            from src.optimization.distiller import distiller
            # We must use sync await or run in event loop if called from sync function
            # Since this function is sync but called from an async workflow, we can use runners or
            # better yet, make this function async? But it's decorated with @traceable wrapper...
            # The safer bet for now is to return the raw text chunks but trimmed, 
            # and let the calling async function handle the distillation if possible,
            # OR use a sync wrapper for the distiller. 
            
            # Given constraints, we will optimize the RAW extraction itself to be very dense.
            # But the REAL gain is calling the distiller.
            # Let's import run_in_executor or use asyncio.run if safe (not nested).
            # Actually, `extract_text_from_pdf` is called by `process_resource` which is ASYNC.
            # So we can rename this to async and await it?
            # Let's keep it sync for now but return text. The calling function `process_resource` 
            # will handle the distillation to keep this function pure-ish.
            pass
        except:
            pass
            
        return final_text
        
    except Exception as e:
        return f"[Erro ao extrair PDF: {str(e)}]"

def html_to_text(html: str) -> str:
    """Converte HTML para texto limpo - otimizado para artigos longos."""
    soup = BeautifulSoup(html, "html.parser")
    
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
        tag.decompose()
    
    text = soup.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    # Aumentado de 150 para 300 linhas para capturar mais conteúdo
    return "\n".join(lines[:300])  

@traceable(name="process_resource", run_type="tool")
async def process_resource(client, resource, logs, query=""):
    """Downloads and processes a single resource (HTML or PDF)."""
    try:
        # Identificar se é PDF
        is_pdf = resource.url.lower().endswith('.pdf') or 'pdf' in resource.url.lower()
        
        if is_pdf:
            logs.append(LogEntry(
                message=f"📄 Baixando PDF: {resource.title}", 
                type="download"
            ))
            
            try:
                # Baixar o PDF
                response = await client.get(resource.url, follow_redirects=True, timeout=30.0)
                
                if response.status_code == 200:
                    # Extrair texto do PDF
                    pdf_text = extract_text_from_pdf(response.content, query)
                    
                    # 🟢 OPTIMIZATION: Distill Content
                    from src.optimization.distiller import distiller
                    logs.append(LogEntry(message=f"🧠 Distilling PDF content with {distiller.model.model_name}...", type="info"))
                    distilled_text = await distiller.distill(pdf_text, query)
                    
                    # Informar sucesso com detalhes
                    word_count = len(pdf_text.split())
                    new_word_count = len(distilled_text.split())
                    compression_ratio = round((1 - new_word_count/word_count) * 100, 1) if word_count > 0 else 0
                    
                    logs.append(LogEntry(
                        message=f"✅ PDF extraído & Destilado: {word_count} -> {new_word_count} palavras (-{compression_ratio}%)", 
                        type="download"
                    ))
                    
                    resource.content = f"[PDF Insights - Distilled from {resource.title}]\n\n{distilled_text}"
                    return True
                else:
                    logs.append(LogEntry(
                        message=f"⚠️ HTTP {response.status_code} ao baixar PDF: {resource.title}", 
                        type="error"
                    ))
                    # Fallback para descrição Tavily
                    resource.content = f"[PDF - Download falhou] {resource.description}"
                    return False
                    
            except Exception as pdf_error:
                logs.append(LogEntry(
                    message=f"❌ Erro ao processar PDF {resource.title}: {str(pdf_error)[:100]}", 
                    type="error"
                ))
                # Fallback para descrição Tavily
                resource.content = f"[PDF - Erro na extração] {resource.description}"
                return False
        
        # Para documentos HTML/artigos
        logs.append(LogEntry(message=f"📥 Baixando: {resource.title}", type="download"))
        
        response = await client.get(resource.url, follow_redirects=True)
        if response.status_code == 200:
            content = html_to_text(response.text)
            
            # 🟢 OPTIMIZATION: Distill HTML too if it's long
            if len(content) > 3000:
                from src.optimization.distiller import distiller
                logs.append(LogEntry(message="🧠 Distilling Article content...", type="info"))
                content = await distiller.distill(content, query)
            
            resource.content = content if content else resource.description
            return True
        else:
            logs.append(LogEntry(
                message=f"⚠️ HTTP {response.status_code}: {resource.title}", 
                type="error"
            ))
            # Manter descrição Tavily mesmo se download falhar
            resource.content = resource.description
            return False
    except Exception as e:
        logs.append(LogEntry(
            message=f"❌ Erro {resource.title}: {str(e)[:100]}", 
            type="error"
        ))
        # Fallback para descrição do Tavily
        resource.content = resource.description
        return False

@traceable(name="download_node", run_type="tool")
async def download_node(state: dict) -> dict:
    """Async node handling parallel resource downloads."""
    resources = state.get("resources", [])
    logs = state.get("logs", [])
    query = state.get("query", "")
    
    try:
        if not resources:
            return {"logs": logs}
        
        logs.append(LogEntry(message=f"Starting parallel downloads for {len(resources)} sources...", type="download"))
        
        async with httpx.AsyncClient(timeout=10.0, headers={"User-Agent": "StratGovBot/1.0"}) as client:
            tasks = [process_resource(client, res, logs, query) for res in resources]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculate success considering exceptions in results (since return_exceptions=True)
        success_count = sum(1 for r in results if r is True)
        logs.append(LogEntry(message=f"Downloads completed: {success_count}/{len(resources)}", type="download"))
        
        return {"resources": resources, "logs": logs}
        
    except Exception as e:
        error_msg = f"Critical Error in Download Node: {str(e)}"
        print(error_msg) # Fallback if logger not available, but we should probably use logger
        logs.append(LogEntry(message=error_msg, type="error"))
        return {"resources": resources, "logs": logs}
