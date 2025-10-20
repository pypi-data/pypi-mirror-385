"""Semantic Search Service for Memory System

Provides advanced semantic search capabilities across different memory types
with performance optimization and caching mechanisms.
"""

from typing import List, Tuple, Optional, Dict, Any
from abc import ABC, abstractmethod
import logging
import asyncio
from datetime import datetime
from enum import Enum

from .models.conversation import ConversationMemory
from .models.config_insight import ConfigurationInsight
from .models.agent_knowledge import AgentKnowledge
from .models.project_context import ProjectContext
from .models.association import MemoryAssociation, MemoryType
from .storage.base import StorageManager
from .config import MemoryConfig

logger = logging.getLogger(__name__)


class SearchScoreType(str, Enum):
    """Types of search scores that can be returned."""
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    BM25 = "bm25"
    CUSTOM = "custom"


class SearchResult:
    """Represents a search result with associated metadata."""
    
    def __init__(self, memory_object: Any, relevance_score: float, 
                 score_type: SearchScoreType = SearchScoreType.SEMANTIC,
                 metadata: Optional[Dict[str, Any]] = None):
        self.memory_object = memory_object
        self.relevance_score = relevance_score
        self.score_type = score_type
        self.metadata = metadata or {}
        self.search_time = datetime.now()
        self.ranking = 0  # Will be set when results are sorted
    
    def __repr__(self):
        return f"SearchResult(score={self.relevance_score:.3f}, type={type(self.memory_object).__name__})"


class BaseSearchService(ABC):
    """Abstract base class for search services."""
    
    @abstractmethod
    async def search(self, query: str, limit: int = 10, 
                     memory_types: Optional[List[MemoryType]] = None,
                     project_id: Optional[str] = None) -> List[SearchResult]:
        """Perform a semantic search."""
        pass
    
    @abstractmethod
    async def batch_search(self, queries: List[str], limit: int = 10) -> List[List[SearchResult]]:
        """Perform multiple searches efficiently."""
        pass


