"""Memory Manager - Core orchestration for multiagent memory system

Handles the main memory operations including conversation storage,
retrieval, search, and cross-agent context sharing.
"""

from typing import Dict, List, Optional, Any, Tuple
from uuid import uuid4
import logging

from .config import MemoryConfig
from .storage.base import StorageManager
from .storage.chroma_store import ChromaDBVectorStore
from .storage.sqlite_store import SQLiteMetadataStore
from .models.conversation import ConversationMemory
from .models.config_insight import ConfigurationInsight
from .models.agent_knowledge import AgentKnowledge
from .models.project_context import ProjectContext
from .models.association import MemoryAssociation, MemoryType

logger = logging.getLogger(__name__)


class MemoryManager:
    """Main interface for memory system operations.
    
    Provides high-level API for storing conversations, searching memories,
    and managing agent knowledge across the multiagent framework.
    """
    
    def __init__(self, config: MemoryConfig):
        """Initialize the memory manager.
        
        Args:
            config: MemoryConfig instance with system configuration
        """
        self.config = config
        self._initialized = False
        self.storage: Optional[StorageManager] = None
        
    async def initialize(self) -> bool:
        """Initialize the memory system components.

        Implements graceful degradation - system can operate without memory
        if initialization fails (logs warning but doesn't crash).

        Returns:
            bool: True if initialization successful, False if degraded mode
        """
        try:
            # Initialize storage backends
            vector_store = ChromaDBVectorStore(
                persist_directory=self.config.get('storage.vector_db.persist_directory'),
                collection_name=self.config.get('storage.vector_db.collection_name')
            )

            metadata_store = SQLiteMetadataStore(
                database_path=self.config.get('storage.metadata_db.database_path')
            )

            # Create unified storage manager
            self.storage = StorageManager(vector_store, metadata_store)
            await self.storage.initialize()

            self._initialized = True
            logger.info("Memory manager initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize memory manager: {e}")
            logger.warning("Memory system operating in degraded mode - memory features unavailable")
            # Don't raise - allow graceful degradation
            self._initialized = False
            return False
    
    def _ensure_initialized(self):
        """Ensure the manager is initialized.

        Raises:
            RuntimeError: If memory system not initialized (graceful degradation mode)
        """
        if not self._initialized or not self.storage:
            raise RuntimeError(
                "Memory system not initialized. Operating in degraded mode. "
                "Memory features unavailable - check logs for initialization errors."
            )
    
    # ==================== Conversation Memory Operations ====================
    
    async def add_conversation(self, conversation: ConversationMemory) -> str:
        """Store a conversation in memory.
        
        Args:
            conversation: ConversationMemory instance to store
            
        Returns:
            str: Memory ID for the stored conversation
        """
        self._ensure_initialized()
        
        # Generate search text from conversation
        search_text = conversation.generate_search_text()
        
        # Store in vector DB for semantic search
        memory_id = await self.storage.vector_store.add(
            id=conversation.conversation_id,
            text=search_text,
            metadata={
                "type": MemoryType.CONVERSATION.value,
                "project_id": conversation.project_id,
                "topic": conversation.topic,
                "participants": [p.value for p in conversation.participants]
            }
        )
        
        # Store full data in metadata DB
        await self.storage.metadata_store.add(
            memory_id=memory_id,
            memory_type=MemoryType.CONVERSATION,
            data=conversation.model_dump(),
            metadata={"project_id": conversation.project_id}
        )
        
        logger.info(f"Stored conversation {memory_id} for project {conversation.project_id}")
        return memory_id
    
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationMemory]:
        """Retrieve a specific conversation by ID.
        
        Args:
            conversation_id: ID of the conversation to retrieve
            
        Returns:
            ConversationMemory instance or None if not found
        """
        self._ensure_initialized()
        
        result = await self.storage.metadata_store.get(conversation_id)
        if result:
            return ConversationMemory(**result["data"])
        return None
    
    async def update_conversation(self, conversation_id: str, conversation: ConversationMemory) -> bool:
        """Update an existing conversation.
        
        Args:
            conversation_id: ID of the conversation to update
            conversation: Updated ConversationMemory instance
            
        Returns:
            bool: True if successful
        """
        self._ensure_initialized()
        
        # Update vector store
        search_text = conversation.generate_search_text()
        await self.storage.vector_store.update(
            id=conversation_id,
            text=search_text,
            metadata={
                "type": MemoryType.CONVERSATION.value,
                "project_id": conversation.project_id,
                "topic": conversation.topic
            }
        )
        
        # Update metadata store
        return await self.storage.metadata_store.update(
            memory_id=conversation_id,
            data=conversation.model_dump(),
            metadata={"project_id": conversation.project_id}
        )
    
    async def search_conversations(
        self, 
        query: str, 
        project_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[ConversationMemory, float]]:
        """Search for relevant conversations using semantic similarity.
        
        Args:
            query: Search query string
            project_id: Optional project filter
            limit: Maximum number of results
            
        Returns:
            List of (ConversationMemory, relevance_score) tuples
        """
        self._ensure_initialized()
        
        # Build metadata filter
        where = {"type": MemoryType.CONVERSATION.value}
        if project_id:
            where["project_id"] = project_id
        
        # Search vector store
        results = await self.storage.vector_store.search(
            query=query,
            limit=limit,
            where=where if where else None
        )
        
        # Fetch full conversation data
        conversations = []
        for memory_id, score in results:
            conv = await self.get_conversation(memory_id)
            if conv:
                conversations.append((conv, score))
        
        return conversations
    
    # ==================== Configuration Insight Operations ====================
    
    async def add_configuration_insight(self, insight: ConfigurationInsight) -> str:
        """Store a configuration insight.
        
        Args:
            insight: ConfigurationInsight instance to store
            
        Returns:
            str: Memory ID for the stored insight
        """
        self._ensure_initialized()
        
        # Generate search text
        search_text = f"{insight.title} {insight.description} {insight.recommendation} {' '.join(insight.applicable_contexts)}"
        
        # Store in vector DB
        memory_id = await self.storage.vector_store.add(
            id=insight.insight_id,
            text=search_text,
            metadata={
                "type": MemoryType.CONFIGURATION_INSIGHT.value,
                "project_id": insight.project_id,
                "category": insight.category.value,
                "confidence": insight.confidence_score
            }
        )
        
        # Store full data
        await self.storage.metadata_store.add(
            memory_id=memory_id,
            memory_type=MemoryType.CONFIGURATION_INSIGHT,
            data=insight.model_dump(),
            metadata={"project_id": insight.project_id}
        )
        
        logger.info(f"Stored configuration insight {memory_id}")
        return memory_id
    
    async def get_configuration_insight(self, insight_id: str) -> Optional[ConfigurationInsight]:
        """Retrieve a specific configuration insight by ID."""
        self._ensure_initialized()
        
        result = await self.storage.metadata_store.get(insight_id)
        if result:
            return ConfigurationInsight(**result["data"])
        return None
    
    async def update_configuration_insight(self, insight_id: str, insight: ConfigurationInsight) -> bool:
        """Update an existing configuration insight."""
        self._ensure_initialized()
        
        search_text = f"{insight.title} {insight.description} {insight.recommendation}"
        await self.storage.vector_store.update(
            id=insight_id,
            text=search_text,
            metadata={
                "type": MemoryType.CONFIGURATION_INSIGHT.value,
                "category": insight.category.value,
                "confidence": insight.confidence_score
            }
        )
        
        return await self.storage.metadata_store.update(
            memory_id=insight_id,
            data=insight.model_dump(),
            metadata={"project_id": insight.project_id}
        )
    
    async def search_configuration_insights(
        self,
        query: str,
        project_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[ConfigurationInsight, float]]:
        """Search for relevant configuration insights."""
        self._ensure_initialized()
        
        where = {"type": MemoryType.CONFIGURATION_INSIGHT.value}
        if project_id:
            where["project_id"] = project_id
        
        results = await self.storage.vector_store.search(
            query=query,
            limit=limit,
            where=where if where else None
        )
        
        insights = []
        for memory_id, score in results:
            insight = await self.get_configuration_insight(memory_id)
            if insight:
                insights.append((insight, score))
        
        return insights
    
    # ==================== Agent Knowledge Operations ====================
    
    async def add_agent_knowledge(self, knowledge: AgentKnowledge) -> str:
        """Store agent knowledge and skills."""
        self._ensure_initialized()
        
        search_text = f"{knowledge.skill_name} {knowledge.domain} {knowledge.description} {' '.join(knowledge.examples)}"
        
        memory_id = await self.storage.vector_store.add(
            id=knowledge.knowledge_id,
            text=search_text,
            metadata={
                "type": MemoryType.AGENT_KNOWLEDGE.value,
                "agent_id": knowledge.agent_id,
                "domain": knowledge.domain,
                "proficiency": knowledge.proficiency_level.value
            }
        )
        
        await self.storage.metadata_store.add(
            memory_id=memory_id,
            memory_type=MemoryType.AGENT_KNOWLEDGE,
            data=knowledge.model_dump(),
            metadata={"agent_id": knowledge.agent_id}
        )
        
        logger.info(f"Stored agent knowledge {memory_id} for agent {knowledge.agent_id}")
        return memory_id
    
    async def get_agent_knowledge(self, knowledge_id: str) -> Optional[AgentKnowledge]:
        """Retrieve specific agent knowledge by ID."""
        self._ensure_initialized()
        
        result = await self.storage.metadata_store.get(knowledge_id)
        if result:
            return AgentKnowledge(**result["data"])
        return None
    
    async def update_agent_knowledge(self, knowledge_id: str, knowledge: AgentKnowledge) -> bool:
        """Update existing agent knowledge."""
        self._ensure_initialized()
        
        search_text = f"{knowledge.skill_name} {knowledge.domain} {knowledge.description}"
        await self.storage.vector_store.update(
            id=knowledge_id,
            text=search_text,
            metadata={
                "type": MemoryType.AGENT_KNOWLEDGE.value,
                "agent_id": knowledge.agent_id,
                "proficiency": knowledge.proficiency_level.value
            }
        )
        
        return await self.storage.metadata_store.update(
            memory_id=knowledge_id,
            data=knowledge.model_dump(),
            metadata={"agent_id": knowledge.agent_id}
        )
    
    async def search_agent_knowledge(
        self,
        query: str,
        agent_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[AgentKnowledge, float]]:
        """Search for relevant agent knowledge and skills."""
        self._ensure_initialized()
        
        where = {"type": MemoryType.AGENT_KNOWLEDGE.value}
        if agent_id:
            where["agent_id"] = agent_id
        
        results = await self.storage.vector_store.search(
            query=query,
            limit=limit,
            where=where if where else None
        )
        
        knowledge_items = []
        for memory_id, score in results:
            knowledge = await self.get_agent_knowledge(memory_id)
            if knowledge:
                knowledge_items.append((knowledge, score))
        
        return knowledge_items
    
    # ==================== Project Context Operations ====================
    
    async def add_project_context(self, context: ProjectContext) -> str:
        """Store project context."""
        self._ensure_initialized()
        
        search_text = f"{context.name} {context.description} {' '.join(context.tech_stack)} {' '.join(context.architectural_decisions)}"
        
        memory_id = await self.storage.vector_store.add(
            id=context.project_id,
            text=search_text,
            metadata={
                "type": MemoryType.PROJECT_CONTEXT.value,
                "project_id": context.project_id,
                "project_type": context.project_type.value
            }
        )
        
        await self.storage.metadata_store.add(
            memory_id=memory_id,
            memory_type=MemoryType.PROJECT_CONTEXT,
            data=context.model_dump(),
            metadata={"project_id": context.project_id}
        )
        
        logger.info(f"Stored project context {memory_id}")
        return memory_id
    
    async def get_project_context(self, project_id: str) -> Optional[ProjectContext]:
        """Retrieve specific project context by ID."""
        self._ensure_initialized()
        
        result = await self.storage.metadata_store.get(project_id)
        if result:
            return ProjectContext(**result["data"])
        return None
    
    async def update_project_context(self, project_id: str, context: ProjectContext) -> bool:
        """Update existing project context."""
        self._ensure_initialized()
        
        search_text = f"{context.name} {context.description} {' '.join(context.tech_stack)}"
        await self.storage.vector_store.update(
            id=project_id,
            text=search_text,
            metadata={
                "type": MemoryType.PROJECT_CONTEXT.value,
                "project_type": context.project_type.value
            }
        )
        
        return await self.storage.metadata_store.update(
            memory_id=project_id,
            data=context.model_dump(),
            metadata={"project_id": context.project_id}
        )
    
    async def search_project_contexts(
        self,
        query: str,
        limit: int = 10
    ) -> List[Tuple[ProjectContext, float]]:
        """Search for relevant project contexts."""
        self._ensure_initialized()
        
        results = await self.storage.vector_store.search(
            query=query,
            limit=limit,
            where={"type": MemoryType.PROJECT_CONTEXT.value}
        )
        
        contexts = []
        for memory_id, score in results:
            context = await self.get_project_context(memory_id)
            if context:
                contexts.append((context, score))
        
        return contexts
    
    # ==================== Memory Association Operations ====================
    
    async def add_association(self, association: MemoryAssociation) -> str:
        """Create a memory association."""
        self._ensure_initialized()
        
        memory_id = await self.storage.metadata_store.add(
            memory_id=association.association_id,
            memory_type=MemoryType.ASSOCIATION,
            data=association.model_dump(),
            metadata={
                "source_id": association.source_memory_id,
                "target_id": association.target_memory_id,
                "type": association.association_type.value
            }
        )
        
        logger.info(f"Created association {memory_id}")
        return memory_id
    
    async def get_association(self, association_id: str) -> Optional[MemoryAssociation]:
        """Retrieve a specific association by ID."""
        self._ensure_initialized()
        
        result = await self.storage.metadata_store.get(association_id)
        if result:
            return MemoryAssociation(**result["data"])
        return None
    
    # ==================== Utility Operations ====================
    
    async def cleanup_old_memories(
        self,
        older_than_days: int = 90,
        min_confidence: float = 0.3
    ) -> Dict[str, int]:
        """Clean up old or low-confidence memories.
        
        Args:
            older_than_days: Remove memories older than this
            min_confidence: Remove memories below this confidence
            
        Returns:
            Dict with cleanup statistics
        """
        self._ensure_initialized()
        
        # TODO: Implement cleanup logic
        logger.info(f"Cleaning up memories older than {older_than_days} days")
        return {"removed": 0, "kept": 0}
