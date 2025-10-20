"""Configuration Insights API Endpoints

REST API for storing, retrieving, and searching configuration insights.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..manager import MemoryManager
from ..models.config_insight import ConfigurationInsight, InsightCategory
from ..config import MemoryConfig


router = APIRouter(prefix="/memory/config-insights", tags=["config-insights"])


class ConfigInsightResponse(BaseModel):
    """Response model for configuration insight operations."""
    insight_id: str
    message: str


class ConfigInsightSearchResult(BaseModel):
    """Search result for configuration insights."""
    insight: ConfigurationInsight
    relevance_score: float


class ConfigInsightSearchResponse(BaseModel):
    """Response for configuration insight search."""
    results: List[ConfigInsightSearchResult]
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


@router.post("/", response_model=ConfigInsightResponse, status_code=201)
async def create_config_insight(insight: ConfigurationInsight):
    """Store a new configuration insight.

    Args:
        insight: ConfigurationInsight instance with learned pattern

    Returns:
        ConfigInsightResponse with insight_id and success message

    Raises:
        HTTPException: 500 if storage fails
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        insight_id = await manager.add_configuration_insight(insight)
        return ConfigInsightResponse(
            insight_id=insight_id,
            message="Configuration insight stored successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store insight: {str(e)}")


@router.get("/{insight_id}", response_model=ConfigurationInsight)
async def get_config_insight(insight_id: str):
    """Retrieve a specific configuration insight by ID.

    Args:
        insight_id: Unique identifier for the insight

    Returns:
        ConfigurationInsight instance with full data

    Raises:
        HTTPException: 404 if insight not found
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        insight = await manager.get_configuration_insight(insight_id)
        if not insight:
            raise HTTPException(status_code=404, detail=f"Configuration insight {insight_id} not found")

        return insight
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve insight: {str(e)}")


@router.put("/{insight_id}", response_model=ConfigInsightResponse)
async def update_config_insight(insight_id: str, insight: ConfigurationInsight):
    """Update an existing configuration insight.

    Args:
        insight_id: ID of the insight to update
        insight: Updated ConfigurationInsight instance

    Returns:
        ConfigInsightResponse with success message

    Raises:
        HTTPException: 404 if insight not found, 500 if update fails
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        success = await manager.update_configuration_insight(insight_id, insight)
        if not success:
            raise HTTPException(status_code=404, detail=f"Configuration insight {insight_id} not found")

        return ConfigInsightResponse(
            insight_id=insight_id,
            message="Configuration insight updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update insight: {str(e)}")


@router.get("/", response_model=ConfigInsightSearchResponse)
async def search_config_insights(
    query: str = Query(..., description="Search query text"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results")
):
    """Search for configuration insights using semantic similarity.

    Args:
        query: Search query text describing configuration issue or pattern
        project_id: Optional project filter
        limit: Maximum number of results (1-100)

    Returns:
        ConfigInsightSearchResponse with matching insights and relevance scores

    Raises:
        HTTPException: 500 if search fails
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        results = await manager.search_configuration_insights(
            query=query,
            project_id=project_id,
            limit=limit
        )

        search_results = [
            ConfigInsightSearchResult(insight=insight, relevance_score=score)
            for insight, score in results
        ]

        return ConfigInsightSearchResponse(
            results=search_results,
            count=len(search_results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search configuration insights: {str(e)}")
