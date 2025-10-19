"""AgentKnowledge model for storing agent-specific learning and expertise.

This module defines the AgentKnowledge class which represents learned
knowledge, patterns, and expertise specific to individual agents.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field, validator


class KnowledgeType(str, Enum):
    """Type of agent knowledge."""
    SKILL = "skill"
    PATTERN = "pattern"
    TECHNIQUE = "technique"
    PREFERENCE = "preference"
    LIMITATION = "limitation"
    SPECIALIZATION = "specialization"


class KnowledgeCategory(str, Enum):
    """Category of agent knowledge."""
    PROGRAMMING = "programming"
    ARCHITECTURE = "architecture"
    DEBUGGING = "debugging"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    COMMUNICATION = "communication"
    PROJECT_MANAGEMENT = "project_management"
    DOMAIN_EXPERTISE = "domain_expertise"


class ProficiencyLevel(str, Enum):
    """Proficiency level for knowledge areas."""
    BEGINNER = "beginner"        # 0.0 - 0.3
    INTERMEDIATE = "intermediate" # 0.3 - 0.7
    ADVANCED = "advanced"        # 0.7 - 0.9
    EXPERT = "expert"           # 0.9 - 1.0


class AgentKnowledge(BaseModel):
    """
    Represents agent-specific knowledge, skills, and learned patterns.
    
    This model stores what an agent has learned, their areas of expertise,
    preferences, and performance patterns for different types of tasks.
    """
    
    # Core identification
    knowledge_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: str = Field(..., description="Type of agent this knowledge belongs to")
    
    # Knowledge classification
    knowledge_type: KnowledgeType = Field(..., description="Type of knowledge")
    category: KnowledgeCategory = Field(..., description="Category of knowledge")
    
    # Content
    title: str = Field(..., min_length=1, max_length=200, description="Brief title of the knowledge")
    description: str = Field(..., min_length=1, description="Detailed description of the knowledge")
    context: str = Field(..., min_length=1, description="Context in which this knowledge applies")
    
    # Proficiency and confidence
    proficiency_score: float = Field(..., ge=0.0, le=1.0, description="Agent's proficiency in this area")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in this knowledge")
    
    # Knowledge details
    key_concepts: List[str] = Field(default_factory=list, description="Key concepts in this knowledge area")
    related_technologies: List[str] = Field(default_factory=list, description="Technologies related to this knowledge")
    common_patterns: List[Dict[str, Any]] = Field(default_factory=list, description="Common patterns the agent uses")
    
    # Performance tracking
    usage_count: int = Field(default=0, description="Number of times this knowledge was applied")
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Success rate when applying this knowledge")
    avg_completion_time: Optional[float] = Field(None, description="Average time to complete tasks using this knowledge (minutes)")
    
    # Learning and improvement
    learning_sources: List[str] = Field(default_factory=list, description="Sources where this knowledge was learned")
    improvement_areas: List[str] = Field(default_factory=list, description="Areas for improvement")
    recent_learnings: List[Dict[str, Any]] = Field(default_factory=list, description="Recent learning updates")
    
    # Context applicability
    effective_contexts: List[str] = Field(default_factory=list, description="Contexts where this knowledge is most effective")
    limitations: List[str] = Field(default_factory=list, description="Known limitations or constraints")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies or prerequisites")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization and search")
    priority: int = Field(default=3, ge=1, le=5, description="Priority level (1=highest, 5=lowest)")
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: Optional[datetime] = Field(None, description="When this knowledge was last applied")
    last_improved: Optional[datetime] = Field(None, description="When this knowledge was last updated/improved")
    
    # Relationships
    related_knowledge: List[str] = Field(default_factory=list, description="IDs of related knowledge items")
    superseded_by: Optional[str] = Field(None, description="ID of knowledge that supersedes this one")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('key_concepts')
    def validate_key_concepts(cls, v):
        """Validate key concepts are non-empty strings."""
        if v:
            for concept in v:
                if not isinstance(concept, str) or not concept.strip():
                    raise ValueError("Key concepts must be non-empty strings")
        return v
    
    @validator('common_patterns')
    def validate_common_patterns(cls, v):
        """Validate common patterns have required structure."""
        if not v:
            return v
        
        for i, pattern in enumerate(v):
            if not isinstance(pattern, dict):
                raise ValueError(f"Pattern {i} must be a dictionary")
            
            if 'name' not in pattern or 'description' not in pattern:
                raise ValueError(f"Pattern {i} must have 'name' and 'description' fields")
        
        return v
    
    @validator('recent_learnings')
    def validate_recent_learnings(cls, v):
        """Validate recent learnings have required structure."""
        if not v:
            return v
        
        for i, learning in enumerate(v):
            if not isinstance(learning, dict):
                raise ValueError(f"Learning {i} must be a dictionary")
            
            required_fields = ['learning', 'timestamp']
            for field in required_fields:
                if field not in learning:
                    raise ValueError(f"Learning {i} missing required field: {field}")
        
        return v
    
    def get_proficiency_level(self) -> ProficiencyLevel:
        """Get the proficiency level based on proficiency score."""
        if self.proficiency_score < 0.3:
            return ProficiencyLevel.BEGINNER
        elif self.proficiency_score < 0.7:
            return ProficiencyLevel.INTERMEDIATE
        elif self.proficiency_score < 0.9:
            return ProficiencyLevel.ADVANCED
        else:
            return ProficiencyLevel.EXPERT
    
    def add_key_concept(self, concept: str) -> None:
        """Add a key concept if it doesn't already exist."""
        if concept.strip() and concept not in self.key_concepts:
            self.key_concepts.append(concept.strip())
            self.updated_at = datetime.now(timezone.utc)
    
    def add_pattern(self, name: str, description: str, effectiveness: Optional[float] = None, 
                   metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a common pattern."""
        pattern = {
            "name": name,
            "description": description,
            "effectiveness": effectiveness,
            "metadata": metadata or {},
            "added_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.common_patterns.append(pattern)
        self.updated_at = datetime.now(timezone.utc)
    
    def add_learning(self, learning: str, source: Optional[str] = None, 
                    impact: Optional[str] = None) -> None:
        """Add a recent learning."""
        learning_record = {
            "learning": learning,
            "source": source,
            "impact": impact,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.recent_learnings.append(learning_record)
        self.last_improved = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_used(self, success: bool, completion_time: Optional[float] = None) -> None:
        """Mark this knowledge as used and update performance metrics."""
        self.usage_count += 1
        self.last_used = datetime.now(timezone.utc)
        
        # Update success rate
        if success:
            successful_uses = self.success_rate * (self.usage_count - 1) + 1
            self.success_rate = successful_uses / self.usage_count
        else:
            successful_uses = self.success_rate * (self.usage_count - 1)
            self.success_rate = successful_uses / self.usage_count
        
        # Update average completion time
        if completion_time is not None:
            if self.avg_completion_time is None:
                self.avg_completion_time = completion_time
            else:
                # Calculate rolling average
                total_time = self.avg_completion_time * (self.usage_count - 1) + completion_time
                self.avg_completion_time = total_time / self.usage_count
        
        self.updated_at = datetime.now(timezone.utc)
    
    def update_proficiency(self, new_score: float, reason: Optional[str] = None) -> None:
        """Update proficiency score with optional reason."""
        if not 0.0 <= new_score <= 1.0:
            raise ValueError("Proficiency score must be between 0.0 and 1.0")
        
        old_score = self.proficiency_score
        self.proficiency_score = new_score
        self.last_improved = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        
        # Add learning record about proficiency change
        if reason:
            change_type = "improved" if new_score > old_score else "adjusted"
            learning = f"Proficiency {change_type} from {old_score:.2f} to {new_score:.2f}: {reason}"
            self.add_learning(learning, source="proficiency_update")
    
    def add_improvement_area(self, area: str) -> None:
        """Add an area for improvement if it doesn't already exist."""
        if area.strip() and area not in self.improvement_areas:
            self.improvement_areas.append(area.strip())
            self.updated_at = datetime.now(timezone.utc)
    
    def remove_improvement_area(self, area: str) -> bool:
        """Remove an improvement area. Returns True if found and removed."""
        if area in self.improvement_areas:
            self.improvement_areas.remove(area)
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def add_limitation(self, limitation: str) -> None:
        """Add a limitation if it doesn't already exist."""
        if limitation.strip() and limitation not in self.limitations:
            self.limitations.append(limitation.strip())
            self.updated_at = datetime.now(timezone.utc)
    
    def is_effective_in_context(self, context: str) -> bool:
        """Check if this knowledge is effective in a given context."""
        if not self.effective_contexts:
            return True  # No specific contexts means generally applicable
        
        return any(ctx.lower() in context.lower() or context.lower() in ctx.lower() 
                  for ctx in self.effective_contexts)
    
    def get_related_technologies(self) -> List[str]:
        """Get all related technologies."""
        return self.related_technologies.copy()
    
    def add_related_technology(self, technology: str) -> None:
        """Add a related technology if it doesn't already exist."""
        if technology.strip() and technology not in self.related_technologies:
            self.related_technologies.append(technology.strip())
            self.updated_at = datetime.now(timezone.utc)
    
    def has_tag(self, tag: str) -> bool:
        """Check if this knowledge has a specific tag."""
        return tag.lower() in [t.lower() for t in self.tags]
    
    def add_tag(self, tag: str) -> None:
        """Add a tag if it doesn't already exist."""
        if not self.has_tag(tag) and tag.strip():
            self.tags.append(tag.strip())
            self.updated_at = datetime.now(timezone.utc)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for this knowledge area."""
        return {
            "proficiency_level": self.get_proficiency_level().value,
            "proficiency_score": self.proficiency_score,
            "confidence_score": self.confidence_score,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "avg_completion_time": self.avg_completion_time,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "improvement_areas_count": len(self.improvement_areas),
            "patterns_count": len(self.common_patterns)
        }
    
    def to_search_text(self) -> str:
        """Generate searchable text representation."""
        parts = [
            self.title,
            self.description,
            self.context,
            " ".join(self.key_concepts),
            " ".join(self.related_technologies),
            " ".join(self.effective_contexts),
            " ".join(self.tags)
        ]
        
        # Add pattern names
        pattern_names = [pattern.get('name', '') for pattern in self.common_patterns]
        parts.append(" ".join(pattern_names))
        
        return " ".join(parts)
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary for API responses."""
        return {
            "knowledge_id": self.knowledge_id,
            "agent_type": self.agent_type,
            "knowledge_type": self.knowledge_type.value,
            "category": self.category.value,
            "title": self.title,
            "proficiency_level": self.get_proficiency_level().value,
            "proficiency_score": self.proficiency_score,
            "confidence_score": self.confidence_score,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None
        }
    
    @classmethod
    def create_skill(cls, agent_type: str, title: str, description: str, context: str,
                    proficiency_score: float, category: KnowledgeCategory = KnowledgeCategory.PROGRAMMING,
                    **kwargs) -> AgentKnowledge:
        """Create a new skill knowledge entry."""
        return cls(
            agent_type=agent_type,
            knowledge_type=KnowledgeType.SKILL,
            category=category,
            title=title,
            description=description,
            context=context,
            proficiency_score=proficiency_score,
            confidence_score=proficiency_score,  # Default confidence to proficiency
            **kwargs
        )
    
    @classmethod
    def create_pattern(cls, agent_type: str, title: str, description: str, context: str,
                      effectiveness: float, category: KnowledgeCategory = KnowledgeCategory.PROGRAMMING,
                      **kwargs) -> AgentKnowledge:
        """Create a new pattern knowledge entry."""
        return cls(
            agent_type=agent_type,
            knowledge_type=KnowledgeType.PATTERN,
            category=category,
            title=title,
            description=description,
            context=context,
            proficiency_score=effectiveness,
            confidence_score=effectiveness,
            **kwargs
        )