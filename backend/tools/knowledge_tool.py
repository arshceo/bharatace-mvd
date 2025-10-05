"""
Knowledge Search Tool
Searches the general knowledge base using the RAG pipeline.
"""

from typing import Dict, Any
import logging
from llama_index.core import VectorStoreIndex

logger = logging.getLogger(__name__)


def search_general_knowledge(query: str, index: VectorStoreIndex = None) -> Dict[str, Any]:
    """
    Search the general knowledge base for information.
    
    This tool uses the RAG pipeline to find relevant information from the
    knowledge_base table containing general university information.
    
    Args:
        query: The search query
        index: The VectorStoreIndex instance (injected by the agent)
        
    Returns:
        Dictionary containing the search results
        
    Example:
        result = search_general_knowledge("What are the library hours?")
        # Returns: {"answer": "The library is open from 8 AM to 10 PM...", "sources": [...]}
    """
    try:
        if index is None:
            logger.error("VectorStoreIndex not provided")
            return {
                "answer": "Knowledge base is not available",
                "sources": [],
                "success": False
            }
        
        logger.info(f"Searching knowledge base for: {query}")
        
        # Create query engine from index
        query_engine = index.as_query_engine(
            similarity_top_k=5,
            response_mode="compact"
        )
        
        # Query the knowledge base
        response = query_engine.query(query)
        
        # Extract source documents
        sources = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                sources.append({
                    "category": node.node.metadata.get('category', 'Unknown'),
                    "content": node.node.text[:200] + "..." if len(node.node.text) > 200 else node.node.text,
                    "score": float(node.score) if hasattr(node, 'score') else 0.0
                })
        
        logger.info(f"Found {len(sources)} relevant sources")
        
        return {
            "answer": str(response),
            "sources": sources,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error searching knowledge base: {str(e)}")
        return {
            "answer": f"Error searching knowledge base: {str(e)}",
            "sources": [],
            "success": False
        }


def search_knowledge_by_category(category: str, index: VectorStoreIndex = None) -> Dict[str, Any]:
    """
    Search the knowledge base filtered by category.
    
    Args:
        category: The category to filter by (e.g., "Library", "Admissions")
        index: The VectorStoreIndex instance
        
    Returns:
        Dictionary containing the filtered results
    """
    try:
        if index is None:
            return {
                "results": [],
                "success": False,
                "message": "Knowledge base not available"
            }
        
        logger.info(f"Searching knowledge base by category: {category}")
        
        # Query with category filter
        query_engine = index.as_query_engine(
            similarity_top_k=10,
            response_mode="tree_summarize",
            filters={"category": category}
        )
        
        response = query_engine.query(f"Tell me about {category}")
        
        return {
            "answer": str(response),
            "category": category,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error searching by category: {str(e)}")
        return {
            "results": [],
            "success": False,
            "message": str(e)
        }

