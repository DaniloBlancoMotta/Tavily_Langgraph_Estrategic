try:
    print("Tentando langchain_tavily...")
    from langchain_tavily import TavilySearchResults
    print("Success langchain_tavily")
except ImportError as e:
    print(f"Falha langchain_tavily: {e}")

try:
    print("Tentando langchain_community...")
    from langchain_community.tools.tavily_search import TavilySearchResults
    print("Success langchain_community")
except ImportError as e:
    print(f"Falha langchain_community: {e}")
