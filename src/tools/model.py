import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_model(model_name: str = "llama-3.3-70b-versatile", temperature: float = 0.2, max_tokens: int = 4096):
    """Dynamic LLM selection via Groq with UX controls."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found")

    model_map = {
        "groq": "llama-3.3-70b-versatile",
        "llama": "llama-3.3-70b-versatile",
        "mixtral": "mixtral-8x7b-32768",
        "kimi": "moonshotai/kimi-k2-instruct-0905"
    }
    
    selected_model = model_map.get(model_name, model_name)
    
    return ChatGroq(
        temperature=temperature,
        model_name=selected_model,
        api_key=api_key,
        max_retries=2,
        max_tokens=max_tokens
    )
