"""MemoryAssociation model for linking related memories with strength scoring.

This module defines the MemoryAssociation class which represents relationships
between different memory items with strength scoring and relationship metadata.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field, validator


class AssociationType(str, Enum):
    """Type of memory association."""
    RELATED = "related"           # General relatedness
    FOLLOWS = "follows"           # Sequential relationship
    CONTRADICTS = "contradicts"   # Conflicting information
    ELABORATES = "elaborates"     # Expands on previous memory
    SIMILAR = "similar"          # Similar content or context
    DEPENDENCY = "dependency"     # One depends on the other
    ALTERNATIVE = "alternative"   # Alternative approach or solution


class MemoryType(str, Enum):
    """Type of memory item being associated."""
    CONVERSATION = "conversation"
    CONFIG_INSIGHT = "config_insight"
    AGENT_KNOWLEDGE = "agent_knowledge"
    PROJECT_CONTEXT = "project_context"


class MemoryAssociation(BaseModel):
    """
    Represents a relationship between two memory items.
    
    This model stores associations between different types of memories,
    including the strength of the relationship and contextual metadata.
    """
    
    # Core identification
    association_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Source and target memories
    source_memory_id: str = Field(..., description="ID of the source memory")
    source_memory_type: MemoryType = Field(..., description="Type of the source memory")
    target_memory_id: str = Field(..., description="ID of the target memory")
    target_memory_type: MemoryType = Field(..., description="Type of the target memory")
    
    # Association properties
    association_type: AssociationType = Field(..., description="Type of association")
    strength: float = Field(..., ge=0.0, le=1.0, description="Strength of the association")
    bidirectional: bool = Field(default=True, description="Whether the association works both ways")
    
    # Context and reasoning
    reasoning: Optional[str] = Field(None, description="Why these memories are associated")
    context: Optional[str] = Field(None, description="Context in which the association was created")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in this association")
    
    # Evidence and validation
    evidence_sources: List[str] = Field(default_factory=list, description="Sources of evidence for this association")
    validation_count: int = Field(default=0, description="Number of times this association was validated")
    
    # Usage tracking
    access_count: int = Field(default=0, description="Number of times this association was accessed")
    last_accessed: Optional[datetime] = Field(None, description="When this association was last accessed")
    
    # Quality metrics
    user_feedback: List[Dict[str, Any]] = Field(default_factory=list, description="User feedback on this association")
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Computed relevance score")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = Field(None, description="When this association expires")
    
    # Creator information
    created_by: Optional[str] = Field(None, description="Who or what created this association")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('source_memory_id')
    def validate_source_memory_id(cls, v):
        """Validate source memory ID is not empty."""
        if not v or not v.strip():
            raise ValueError("Source memory ID cannot be empty")
        return v
    
    @validator('target_memory_id')
    def validate_target_memory_id(cls, v):
        """Validate target memory ID is not empty."""
        if not v or not v.strip():
            raise ValueError("Target memory ID cannot be empty")
        return v
    
    @validator('user_feedback')
    def validate_user_feedback(cls, v):
        """Validate user feedback has required structure."""
        if not v:
            return v
        
        for i, feedback in enumerate(v):
            if not isinstance(feedback, dict):
                raise ValueError(f"Feedback {i} must be a dictionary")
            
            required_fields = ['rating', 'timestamp']
            for field in required_fields:
                if field not in feedback:
                    raise ValueError(f"Feedback {i} missing required field: {field}")
            
            # Validate rating is between 1-5
            rating = feedback.get('rating')
            if not isinstance(rating, (int, float)) or not 1 <= rating <= 5:
                raise ValueError(f"Feedback {i} rating must be between 1 and 5")
        
        return v
    
    def __post_init__(self):
        """Post-initialization validation."""
        # Ensure source and target are different
        if self.source_memory_id == self.target_memory_id:
            raise ValueError("Source and target memory IDs cannot be the same")
    
    def mark_accessed(self) -> None:
        """Mark this association as accessed."""
        self.access_count += 1
        self.last_accessed = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def add_evidence_source(self, source: str) -> None:
        """Add an evidence source if it doesn't already exist."""
        if source.strip() and source not in self.evidence_sources:
            self.evidence_sources.append(source.strip())
            self.updated_at = datetime.now(timezone.utc)
    
    def increment_validation(self) -> None:
        """Increment the validation count."""
        self.validation_count += 1
        self.updated_at = datetime.now(timezone.utc)
    
    def add_user_feedback(self, rating: int, comment: Optional[str] = None, 
                         user_id: Optional[str] = None) -> None:
        """Add user feedback for this association."""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        feedback = {
            "rating": rating,
            "comment": comment,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.user_feedback.append(feedback)
        self.updated_at = datetime.now(timezone.utc)
    
    def calculate_relevance_score(self) -> float:
        """Calculate and update the relevance score based on various factors."""
        score = self.strength  # Base score from strength
        
        # Factor in confidence
        score = (score * 0.7) + (self.confidence * 0.3)
        
        # Factor in validation count (more validations = higher relevance)
        validation_bonus = min(self.validation_count * 0.1, 0.3)  # Cap at 0.3
        score += validation_bonus
        
        # Factor in user feedback
        if self.user_feedback:
            avg_rating = sum(f['rating'] for f in self.user_feedback) / len(self.user_feedback)
            feedback_score = (avg_rating - 1) / 4  # Normalize 1-5 rating to 0-1
            score = (score * 0.8) + (feedback_score * 0.2)
        
        # Factor in access count (more accessed = more relevant)
        access_bonus = min(self.access_count * 0.01, 0.1)  # Cap at 0.1
        score += access_bonus
        
        # Ensure score stays within bounds
        score = max(0.0, min(1.0, score))
        
        self.relevance_score = score
        self.updated_at = datetime.now(timezone.utc)
        
        return score
    
    def get_average_user_rating(self) -> Optional[float]:
        """Get the average user rating for this association."""
        if not self.user_feedback:
            return None
        
        total_rating = sum(f['rating'] for f in self.user_feedback)
        return total_rating / len(self.user_feedback)
    
    def is_expired(self) -> bool:
        """Check if this association has expired."""
        if self.expires_at is None:
            return False
        
        return datetime.now(timezone.utc) > self.expires_at
    
    def set_expiration(self, expires_at: datetime) -> None:
        """Set expiration time for this association."""
        self.expires_at = expires_at
        self.updated_at = datetime.now(timezone.utc)
    
    def update_strength(self, new_strength: float, reason: Optional[str] = None) -> None:
        """Update the association strength."""
        if not 0.0 <= new_strength <= 1.0:
            raise ValueError("Strength must be between 0.0 and 1.0")
        
        old_strength = self.strength
        self.strength = new_strength
        self.updated_at = datetime.now(timezone.utc)
        
        # Add to metadata
        if reason:
            if 'strength_updates' not in self.metadata:
                self.metadata['strength_updates'] = []
            
            update_record = {
                "old_strength": old_strength,
                "new_strength": new_strength,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self.metadata['strength_updates'].append(update_record)
    
    def get_opposite_memory(self, memory_id: str) -> Optional[Dict[str, str]]:
        """Get the opposite memory in this association given one memory ID."""
        if memory_id == self.source_memory_id:
            return {
                "memory_id": self.target_memory_id,
                "memory_type": self.target_memory_type.value
            }
        elif memory_id == self.target_memory_id:
            return {
                "memory_id": self.source_memory_id,
                "memory_type": self.source_memory_type.value
            }
        else:
            return None
    
    def involves_memory(self, memory_id: str) -> bool:
        """Check if this association involves a specific memory."""
        return memory_id in [self.source_memory_id, self.target_memory_id]
    
    def involves_memory_type(self, memory_type: MemoryType) -> bool:
        """Check if this association involves a specific memory type."""
        return memory_type in [self.source_memory_type, self.target_memory_type]
    
    def has_tag(self, tag: str) -> bool:
        """Check if this association has a specific tag."""
        return tag.lower() in [t.lower() for t in self.tags]
    
    def add_tag(self, tag: str) -> None:
        """Add a tag if it doesn't already exist."""
        if not self.has_tag(tag) and tag.strip():
            self.tags.append(tag.strip())
            self.updated_at = datetime.now(timezone.utc)
    
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag. Returns True if tag was found and removed."""
        original_length = len(self.tags)
        self.tags = [t for t in self.tags if t.lower() != tag.lower()]
        
        if len(self.tags) < original_length:
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary for API responses."""
        return {
            "association_id": self.association_id,
            "source_memory_id": self.source_memory_id,
            "source_memory_type": self.source_memory_type.value,
            "target_memory_id": self.target_memory_id,
            "target_memory_type": self.target_memory_type.value,
            "association_type": self.association_type.value,
            "strength": self.strength,
            "confidence": self.confidence,
            "relevance_score": self.relevance_score,
            "bidirectional": self.bidirectional,
            "access_count": self.access_count,
            "validation_count": self.validation_count,
            "average_rating": self.get_average_user_rating(),
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "is_expired": self.is_expired()
        }
    
    @classmethod
    def create_association(cls, source_memory_id: str, source_memory_type: MemoryType,
                          target_memory_id: str, target_memory_type: MemoryType,
                          association_type: AssociationType, strength: float,
                          reasoning: Optional[str] = None, **kwargs) -> MemoryAssociation:
        """Create a new memory association."""
        return cls(
            source_memory_id=source_memory_id,
            source_memory_type=source_memory_type,
            target_memory_id=target_memory_id,
            target_memory_type=target_memory_type,
            association_type=association_type,
            strength=strength,
            reasoning=reasoning,
            **kwargs
        )
    
    @classmethod
    def create_similarity_association(cls, memory1_id: str, memory1_type: MemoryType,
                                    memory2_id: str, memory2_type: MemoryType,
                                    similarity_score: float, **kwargs) -> MemoryAssociation:
        """Create a similarity association between two memories."""
        return cls.create_association(
            source_memory_id=memory1_id,
            source_memory_type=memory1_type,
            target_memory_id=memory2_id,
            target_memory_type=memory2_type,
            association_type=AssociationType.SIMILAR,
            strength=similarity_score,
            reasoning="Automatically detected similarity",
            **kwargs
        )