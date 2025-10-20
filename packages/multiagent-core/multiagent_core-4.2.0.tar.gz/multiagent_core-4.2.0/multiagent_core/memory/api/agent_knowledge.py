"""Agent Knowledge API Endpoints

REST API for storing, retrieving, and searching agent knowledge and skills.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..manager import MemoryManager
from ..models.agent_knowledge import AgentKnowledge, ProficiencyLevel
from ..config import MemoryConfig


router = APIRouter(prefix="/memory/agent-knowledge", tags=["agent-knowledge"])


class AgentKnowledgeResponse(BaseModel):
    """Response model for agent knowledge operations."""
    knowledge_id: str
    message: str


class AgentKnowledgeSearchResult(BaseModel):
    """Search result for agent knowledge."""
    knowledge: AgentKnowledge
    relevance_score: float


class AgentKnowledgeSearchResponse(BaseModel):
    """Response for agent knowledge search."""
    results: List[AgentKnowledgeSearchResult]
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


@router.post("/", response_model=AgentKnowledgeResponse, status_code=201)
async def create_agent_knowledge(knowledge: AgentKnowledge):
    """Store new agent knowledge or skill.

    Args:
        knowledge: AgentKnowledge instance with skill data

    Returns:
        AgentKnowledgeResponse with knowledge_id and success message

    Raises:
        HTTPException: 500 if storage fails
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        knowledge_id = await manager.add_agent_knowledge(knowledge)
        return AgentKnowledgeResponse(
            knowledge_id=knowledge_id,
            message="Agent knowledge stored successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store agent knowledge: {str(e)}")


@router.get("/{knowledge_id}", response_model=AgentKnowledge)
async def get_agent_knowledge(knowledge_id: str):
    """Retrieve specific agent knowledge by ID.

    Args:
        knowledge_id: Unique identifier for the knowledge entry

    Returns:
        AgentKnowledge instance with full data

    Raises:
        HTTPException: 404 if knowledge not found
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        knowledge = await manager.get_agent_knowledge(knowledge_id)
        if not knowledge:
            raise HTTPException(status_code=404, detail=f"Agent knowledge {knowledge_id} not found")

        return knowledge
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve agent knowledge: {str(e)}")


@router.put("/{knowledge_id}", response_model=AgentKnowledgeResponse)
async def update_agent_knowledge(knowledge_id: str, knowledge: AgentKnowledge):
    """Update existing agent knowledge.

    Args:
        knowledge_id: ID of the knowledge entry to update
        knowledge: Updated AgentKnowledge instance

    Returns:
        AgentKnowledgeResponse with success message

    Raises:
        HTTPException: 404 if knowledge not found, 500 if update fails
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        success = await manager.update_agent_knowledge(knowledge_id, knowledge)
        if not success:
            raise HTTPException(status_code=404, detail=f"Agent knowledge {knowledge_id} not found")

        return AgentKnowledgeResponse(
            knowledge_id=knowledge_id,
            message="Agent knowledge updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update agent knowledge: {str(e)}")


@router.get("/", response_model=AgentKnowledgeSearchResponse)
async def search_agent_knowledge(
    query: str = Query(..., description="Search query text"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results")
):
    """Search for agent knowledge using semantic similarity.

    Args:
        query: Search query describing skill or domain
        agent_id: Optional agent filter
        limit: Maximum number of results (1-100)

    Returns:
        AgentKnowledgeSearchResponse with matching knowledge and relevance scores

    Raises:
        HTTPException: 500 if search fails
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        results = await manager.search_agent_knowledge(
            query=query,
            agent_id=agent_id,
            limit=limit
        )

        search_results = [
            AgentKnowledgeSearchResult(knowledge=knowledge, relevance_score=score)
            for knowledge, score in results
        ]

        return AgentKnowledgeSearchResponse(
            results=search_results,
            count=len(search_results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search agent knowledge: {str(e)}")
