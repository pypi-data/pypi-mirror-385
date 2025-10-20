"""
ChromaDB Vector Store Implementation

Provides semantic search capabilities using ChromaDB for embeddings storage.
"""

import asyncio
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from .base import VectorStore


class ChromaDBVectorStore(VectorStore):
    """
    ChromaDB implementation of vector storage.

    Handles embeddings generation, storage, and similarity search.
    """

    def __init__(
        self,
        persist_directory: str = "./data/memory/chroma",
        collection_name: str = "multiagent_memories",
        embedding_function: Optional[Any] = None,
        distance_metric: str = "cosine"
    ):
        """
        Initialize ChromaDB vector store.

        Args:
            persist_directory: Directory for persistent storage
            collection_name: Name of the ChromaDB collection
            embedding_function: Custom embedding function (default: sentence transformers)
            distance_metric: Distance metric for similarity ("cosine", "l2", "ip")
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.distance_metric = distance_metric

        # Use sentence transformers by default for embeddings
        self.embedding_function = embedding_function or embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"  # Fast, good quality embeddings
        )

        self.client: Optional[chromadb.Client] = None
        self.collection: Optional[Any] = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize ChromaDB client and collection."""
        if self._initialized:
            return

        # Run synchronous ChromaDB initialization in executor
        await asyncio.get_event_loop().run_in_executor(
            None, self._initialize_sync
        )

        self._initialized = True

    def _initialize_sync(self) -> None:
        """Synchronous initialization helper."""
        # Create ChromaDB client with persistence
        self.client = chromadb.Client(
            Settings(
                persist_directory=self.persist_directory,
                anonymized_telemetry=False
            )
        )

        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
        except Exception:
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": self.distance_metric}
            )

    async def close(self) -> None:
        """Close ChromaDB connection and persist data."""
        if not self._initialized:
            return

        # ChromaDB auto-persists with client settings
        self.collection = None
        self.client = None
        self._initialized = False

    async def add_memory(
        self,
        memory_id: str,
        memory_type: str,
        content: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a memory to ChromaDB with embeddings.

        Args:
            memory_id: Unique memory identifier
            memory_type: Type of memory
            content: Text content to embed
            embedding: Pre-computed embedding (if None, will be generated)
            metadata: Additional metadata

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            raise RuntimeError("ChromaDBVectorStore not initialized")

        try:
            # Prepare metadata
            meta = metadata or {}
            meta["memory_type"] = memory_type

            # Create unique ID combining type and ID
            doc_id = f"{memory_type}:{memory_id}"

            # Add to collection
            if embedding is not None:
                # Use provided embedding
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.collection.add(
                        ids=[doc_id],
                        embeddings=[embedding],
                        documents=[content],
                        metadatas=[meta]
                    )
                )
            else:
                # Let ChromaDB generate embedding
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.collection.add(
                        ids=[doc_id],
                        documents=[content],
                        metadatas=[meta]
                    )
                )

            return True

        except Exception as e:
            print(f"Error adding memory to ChromaDB: {e}")
            return False

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
            memory_type: Optional memory type filter
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold (0.0-1.0)
            filters: Additional metadata filters

        Returns:
            List of matching memories with similarity scores
        """
        if not self._initialized:
            raise RuntimeError("ChromaDBVectorStore not initialized")

        try:
            # Build where filter
            where = filters or {}
            if memory_type:
                where["memory_type"] = memory_type

            # Query ChromaDB
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.collection.query(
                    query_texts=[query],
                    n_results=limit,
                    where=where if where else None
                )
            )

            # Parse results
            memories = []
            if results and results.get("ids"):
                for i, doc_id in enumerate(results["ids"][0]):
                    # Extract memory type and ID from document ID
                    parts = doc_id.split(":", 1)
                    if len(parts) != 2:
                        continue

                    m_type, m_id = parts

                    # Calculate similarity from distance
                    # ChromaDB returns distances, convert to similarity
                    distance = results["distances"][0][i] if results.get("distances") else 1.0

                    if self.distance_metric == "cosine":
                        similarity = 1.0 - distance  # Cosine distance to similarity
                    elif self.distance_metric == "l2":
                        # L2 distance to similarity (normalized)
                        similarity = 1.0 / (1.0 + distance)
                    else:  # inner product
                        similarity = distance  # Already similarity-like

                    # Filter by minimum similarity
                    if similarity < min_similarity:
                        continue

                    memory_data = {
                        "memory_id": m_id,
                        "memory_type": m_type,
                        "content": results["documents"][0][i] if results.get("documents") else "",
                        "similarity": similarity,
                        "distance": distance,
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {}
                    }

                    memories.append(memory_data)

            return memories

        except Exception as e:
            print(f"Error searching ChromaDB: {e}")
            return []

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
        if not self._initialized:
            raise RuntimeError("ChromaDBVectorStore not initialized")

        try:
            doc_id = f"{memory_type}:{memory_id}"

            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.collection.get(
                    ids=[doc_id],
                    include=["documents", "metadatas", "embeddings"]
                )
            )

            if result and result.get("ids") and len(result["ids"]) > 0:
                return {
                    "memory_id": memory_id,
                    "memory_type": memory_type,
                    "content": result["documents"][0] if result.get("documents") else "",
                    "metadata": result["metadatas"][0] if result.get("metadatas") else {},
                    "embedding": result["embeddings"][0] if result.get("embeddings") else None
                }

            return None

        except Exception as e:
            print(f"Error getting memory from ChromaDB: {e}")
            return None

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
        if not self._initialized:
            raise RuntimeError("ChromaDBVectorStore not initialized")

        try:
            doc_id = f"{memory_type}:{memory_id}"

            # Prepare update parameters
            update_params = {"ids": [doc_id]}

            if content is not None:
                update_params["documents"] = [content]

            if metadata is not None:
                meta = metadata.copy()
                meta["memory_type"] = memory_type
                update_params["metadatas"] = [meta]

            # Update in ChromaDB
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.collection.update(**update_params)
            )

            return True

        except Exception as e:
            print(f"Error updating memory in ChromaDB: {e}")
            return False

    async def delete_memory(
        self,
        memory_id: str,
        memory_type: str
    ) -> bool:
        """
        Delete a memory from ChromaDB.

        Args:
            memory_id: Memory identifier
            memory_type: Memory type

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            raise RuntimeError("ChromaDBVectorStore not initialized")

        try:
            doc_id = f"{memory_type}:{memory_id}"

            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.collection.delete(ids=[doc_id])
            )

            return True

        except Exception as e:
            print(f"Error deleting memory from ChromaDB: {e}")
            return False

    async def count_memories(
        self,
        memory_type: Optional[str] = None
    ) -> int:
        """
        Count total memories in the collection.

        Args:
            memory_type: Optional filter by memory type

        Returns:
            Total count of memories
        """
        if not self._initialized:
            raise RuntimeError("ChromaDBVectorStore not initialized")

        try:
            if memory_type:
                # Count with filter
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.collection.get(
                        where={"memory_type": memory_type},
                        include=[]  # Don't fetch data, just count
                    )
                )
                return len(result.get("ids", []))
            else:
                # Total count
                count = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.collection.count()
                )
                return count

        except Exception as e:
            print(f"Error counting memories in ChromaDB: {e}")
            return 0

    async def clear_collection(self) -> bool:
        """
        Clear all memories from the collection (use with caution).

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            raise RuntimeError("ChromaDBVectorStore not initialized")

        try:
            # Delete the collection
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.delete_collection(name=self.collection_name)
            )

            # Recreate empty collection
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function,
                    metadata={"hnsw:space": self.distance_metric}
                )
            )

            return True

        except Exception as e:
            print(f"Error clearing ChromaDB collection: {e}")
            return False
