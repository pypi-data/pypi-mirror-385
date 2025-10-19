"""Storage package for memory system

Provides abstract base classes and concrete implementations for:
- Vector storage (ChromaDB for semantic search)
- Metadata storage (SQLite for relationships and structured data)
- Storage abstraction layer for unified access
"""

from .base import VectorStore, MetadataStore, StorageManager
from .chroma_store import ChromaDBVectorStore
from .sqlite_store import SQLiteMetadataStore

__all__ = [
    "VectorStore",
    "MetadataStore", 
    "StorageManager",
    "ChromaDBVectorStore",
    "SQLiteMetadataStore"
]

__all__ = ['StorageBackend', 'VectorStore', 'MetadataStore']