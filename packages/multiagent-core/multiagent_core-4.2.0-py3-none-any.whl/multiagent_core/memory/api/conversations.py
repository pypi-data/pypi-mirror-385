"""Conversation Memory API Endpoints

REST API for storing, retrieving, and searching conversation memories.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..manager import MemoryManager
from ..models.conversation import ConversationMemory, AgentType
from ..config import MemoryConfig


router = APIRouter(prefix="/memory/conversations", tags=["conversations"])


class ConversationResponse(BaseModel):
    """Response model for conversation operations."""
    conversation_id: str
    message: str


class ConversationSearchResult(BaseModel):
    """Search result for conversations."""
    conversation: ConversationMemory
    relevance_score: float


class ConversationSearchResponse(BaseModel):
    """Response for conversation search."""
    results: List[ConversationSearchResult]
    count: int


# Dependency injection for memory manager
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get or create memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        config = MemoryConfig()
        _memory_manager = MemoryManager(config)
    return _memory_manager


@router.post("/", response_model=ConversationResponse, status_code=201)
async def create_conversation(conversation: ConversationMemory):
    """Store a new conversation in memory.

    Args:
        conversation: ConversationMemory instance with full conversation data

    Returns:
        ConversationResponse with conversation_id and success message

    Raises:
        HTTPException: 500 if storage fails
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        conversation_id = await manager.add_conversation(conversation)
        return ConversationResponse(
            conversation_id=conversation_id,
            message="Conversation stored successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store conversation: {str(e)}")


@router.get("/{conversation_id}", response_model=ConversationMemory)
async def get_conversation(conversation_id: str):
    """Retrieve a specific conversation by ID.

    Args:
        conversation_id: Unique identifier for the conversation

    Returns:
        ConversationMemory instance with full conversation data

    Raises:
        HTTPException: 404 if conversation not found
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        conversation = await manager.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")

        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation: {str(e)}")


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(conversation_id: str, conversation: ConversationMemory):
    """Update an existing conversation.

    Args:
        conversation_id: ID of the conversation to update
        conversation: Updated ConversationMemory instance

    Returns:
        ConversationResponse with success message

    Raises:
        HTTPException: 404 if conversation not found, 500 if update fails
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        success = await manager.update_conversation(conversation_id, conversation)
        if not success:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")

        return ConversationResponse(
            conversation_id=conversation_id,
            message="Conversation updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update conversation: {str(e)}")


@router.get("/", response_model=ConversationSearchResponse)
async def search_conversations(
    query: str = Query(..., description="Search query text"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results")
):
    """Search for conversations using semantic similarity.

    Args:
        query: Search query text
        project_id: Optional project filter
        limit: Maximum number of results (1-100)

    Returns:
        ConversationSearchResponse with matching conversations and relevance scores

    Raises:
        HTTPException: 500 if search fails
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        results = await manager.search_conversations(
            query=query,
            project_id=project_id,
            limit=limit
        )

        search_results = [
            ConversationSearchResult(conversation=conv, relevance_score=score)
            for conv, score in results
        ]

        return ConversationSearchResponse(
            results=search_results,
            count=len(search_results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search conversations: {str(e)}")
