import asyncio
import httpx
from bs4 import BeautifulSoup
from state import LogEntry

def html_to_text(html: str) -> str:
    """Converte HTML para texto limpo (CPU-bound, rápido)."""
    soup = BeautifulSoup(html, "html.parser")
    
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
        tag.decompose()
    
    text = soup.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines[:150])  # Aumentado limite levemente

async def process_resource(client, resource, logs):
    """Downloads and processes a single resource."""
    try:
        logs.append(LogEntry(message=f"Downloading: {resource.title}", type="download"))
        
        response = await client.get(resource.url, follow_redirects=True)
        if response.status_code == 200:
            content = html_to_text(response.text)
            resource.content = content
            return True
        else:
            logs.append(LogEntry(message=f"HTTP Error {response.status_code}: {resource.title}", type="error"))
            return False
    except Exception as e:
        logs.append(LogEntry(message=f"Failed {resource.title}: {str(e)[:50]}", type="error"))
        return False

async def download_node(state: dict) -> dict:
    """Async node handling parallel resource downloads."""
    resources = state.get("resources", [])
    logs = state.get("logs", [])
    
    if not resources:
        return {"logs": logs}
    
    logs.append(LogEntry(message=f"Starting parallel downloads for {len(resources)} sources...", type="download"))
    
    async with httpx.AsyncClient(timeout=10.0, headers={"User-Agent": "StratGovBot/1.0"}) as client:
        tasks = [process_resource(client, res, logs) for res in resources]
        results = await asyncio.gather(*tasks)
    
    success_count = sum(1 for r in results if r)
    logs.append(LogEntry(message=f"Downloads completed: {success_count}/{len(resources)}", type="download"))
    
    return {"resources": resources, "logs": logs}
