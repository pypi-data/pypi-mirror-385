"""Project Context API Endpoints

REST API for storing, retrieving, and searching project context information.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..manager import MemoryManager
from ..models.project_context import ProjectContext, ProjectType
from ..config import MemoryConfig


router = APIRouter(prefix="/memory/project-context", tags=["project-context"])


class ProjectContextResponse(BaseModel):
    """Response model for project context operations."""
    project_id: str
    message: str


class ProjectContextSearchResult(BaseModel):
    """Search result for project contexts."""
    context: ProjectContext
    relevance_score: float


class ProjectContextSearchResponse(BaseModel):
    """Response for project context search."""
    results: List[ProjectContextSearchResult]
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


@router.post("/", response_model=ProjectContextResponse, status_code=201)
async def create_project_context(context: ProjectContext):
    """Store new project context.

    Args:
        context: ProjectContext instance with full project data

    Returns:
        ProjectContextResponse with project_id and success message

    Raises:
        HTTPException: 500 if storage fails
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        project_id = await manager.add_project_context(context)
        return ProjectContextResponse(
            project_id=project_id,
            message="Project context stored successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store project context: {str(e)}")


@router.get("/{project_id}", response_model=ProjectContext)
async def get_project_context(project_id: str):
    """Retrieve specific project context by ID.

    Args:
        project_id: Unique identifier for the project

    Returns:
        ProjectContext instance with full data

    Raises:
        HTTPException: 404 if project not found
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        context = await manager.get_project_context(project_id)
        if not context:
            raise HTTPException(status_code=404, detail=f"Project context {project_id} not found")

        return context
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve project context: {str(e)}")


@router.put("/{project_id}", response_model=ProjectContextResponse)
async def update_project_context(project_id: str, context: ProjectContext):
    """Update existing project context.

    Args:
        project_id: ID of the project to update
        context: Updated ProjectContext instance

    Returns:
        ProjectContextResponse with success message

    Raises:
        HTTPException: 404 if project not found, 500 if update fails
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        success = await manager.update_project_context(project_id, context)
        if not success:
            raise HTTPException(status_code=404, detail=f"Project context {project_id} not found")

        return ProjectContextResponse(
            project_id=project_id,
            message="Project context updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update project context: {str(e)}")


@router.get("/", response_model=ProjectContextSearchResponse)
async def search_project_contexts(
    query: str = Query(..., description="Search query text"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results")
):
    """Search for project contexts using semantic similarity.

    Args:
        query: Search query describing project characteristics
        limit: Maximum number of results (1-100)

    Returns:
        ProjectContextSearchResponse with matching contexts and relevance scores

    Raises:
        HTTPException: 500 if search fails
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        results = await manager.search_project_contexts(
            query=query,
            limit=limit
        )

        search_results = [
            ProjectContextSearchResult(context=context, relevance_score=score)
            for context, score in results
        ]

        return ProjectContextSearchResponse(
            results=search_results,
            count=len(search_results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search project contexts: {str(e)}")
