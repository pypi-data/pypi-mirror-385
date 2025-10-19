"""
Storage Abstraction Layer

Defines abstract base classes for memory storage implementations.
Provides unified interfaces for vector and metadata storage.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from datetime import datetime


class VectorStore(ABC):
    """
    Abstract base class for vector storage backends.

    Handles embeddings storage and semantic similarity search.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the vector store connection and collections."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the vector store connection and cleanup resources."""
        pass

    @abstractmethod
    async def add_memory(
        self,
        memory_id: str,
        memory_type: str,
        content: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a memory to the vector store.

        Args:
            memory_id: Unique memory identifier
            memory_type: Type of memory (conversation, insight, etc.)
            content: Text content to store/embed
            embedding: Pre-computed embedding vector (if None, will be generated)
            metadata: Additional metadata to store with the memory

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def search_similar(
        self,
        query: str,
        memory_type: Optional[str] = None,
        limit: int = 10,
        min_similarity: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar memories using semantic similarity.

        Args:
            query: Search query text
            memory_type: Optional filter by memory type
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold (0.0-1.0)
            filters: Additional metadata filters

        Returns:
            List of matching memories with similarity scores
        """
        pass

    @abstractmethod
    async def get_memory(
        self,
        memory_id: str,
        memory_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by ID and type.

        Args:
            memory_id: Memory identifier
            memory_type: Memory type

        Returns:
            Memory data if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_memory(
        self,
        memory_id: str,
        memory_type: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing memory's content or metadata.

        Args:
            memory_id: Memory identifier
            memory_type: Memory type
            content: Updated content (will regenerate embedding)
            metadata: Updated metadata

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def delete_memory(
        self,
        memory_id: str,
        memory_type: str
    ) -> bool:
        """
        Delete a memory from the vector store.

        Args:
            memory_id: Memory identifier
            memory_type: Memory type

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def count_memories(
        self,
        memory_type: Optional[str] = None
    ) -> int:
        """
        Count total memories in the store.

        Args:
            memory_type: Optional filter by memory type

        Returns:
            Total count of memories
        """
        pass


class MetadataStore(ABC):
    """
    Abstract base class for metadata storage backends.

    Handles structured data storage with relationships and indexing.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the metadata store and create tables/schemas."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the metadata store connection and cleanup resources."""
        pass

    @abstractmethod
    async def save_memory(
        self,
        memory_id: str,
        memory_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Save memory metadata to the store.

        Args:
            memory_id: Unique memory identifier
            memory_type: Type of memory
            data: Memory data as dictionary

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_memory(
        self,
        memory_id: str,
        memory_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve memory metadata by ID and type.

        Args:
            memory_id: Memory identifier
            memory_type: Memory type

        Returns:
            Memory data if found, None otherwise
        """
        pass

    @abstractmethod
    async def query_memories(
        self,
        memory_type: str,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Query memories with filtering and sorting.

        Args:
            memory_type: Type of memory to query
            filters: Filter conditions as key-value pairs
            sort_by: Field to sort by (prefix with '-' for descending)
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of matching memories
        """
        pass

    @abstractmethod
    async def update_memory(
        self,
        memory_id: str,
        memory_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Update existing memory metadata.

        Args:
            memory_id: Memory identifier
            memory_type: Memory type
            data: Updated memory data

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def delete_memory(
        self,
        memory_id: str,
        memory_type: str
    ) -> bool:
        """
        Delete memory metadata from the store.

        Args:
            memory_id: Memory identifier
            memory_type: Memory type

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def save_association(
        self,
        association_id: str,
        source_id: str,
        source_type: str,
        target_id: str,
        target_type: str,
        association_data: Dict[str, Any]
    ) -> bool:
        """
        Save a memory association.

        Args:
            association_id: Unique association identifier
            source_id: Source memory ID
            source_type: Source memory type
            target_id: Target memory ID
            target_type: Target memory type
            association_data: Association metadata

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_associations(
        self,
        memory_id: str,
        memory_type: str,
        direction: str = "both"
    ) -> List[Dict[str, Any]]:
        """
        Get all associations for a memory.

        Args:
            memory_id: Memory identifier
            memory_type: Memory type
            direction: "incoming", "outgoing", or "both"

        Returns:
            List of associations
        """
        pass

    @abstractmethod
    async def count_memories(
        self,
        memory_type: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count memories matching criteria.

        Args:
            memory_type: Optional memory type filter
            filters: Optional additional filters

        Returns:
            Count of matching memories
        """
        pass

    @abstractmethod
    async def execute_raw_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a raw database query (use with caution).

        Args:
            query: SQL or query string
            params: Query parameters

        Returns:
            Query results
        """
        pass


class StorageManager:
    """
    Unified storage manager that coordinates vector and metadata stores.

    Provides high-level operations that work across both storage backends.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        metadata_store: MetadataStore
    ):
        """
        Initialize storage manager with both storage backends.

        Args:
            vector_store: Vector storage implementation
            metadata_store: Metadata storage implementation
        """
        self.vector_store = vector_store
        self.metadata_store = metadata_store
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize both storage backends."""
        if self._initialized:
            return

        await self.vector_store.initialize()
        await self.metadata_store.initialize()
        self._initialized = True

    async def close(self) -> None:
        """Close both storage backends."""
        if not self._initialized:
            return

        await self.vector_store.close()
        await self.metadata_store.close()
        self._initialized = False

    async def save_memory(
        self,
        memory_id: str,
        memory_type: str,
        data: Dict[str, Any],
        search_text: str,
        embedding: Optional[List[float]] = None
    ) -> bool:
        """
        Save a memory to both storage backends.

        Args:
            memory_id: Unique memory identifier
            memory_type: Type of memory
            data: Memory data dictionary
            search_text: Text content for semantic search
            embedding: Optional pre-computed embedding

        Returns:
            True if successful in both stores, False otherwise
        """
        if not self._initialized:
            raise RuntimeError("StorageManager not initialized")

        # Save to metadata store first
        metadata_success = await self.metadata_store.save_memory(
            memory_id, memory_type, data
        )

        if not metadata_success:
            return False

        # Then save to vector store for semantic search
        vector_success = await self.vector_store.add_memory(
            memory_id,
            memory_type,
            search_text,
            embedding=embedding,
            metadata={"memory_type": memory_type}
        )

        if not vector_success:
            # Rollback metadata store save
            await self.metadata_store.delete_memory(memory_id, memory_type)
            return False

        return True

    async def get_memory(
        self,
        memory_id: str,
        memory_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a memory from metadata store.

        Args:
            memory_id: Memory identifier
            memory_type: Memory type

        Returns:
            Memory data if found, None otherwise
        """
        if not self._initialized:
            raise RuntimeError("StorageManager not initialized")

        return await self.metadata_store.get_memory(memory_id, memory_type)

    async def search_memories(
        self,
        query: str,
        memory_type: Optional[str] = None,
        limit: int = 10,
        min_similarity: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for similar memories and enrich with full metadata.

        Args:
            query: Search query text
            memory_type: Optional memory type filter
            limit: Maximum results
            min_similarity: Minimum similarity threshold

        Returns:
            List of memories with full data and similarity scores
        """
        if not self._initialized:
            raise RuntimeError("StorageManager not initialized")

        # Search vector store for similar memories
        similar = await self.vector_store.search_similar(
            query,
            memory_type=memory_type,
            limit=limit,
            min_similarity=min_similarity
        )

        # Enrich with full metadata
        enriched = []
        for result in similar:
            memory_id = result.get("memory_id")
            m_type = result.get("memory_type")

            if memory_id and m_type:
                full_data = await self.metadata_store.get_memory(memory_id, m_type)
                if full_data:
                    full_data["_similarity_score"] = result.get("similarity", 0.0)
                    enriched.append(full_data)

        return enriched

    async def delete_memory(
        self,
        memory_id: str,
        memory_type: str
    ) -> bool:
        """
        Delete a memory from both storage backends.

        Args:
            memory_id: Memory identifier
            memory_type: Memory type

        Returns:
            True if successful in both stores
        """
        if not self._initialized:
            raise RuntimeError("StorageManager not initialized")

        # Delete from both stores
        metadata_deleted = await self.metadata_store.delete_memory(
            memory_id, memory_type
        )
        vector_deleted = await self.vector_store.delete_memory(
            memory_id, memory_type
        )

        return metadata_deleted and vector_deleted

    def __enter__(self):
        """Context manager entry."""
        return self

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
