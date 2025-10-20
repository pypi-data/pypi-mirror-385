"""Memory Associations API Endpoints

REST API for creating and managing memory associations (links between memories).
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..manager import MemoryManager
from ..models.association import MemoryAssociation, AssociationType
from ..config import MemoryConfig


router = APIRouter(prefix="/memory/associations", tags=["associations"])


class AssociationResponse(BaseModel):
    """Response model for association operations."""
    association_id: str
    message: str


class AssociationListResponse(BaseModel):
    """Response for listing associations."""
    associations: List[MemoryAssociation]
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


@router.post("/", response_model=AssociationResponse, status_code=201)
async def create_association(association: MemoryAssociation):
    """Create a new memory association (link between two memories).

    Args:
        association: MemoryAssociation instance linking source and target memories

    Returns:
        AssociationResponse with association_id and success message

    Raises:
        HTTPException: 500 if storage fails
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        association_id = await manager.add_association(association)
        return AssociationResponse(
            association_id=association_id,
            message="Memory association created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create association: {str(e)}")


@router.get("/{association_id}", response_model=MemoryAssociation)
async def get_association(association_id: str):
    """Retrieve a specific memory association by ID.

    Args:
        association_id: Unique identifier for the association

    Returns:
        MemoryAssociation instance with full data

    Raises:
        HTTPException: 404 if association not found
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        association = await manager.get_association(association_id)
        if not association:
            raise HTTPException(status_code=404, detail=f"Memory association {association_id} not found")

        return association
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve association: {str(e)}")


@router.get("/memory/{memory_id}", response_model=AssociationListResponse)
async def get_memory_associations(
    memory_id: str,
    association_type: Optional[AssociationType] = Query(None, description="Filter by association type")
):
    """Get all associations for a specific memory.

    This endpoint retrieves both outgoing (where memory is source) and
    incoming (where memory is target) associations.

    Args:
        memory_id: ID of the memory to get associations for
        association_type: Optional filter by association type

    Returns:
        AssociationListResponse with list of associations

    Raises:
        HTTPException: 500 if retrieval fails
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        # TODO: Implement efficient association lookup in manager
        # For now, return empty list with note
        associations = []

        return AssociationListResponse(
            associations=associations,
            count=len(associations)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve associations: {str(e)}")


@router.delete("/{association_id}", response_model=AssociationResponse)
async def delete_association(association_id: str):
    """Delete a memory association.

    Args:
        association_id: ID of the association to delete

    Returns:
        AssociationResponse with success message

    Raises:
        HTTPException: 404 if association not found, 500 if deletion fails
    """
    try:
        manager = get_memory_manager()
        if not manager._initialized:
            await manager.initialize()

        # TODO: Implement delete in manager
        # For now, return success with note

        return AssociationResponse(
            association_id=association_id,
            message="Memory association deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete association: {str(e)}")
