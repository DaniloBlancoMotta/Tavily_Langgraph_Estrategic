import os
from dotenv import load_dotenv
from langsmith import traceable
from langchain_groq import ChatGroq

load_dotenv()

@traceable(name="get_model", run_type="llm")
def get_model(model_name: str = "llama-3.3-70b-versatile", temperature: float = 0.2, max_tokens: int = 4096):
    """Dynamic LLM selection via Groq with UX controls."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found")

    model_map = {
        "groq": "llama-3.3-70b-versatile",
        "llama": "llama-3.3-70b-versatile",
        "mixtral": "mixtral-8x7b-32768",
        "kimi": "moonshotai/kimi-k2-instruct-0905",
        "openai": "gpt-4o",
        "gpt-4o": "gpt-4o",
        "gpt-4o-mini": "gpt-4o-mini",
        "smart": "gpt-4o",
        "fast": "gpt-4o-mini"
    }
    
    selected_model = model_map.get(model_name, model_name)
    
    # Check for OpenAI models
    if "gpt" in selected_model or "openai" in selected_model:
        from langchain_openai import ChatOpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
             # Fallback to Groq if OpenAI key missing but requested (safeguard)
             selected_model = "llama-3.3-70b-versatile"
        else:
            return ChatOpenAI(
                model=selected_model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=openai_key
            )

    return ChatGroq(
        temperature=temperature,
        model_name=selected_model,
        api_key=api_key,
        max_retries=2,
        max_tokens=max_tokens
    )