class SemanticSearchService(BaseSearchService):
    """Optimized semantic search service for memory system."""
    
    def __init__(self, storage: StorageManager, config: MemoryConfig):
        self.storage = storage
        self.config = config
        self._query_cache = {}  # Simple in-memory cache
        self.cache_ttl = config.get('search.cache_ttl', 300)  # 5 minutes default
        
        # Performance tracking
        self.search_count = 0
        self.total_search_time = 0.0
    
    async def search(self, query: str, limit: int = 10, 
                     memory_types: Optional[List[MemoryType]] = None,
                     project_id: Optional[str] = None) -> List[SearchResult]:
        """Perform optimized semantic search across memory types.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            memory_types: Optional list of memory types to search
            project_id: Optional project filter
            
        Returns:
            List of SearchResult objects sorted by relevance
        """
        start_time = datetime.now()
        
        # Check cache first
        cache_key = f"{query}:{limit}:{memory_types}:{project_id}"
        if cache_key in self._query_cache:
            cached_result, timestamp = self._query_cache[cache_key]
            # Check if cache is still valid (within TTL)
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                logger.debug(f"Cache hit for query: {query[:50]}...")
                return cached_result
        
        # Build metadata filter
        where = {}
        if memory_types:
            where["type"] = {"$in": [mt.value for mt in memory_types]}
        if project_id:
            where["project_id"] = project_id
        
        # Perform vector search
        search_results = await self.storage.vector_store.search(
            query=query,
            limit=limit,
            where=where
        )
        
        results = []
        
        # Process each result based on its memory type
        for memory_id, score in search_results:
            # Fetch the full memory object from metadata store
            memory_record = await self.storage.metadata_store.get(memory_id)
            
            if not memory_record:
                logger.warning(f"Memory record not found for ID: {memory_id}")
                continue
            
            memory_type = MemoryType(memory_record["metadata"]["type"])
            memory_data = memory_record["data"]
            
            # Reconstruct the appropriate memory object based on type
            memory_obj = None
            if memory_type == MemoryType.CONVERSATION:
                memory_obj = ConversationMemory(**memory_data)
            elif memory_type == MemoryType.CONFIGURATION_INSIGHT:
                memory_obj = ConfigurationInsight(**memory_data)
            elif memory_type == MemoryType.AGENT_KNOWLEDGE:
                memory_obj = AgentKnowledge(**memory_data)
            elif memory_type == MemoryType.PROJECT_CONTEXT:
                memory_obj = ProjectContext(**memory_data)
            
            if memory_obj:
                result = SearchResult(
                    memory_object=memory_obj,
                    relevance_score=score,
                    score_type=SearchScoreType.SEMANTIC,
                    metadata=memory_record["metadata"]
                )
                results.append(result)
        
        # Sort results by relevance score (descending)
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        # Add rankings
        for i, result in enumerate(results):
            result.ranking = i + 1
        
        # Cache the results
        self._query_cache[cache_key] = (results, datetime.now())
        
        # Performance tracking
        search_duration = (datetime.now() - start_time).total_seconds()
        self.search_count += 1
        self.total_search_time += search_duration
        
        logger.debug(f"Search completed for query '{query[:30]}...' in {search_duration:.3f}s. Found {len(results)} results.")
        
        return results
    
    async def batch_search(self, queries: List[str], limit: int = 10) -> List[List[SearchResult]]:
        """Perform multiple searches efficiently.
        
        Args:
            queries: List of search query strings
            limit: Maximum number of results per query
            
        Returns:
            List of result lists, one for each query
        """
        tasks = [self.search(query, limit) for query in queries]
        results = await asyncio.gather(*tasks)
        return results
    
    async def hybrid_search(self, query: str, limit: int = 10,
                           keyword_weight: float = 0.3,
                           semantic_weight: float = 0.7) -> List[SearchResult]:
        """Perform hybrid search combining semantic and keyword search.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            keyword_weight: Weight for keyword search results (0-1)
            semantic_weight: Weight for semantic search results (0-1)
            
        Returns:
            List of SearchResult objects with combined scores
        """
        # First perform semantic search
        semantic_results = await self.search(query, limit=limit * 2)  # Get more results for hybrid
        
        # TODO: Implement keyword search using full-text index
        # For now, we'll just return semantic results with adjusted scores
        # In a real implementation, we would:
        # 1. Perform keyword search on metadata
        # 2. Combine scores using the provided weights
        # 3. Return re-ranked results
        
        # For now, just return semantic results with a hybrid score type
        for result in semantic_results:
            result.score_type = SearchScoreType.HYBRID
        
        return semantic_results[:limit]
    
    async def search_with_associations(self, query: str, limit: int = 10,
                                      include_associated: bool = False) -> Tuple[List[SearchResult], List[MemoryAssociation]]:
        """Perform search and return associated memories if requested.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            include_associated: Whether to include associated memories
            
        Returns:
            Tuple of (search_results, associated_memories)
        """
        results = await self.search(query, limit)
        
        if include_associated:
            all_associations = []
            for result in results:
                # Get associations for this memory
                # This is a simplified approach - in a real implementation
                # we would have a method to find associations efficiently
                pass
            
            # Note: Association search is handled in the AssociationService
            # so we'll return empty list for now
            return results, []
        
        return results, []
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for this search service."""
        avg_search_time = self.total_search_time / self.search_count if self.search_count > 0 else 0
        return {
            "search_count": self.search_count,
            "total_search_time": self.total_search_time,
            "average_search_time": avg_search_time,
            "cache_size": len(self._query_cache)
        }
    
    def clear_cache(self) -> None:
        """Clear the search result cache."""
        self._query_cache.clear()
        logger.info("Search cache cleared")


class SemanticSearchOptimizer:
    """Performance optimization tools for semantic search."""
    
    def __init__(self, search_service: SemanticSearchService):
        self.search_service = search_service
    
    async def optimize_query(self, query: str) -> str:
        """Optimize a search query for better results."""
        # In a real implementation, this would:
        # - Clean and normalize the query
        # - Extract key terms
        # - Apply stemming/lemmatization
        # - Expand with synonyms if needed
        return query.strip().lower()
    
    async def suggest_query_improvements(self, original_query: str) -> List[str]:
        """Suggest improvements to a query for better search results."""
        # In a real implementation, this would:
        # - Analyze the query
        # - Suggest alternative terms
        # - Propose query reformulations
        # - Identify missing context
        return [original_query]
    
    def get_search_recommendations(self, query: str, results: List[SearchResult]) -> List[str]:
        """Provide recommendations based on search results."""
        # In a real implementation, this would:
        # - Analyze result relevance
        # - Suggest follow-up queries
        # - Identify knowledge gaps
        recommendations = []
        
        if len(results) < 3:
            recommendations.append("Consider broadening your search terms")
        elif len(results) > 20:
            recommendations.append("Consider narrowing your search terms")
        
        return recommendations