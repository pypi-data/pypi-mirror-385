"""
SQLite Metadata Store Implementation

Provides structured storage for memory metadata with relationships and indexing.
"""

import asyncio
import json
import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from .base import MetadataStore


class SQLiteMetadataStore(MetadataStore):
    """
    SQLite implementation of metadata storage.

    Handles structured data storage with SQL queries and relationships.
    """

    def __init__(
        self,
        database_path: str = "./data/memory/metadata.db",
        auto_commit: bool = True
    ):
        """
        Initialize SQLite metadata store.

        Args:
            database_path: Path to SQLite database file
            auto_commit: Whether to auto-commit transactions
        """
        self.database_path = database_path
        self.auto_commit = auto_commit
        self.connection: Optional[sqlite3.Connection] = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize SQLite database and create tables."""
        if self._initialized:
            return

        # Ensure database directory exists
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)

        # Create connection
        self.connection = sqlite3.connect(
            self.database_path,
            check_same_thread=False  # Allow use in async context
        )
        self.connection.row_factory = sqlite3.Row  # Access columns by name

        # Create tables
        await self._create_tables()

        self._initialized = True

    async def _create_tables(self) -> None:
        """Create database tables for memory storage."""
        cursor = self.connection.cursor()

        # Main memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                memory_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (memory_id, memory_type)
            )
        """)

        # Associations table for memory relationships
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS associations (
                association_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                source_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                target_type TEXT NOT NULL,
                association_type TEXT NOT NULL,
                data TEXT NOT NULL,
                strength REAL DEFAULT 0.5,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (source_id, source_type) REFERENCES memories (memory_id, memory_type),
                FOREIGN KEY (target_id, target_type) REFERENCES memories (memory_id, memory_type)
            )
        """)

        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_type
            ON memories(memory_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_created
            ON memories(created_at)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_associations_source
            ON associations(source_id, source_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_associations_target
            ON associations(target_id, target_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_associations_type
            ON associations(association_type)
        """)

        if self.auto_commit:
            self.connection.commit()

    async def close(self) -> None:
        """Close SQLite database connection."""
        if not self._initialized:
            return

        if self.connection:
            self.connection.close()
            self.connection = None

        self._initialized = False

    async def save_memory(
        self,
        memory_id: str,
        memory_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Save memory metadata to SQLite.

        Args:
            memory_id: Unique memory identifier
            memory_type: Type of memory
            data: Memory data as dictionary

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            raise RuntimeError("SQLiteMetadataStore not initialized")

        try:
            cursor = self.connection.cursor()

            now = datetime.now().isoformat()
            data_json = json.dumps(data)

            # Insert or replace memory
            cursor.execute("""
                INSERT OR REPLACE INTO memories
                (memory_id, memory_type, data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (memory_id, memory_type, data_json, now, now))

            if self.auto_commit:
                self.connection.commit()

            return True

        except Exception as e:
            print(f"Error saving memory to SQLite: {e}")
            if self.auto_commit:
                self.connection.rollback()
            return False

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
        if not self._initialized:
            raise RuntimeError("SQLiteMetadataStore not initialized")

        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                SELECT data FROM memories
                WHERE memory_id = ? AND memory_type = ?
            """, (memory_id, memory_type))

            row = cursor.fetchone()
            if row:
                return json.loads(row[0])

            return None

        except Exception as e:
            print(f"Error getting memory from SQLite: {e}")
            return None

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
            filters: Filter conditions (basic key-value matching in JSON)
            sort_by: Field to sort by (prefix with '-' for descending)
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of matching memories
        """
        if not self._initialized:
            raise RuntimeError("SQLiteMetadataStore not initialized")

        try:
            cursor = self.connection.cursor()

            # Build query
            query = "SELECT data FROM memories WHERE memory_type = ?"
            params = [memory_type]

            # Note: JSON filtering in SQLite is limited without json1 extension
            # For now, we'll fetch and filter in Python

            # Add sorting
            if sort_by:
                if sort_by.startswith('-'):
                    order = "DESC"
                    field = sort_by[1:]
                else:
                    order = "ASC"
                    field = sort_by

                # Sort by database fields only
                if field in ['created_at', 'updated_at']:
                    query += f" ORDER BY {field} {order}"

            # Add pagination
            if limit:
                query += " LIMIT ?"
                params.append(limit)

            if offset:
                query += " OFFSET ?"
                params.append(offset)

            cursor.execute(query, params)

            # Parse results
            memories = []
            for row in cursor.fetchall():
                data = json.loads(row[0])

                # Apply filters in Python
                if filters:
                    matches = True
                    for key, value in filters.items():
                        if data.get(key) != value:
                            matches = False
                            break

                    if not matches:
                        continue

                memories.append(data)

            return memories

        except Exception as e:
            print(f"Error querying memories from SQLite: {e}")
            return []

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
        if not self._initialized:
            raise RuntimeError("SQLiteMetadataStore not initialized")

        try:
            cursor = self.connection.cursor()

            now = datetime.now().isoformat()
            data_json = json.dumps(data)

            cursor.execute("""
                UPDATE memories
                SET data = ?, updated_at = ?
                WHERE memory_id = ? AND memory_type = ?
            """, (data_json, now, memory_id, memory_type))

            if self.auto_commit:
                self.connection.commit()

            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error updating memory in SQLite: {e}")
            if self.auto_commit:
                self.connection.rollback()
            return False

    async def delete_memory(
        self,
        memory_id: str,
        memory_type: str
    ) -> bool:
        """
        Delete memory metadata from SQLite.

        Args:
            memory_id: Memory identifier
            memory_type: Memory type

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            raise RuntimeError("SQLiteMetadataStore not initialized")

        try:
            cursor = self.connection.cursor()

            # Delete associated associations first
            cursor.execute("""
                DELETE FROM associations
                WHERE (source_id = ? AND source_type = ?)
                   OR (target_id = ? AND target_type = ?)
            """, (memory_id, memory_type, memory_id, memory_type))

            # Delete memory
            cursor.execute("""
                DELETE FROM memories
                WHERE memory_id = ? AND memory_type = ?
            """, (memory_id, memory_type))

            if self.auto_commit:
                self.connection.commit()

            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error deleting memory from SQLite: {e}")
            if self.auto_commit:
                self.connection.rollback()
            return False

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
        if not self._initialized:
            raise RuntimeError("SQLiteMetadataStore not initialized")

        try:
            cursor = self.connection.cursor()

            now = datetime.now().isoformat()
            data_json = json.dumps(association_data)

            # Extract association type and strength
            assoc_type = association_data.get('association_type', 'unknown')
            strength = association_data.get('strength', 0.5)

            cursor.execute("""
                INSERT OR REPLACE INTO associations
                (association_id, source_id, source_type, target_id, target_type,
                 association_type, data, strength, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (association_id, source_id, source_type, target_id, target_type,
                  assoc_type, data_json, strength, now, now))

            if self.auto_commit:
                self.connection.commit()

            return True

        except Exception as e:
            print(f"Error saving association to SQLite: {e}")
            if self.auto_commit:
                self.connection.rollback()
            return False

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
        if not self._initialized:
            raise RuntimeError("SQLiteMetadataStore not initialized")

        try:
            cursor = self.connection.cursor()

            if direction == "outgoing":
                cursor.execute("""
                    SELECT data FROM associations
                    WHERE source_id = ? AND source_type = ?
                    ORDER BY strength DESC
                """, (memory_id, memory_type))
            elif direction == "incoming":
                cursor.execute("""
                    SELECT data FROM associations
                    WHERE target_id = ? AND target_type = ?
                    ORDER BY strength DESC
                """, (memory_id, memory_type))
            else:  # both
                cursor.execute("""
                    SELECT data FROM associations
                    WHERE (source_id = ? AND source_type = ?)
                       OR (target_id = ? AND target_type = ?)
                    ORDER BY strength DESC
                """, (memory_id, memory_type, memory_id, memory_type))

            associations = []
            for row in cursor.fetchall():
                associations.append(json.loads(row[0]))

            return associations

        except Exception as e:
            print(f"Error getting associations from SQLite: {e}")
            return []

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
        if not self._initialized:
            raise RuntimeError("SQLiteMetadataStore not initialized")

        try:
            cursor = self.connection.cursor()

            if memory_type:
                cursor.execute("""
                    SELECT COUNT(*) FROM memories
                    WHERE memory_type = ?
                """, (memory_type,))
            else:
                cursor.execute("SELECT COUNT(*) FROM memories")

            return cursor.fetchone()[0]

        except Exception as e:
            print(f"Error counting memories in SQLite: {e}")
            return 0

    async def execute_raw_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a raw SQL query (use with caution).

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Query results as list of dictionaries
        """
        if not self._initialized:
            raise RuntimeError("SQLiteMetadataStore not initialized")

        try:
            cursor = self.connection.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Convert rows to dictionaries
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            results = []

            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            return results

        except Exception as e:
            print(f"Error executing raw query in SQLite: {e}")
            return []

    async def vacuum(self) -> bool:
        """
        Optimize database by reclaiming unused space.

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            raise RuntimeError("SQLiteMetadataStore not initialized")

        try:
            cursor = self.connection.cursor()
            cursor.execute("VACUUM")
            return True

        except Exception as e:
            print(f"Error vacuuming SQLite database: {e}")
            return False
