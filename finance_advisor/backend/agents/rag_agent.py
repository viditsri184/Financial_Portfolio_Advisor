# backend/agents/rag_agent.py

from typing import List, Dict, Any

from ..rag.retriever import retrieve_top_k


class RAGAgent:
    """
    The agent responsible for regulatory lookup.
    """

    @staticmethod
    def lookup(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Returns top-k relevant text chunks from the vector store.
        """
        return retrieve_top_k(query, top_k)


rag_agent = RAGAgent()
