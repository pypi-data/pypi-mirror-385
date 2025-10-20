"""ConfigurationInsight model for storing configuration recommendations and patterns.

This module defines the ConfigurationInsight class which represents learned
configuration patterns, recommendations, and insights from project analysis.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field, validator


class InsightType(str, Enum):
    """Type of configuration insight."""
    RECOMMENDATION = "recommendation"
    PATTERN = "pattern"
    ANTI_PATTERN = "anti_pattern"
    BEST_PRACTICE = "best_practice"
    WARNING = "warning"
    OPTIMIZATION = "optimization"


class InsightCategory(str, Enum):
    """Category of configuration insight."""
    ARCHITECTURE = "architecture"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DEPLOYMENT = "deployment"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    MAINTENANCE = "maintenance"


class ConfidenceLevel(str, Enum):
    """Confidence level for insights."""
    LOW = "low"           # 0.0 - 0.3
    MEDIUM = "medium"     # 0.3 - 0.7
    HIGH = "high"         # 0.7 - 1.0


class ConfigurationInsight(BaseModel):
    """
    Represents a configuration insight, recommendation, or learned pattern.
    
    This model stores insights about configuration patterns, recommendations
    for improvements, and learned best practices from project analysis.
    """
    
    # Core identification
    insight_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: Optional[str] = Field(None, description="Specific project this insight applies to")
    
    # Insight classification
    insight_type: InsightType = Field(..., description="Type of insight")
    category: InsightCategory = Field(..., description="Category of configuration area")
    
    # Content
    title: str = Field(..., min_length=1, max_length=200, description="Brief title of the insight")
    description: str = Field(..., min_length=1, description="Detailed description of the insight")
    reasoning: str = Field(..., min_length=1, description="Why this insight is valuable")
    
    # Recommendation details
    current_config: Optional[Dict[str, Any]] = Field(None, description="Current configuration state")
    recommended_config: Optional[Dict[str, Any]] = Field(None, description="Recommended configuration")
    migration_steps: List[str] = Field(default_factory=list, description="Steps to implement recommendation")
    
    # Context and applicability
    applicable_technologies: List[str] = Field(default_factory=list, description="Technologies this applies to")
    project_types: List[str] = Field(default_factory=list, description="Project types this applies to")
    team_sizes: List[str] = Field(default_factory=list, description="Team sizes this is relevant for")
    
    # Evidence and validation
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in this insight")
    evidence_sources: List[str] = Field(default_factory=list, description="Sources of evidence for this insight")
    validation_count: int = Field(default=0, description="Number of times this has been validated")
    
    # Impact assessment
    impact_areas: List[str] = Field(default_factory=list, description="Areas that will be impacted")
    estimated_effort: Optional[str] = Field(None, description="Estimated effort to implement")
    expected_benefits: List[str] = Field(default_factory=list, description="Expected benefits")
    potential_risks: List[str] = Field(default_factory=list, description="Potential risks")
    
    # Usage tracking
    applied_count: int = Field(default=0, description="Number of times this insight was applied")
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Success rate when applied")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization and search")
    priority: int = Field(default=3, ge=1, le=5, description="Priority level (1=highest, 5=lowest)")
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_applied: Optional[datetime] = Field(None, description="When this insight was last applied")
    
    # Relationships
    related_insights: List[str] = Field(default_factory=list, description="IDs of related insights")
    superseded_by: Optional[str] = Field(None, description="ID of insight that supersedes this one")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('migration_steps')
    def validate_migration_steps(cls, v):
        """Validate migration steps are non-empty strings."""
        if v:
            for i, step in enumerate(v):
                if not isinstance(step, str) or not step.strip():
                    raise ValueError(f"Migration step {i} must be a non-empty string")
        return v
    
    @validator('applicable_technologies')
    def validate_technologies(cls, v):
        """Validate technology names."""
        if v:
            for tech in v:
                if not isinstance(tech, str) or not tech.strip():
                    raise ValueError("Technology names must be non-empty strings")
        return v
    
    @validator('evidence_sources')
    def validate_evidence_sources(cls, v):
        """Validate evidence sources."""
        if v:
            for source in v:
                if not isinstance(source, str) or not source.strip():
                    raise ValueError("Evidence sources must be non-empty strings")
        return v
    
    def get_confidence_level(self) -> ConfidenceLevel:
        """Get the confidence level based on confidence score."""
        if self.confidence_score <= 0.3:
            return ConfidenceLevel.LOW
        elif self.confidence_score <= 0.7:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.HIGH
    
    def add_evidence_source(self, source: str) -> None:
        """Add an evidence source if it doesn't already exist."""
        if source.strip() and source not in self.evidence_sources:
            self.evidence_sources.append(source.strip())
            self.updated_at = datetime.now(timezone.utc)
    
    def add_migration_step(self, step: str, position: Optional[int] = None) -> None:
        """Add a migration step at the specified position (or end if None)."""
        if not step.strip():
            raise ValueError("Migration step cannot be empty")
        
        if position is None:
            self.migration_steps.append(step.strip())
        else:
            self.migration_steps.insert(position, step.strip())
        
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_applied(self, success: bool) -> None:
        """Mark this insight as applied and update success rate."""
        self.applied_count += 1
        self.last_applied = datetime.now(timezone.utc)
        
        # Update success rate
        if success:
            # Calculate new success rate
            successful_applications = self.success_rate * (self.applied_count - 1) + 1
            self.success_rate = successful_applications / self.applied_count
        else:
            # Recalculate success rate
            successful_applications = self.success_rate * (self.applied_count - 1)
            self.success_rate = successful_applications / self.applied_count
        
        self.updated_at = datetime.now(timezone.utc)
    
    def increment_validation(self) -> None:
        """Increment the validation count."""
        self.validation_count += 1
        self.updated_at = datetime.now(timezone.utc)
    
    def add_related_insight(self, insight_id: str) -> None:
        """Add a related insight ID if it doesn't already exist."""
        if insight_id not in self.related_insights:
            self.related_insights.append(insight_id)
            self.updated_at = datetime.now(timezone.utc)
    
    def remove_related_insight(self, insight_id: str) -> bool:
        """Remove a related insight ID. Returns True if found and removed."""
        if insight_id in self.related_insights:
            self.related_insights.remove(insight_id)
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def supersede(self, new_insight_id: str) -> None:
        """Mark this insight as superseded by a new insight."""
        self.superseded_by = new_insight_id
        self.updated_at = datetime.now(timezone.utc)
    
    def is_applicable_to_project(self, project_type: Optional[str] = None, 
                               technologies: Optional[List[str]] = None,
                               team_size: Optional[str] = None) -> bool:
        """Check if this insight is applicable to a specific project context."""
        # If no specific criteria, assume applicable
        if not any([project_type, technologies, team_size]):
            return True
        
        # Check project type
        if project_type and self.project_types:
            if project_type not in self.project_types:
                return False
        
        # Check technologies (any overlap means applicable)
        if technologies and self.applicable_technologies:
            if not any(tech in self.applicable_technologies for tech in technologies):
                return False
        
        # Check team size
        if team_size and self.team_sizes:
            if team_size not in self.team_sizes:
                return False
        
        return True
    
    def has_tag(self, tag: str) -> bool:
        """Check if this insight has a specific tag."""
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
    
    def get_recommendation_text(self) -> str:
        """Generate human-readable recommendation text."""
        parts = [self.title, self.description, self.reasoning]
        
        if self.migration_steps:
            parts.append("Implementation steps:")
            parts.extend([f"{i+1}. {step}" for i, step in enumerate(self.migration_steps)])
        
        if self.expected_benefits:
            parts.append("Expected benefits:")
            parts.extend([f"- {benefit}" for benefit in self.expected_benefits])
        
        return "\n\n".join(parts)
    
    def to_search_text(self) -> str:
        """Generate searchable text representation."""
        parts = [
            self.title,
            self.description,
            self.reasoning,
            " ".join(self.applicable_technologies),
            " ".join(self.project_types),
            " ".join(self.tags),
            " ".join(self.impact_areas),
            " ".join(self.expected_benefits)
        ]
        
        return " ".join(parts)
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary for API responses."""
        return {
            "insight_id": self.insight_id,
            "project_id": self.project_id,
            "insight_type": self.insight_type.value,
            "category": self.category.value,
            "title": self.title,
            "confidence_score": self.confidence_score,
            "confidence_level": self.get_confidence_level().value,
            "priority": self.priority,
            "applied_count": self.applied_count,
            "success_rate": self.success_rate,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def create_recommendation(cls, title: str, description: str, reasoning: str,
                            category: InsightCategory, confidence_score: float,
                            project_id: Optional[str] = None,
                            **kwargs) -> ConfigurationInsight:
        """Create a new recommendation insight."""
        return cls(
            insight_type=InsightType.RECOMMENDATION,
            title=title,
            description=description,
            reasoning=reasoning,
            category=category,
            confidence_score=confidence_score,
            project_id=project_id,
            **kwargs
        )
    
    @classmethod
    def create_pattern(cls, title: str, description: str, reasoning: str,
                      category: InsightCategory, confidence_score: float,
                      pattern_type: InsightType = InsightType.PATTERN,
                      **kwargs) -> ConfigurationInsight:
        """Create a new pattern insight (pattern or anti-pattern)."""
        if pattern_type not in [InsightType.PATTERN, InsightType.ANTI_PATTERN]:
            raise ValueError("Pattern type must be PATTERN or ANTI_PATTERN")
        
        return cls(
            insight_type=pattern_type,
            title=title,
            description=description,
            reasoning=reasoning,
            category=category,
            confidence_score=confidence_score,
            **kwargs
        )