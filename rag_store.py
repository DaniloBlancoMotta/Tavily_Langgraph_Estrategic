"""
RAG Store for StratGov AI - Strategic Knowledge Base
Provides semantic search over consulting documents and frameworks.
"""
import os
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from state import Resource, LogEntry


class StrategyRAG:
    """Vector store for strategic consulting knowledge."""
    
    def __init__(self, persist_directory: str = "./strategy_db"):
        """Initialize RAG with OpenAI embeddings and Chroma."""
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
        
        # Load existing store or create new one
        if os.path.exists(persist_directory):
            self.vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings
            )
        else:
            self.vectorstore = None
    
    def index_documents(self, docs: List[Document]) -> None:
        """Index documents into the vector store."""
        if self.vectorstore is None:
            self.vectorstore = Chroma.from_documents(
                documents=docs,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
        else:
            self.vectorstore.add_documents(docs)
    
    def search(self, query: str, k: int = 5) -> List[Document]:
        """Semantic search over indexed documents."""
        if self.vectorstore is None:
            return []
        return self.vectorstore.similarity_search(query, k=k)
    
    def search_with_scores(self, query: str, k: int = 5) -> List[tuple]:
        """Search with relevance scores."""
        if self.vectorstore is None:
            return []
        return self.vectorstore.similarity_search_with_score(query, k=k)
    
    def to_resources(self, docs: List[Document]) -> List[Resource]:
        """Convert Documents to Resource objects for state."""
        resources = []
        for doc in docs:
            resources.append(Resource(
                url=doc.metadata.get("source", "internal_kb"),
                title=doc.metadata.get("title", "Strategy Document"),
                description=doc.page_content[:500]
            ))
        return resources


# Global RAG instance
_rag_instance: Optional[StrategyRAG] = None


def get_rag() -> StrategyRAG:
    """Get or create global RAG instance."""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = StrategyRAG()
    return _rag_instance
