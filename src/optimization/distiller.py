
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.model import get_model
from src.optimization.caching import cache
from langsmith import traceable

class DocumentDistiller:
    """
    Optimization layer to compress long documents into strategic findings.
    Prevents token bloat by summarizing chunks before context injection.
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initialize with a fast/cheap model.
        Args:
            model_name: Default 'gpt-4o-mini' for balance of speed/cost.
        """
        self.model = get_model(model_name)
        self.parser = StrOutputParser()
        
        # Prompt for distillation
        self.distill_prompt = ChatPromptTemplate.from_template(
            """
            Analyze the following text chunk from a strategic document.
            Extract ONLY:
            1. Key strategic insights (Market trends, risks, opportunities)
            2. Hard data/Statistics (percentages, $$$ values)
            3. Direct quotes if extremely impactful.

            Query focus (if any): {query}

            If the text contains nothing relevant to strategy or the query, return "NO_RELEVANT_INFO".
            Keep it concise (bullet points).

            Text Chunk:
            {chunk}
            """
        )
        self.chain = self.distill_prompt | self.model | self.parser

    @traceable(name="distill_content", run_type="chain")
    async def distill(self, text: str, query: str = "", chunk_size: int = 4000) -> str:
        """
        Distills a long text into a compressed summary.
        Uses caching to avoid re-processing same text.
        """
        # Cache Key: Hash of text + query
        cache_key = f"distill_{hash(text)}_{hash(query)}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return f"[FROM CACHE] {cached_result}"

        # If text is small enough, process directly
        if len(text) < chunk_size:
            result = await self.chain.ainvoke({"chunk": text, "query": query})
            if "NO_RELEVANT_INFO" in result:
                return ""
            cache.set(cache_key, result)
            return result

        # Chunking strategy (Simple split for now)
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        distilled_chunks = []
        
        # Parallel processing could be added here, but doing sequential for safety first
        for chunk in chunks:
            try:
                # We assume chain.ainvoke handles the async call to LLM
                chunk_result = await self.chain.ainvoke({"chunk": chunk, "query": query})
                if "NO_RELEVANT_INFO" not in chunk_result:
                    distilled_chunks.append(chunk_result)
            except Exception as e:
                distilled_chunks.append(f"[Error distilling chunk: {e}]")

        final_summary = "\n---\n".join(distilled_chunks)
        
        # Save to cache
        cache.set(cache_key, final_summary)
        
        return final_summary

# Singleton
distiller = DocumentDistiller()
