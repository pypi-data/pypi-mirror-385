"""ProjectContext model for project-specific settings and architectural decisions.

This module defines the ProjectContext class which represents project-specific
configuration, architectural decisions, technology stack, and team preferences.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field, validator


class ProjectType(str, Enum):
    """Type of project."""
    WEB_APPLICATION = "web-application"
    MOBILE_APP = "mobile-app"
    API_SERVICE = "api-service"
    DESKTOP_APP = "desktop-app"
    LIBRARY = "library"
    PROTOTYPE = "prototype"
    MICROSERVICE = "microservice"
    CLI_TOOL = "cli-tool"


class TeamSize(str, Enum):
    """Team size categories."""
    SOLO = "solo"           # 1 person
    SMALL = "small"         # 2-5 people
    MEDIUM = "medium"       # 6-15 people
    LARGE = "large"         # 16+ people


class ProjectContext(BaseModel):
    """
    Represents project-specific context, configuration, and architectural decisions.
    
    This model stores information about a project's technology stack, team
    preferences, architectural decisions, and configuration patterns.
    """
    
    # Core identification
    context_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = Field(..., description="Unique project identifier")
    project_name: Optional[str] = Field(None, description="Human-readable project name")
    
    # Project classification
    project_type: ProjectType = Field(..., description="Type of project")
    team_size: Optional[TeamSize] = Field(None, description="Size of the development team")
    
    # Technology stack
    technology_stack: Dict[str, List[str]] = Field(default_factory=dict, description="Technology stack by category")
    primary_languages: List[str] = Field(default_factory=list, description="Primary programming languages")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks and libraries used")
    
    # Architectural decisions
    architectural_decisions: List[Dict[str, Any]] = Field(default_factory=list, description="Key architectural decisions")
    design_patterns: List[str] = Field(default_factory=list, description="Design patterns used in the project")
    
    # Development practices
    coding_standards: Dict[str, Any] = Field(default_factory=dict, description="Coding standards and style guides")
    team_preferences: Dict[str, Any] = Field(default_factory=dict, description="Team preferences and workflows")
    development_workflow: Optional[str] = Field(None, description="Development workflow description")
    
    # Configuration and deployment
    deployment_targets: List[str] = Field(default_factory=list, description="Target deployment environments")
    configuration_patterns: Dict[str, Any] = Field(default_factory=dict, description="Configuration patterns and settings")
    environment_setup: Dict[str, Any] = Field(default_factory=dict, description="Environment setup requirements")
    
    # Project requirements and constraints
    performance_requirements: Dict[str, Any] = Field(default_factory=dict, description="Performance requirements")
    security_requirements: List[str] = Field(default_factory=list, description="Security requirements and constraints")
    compliance_requirements: List[str] = Field(default_factory=list, description="Compliance and regulatory requirements")
    
    # Learning and adaptation
    lessons_learned: List[Dict[str, Any]] = Field(default_factory=list, description="Lessons learned during development")
    pain_points: List[str] = Field(default_factory=list, description="Known pain points and challenges")
    success_factors: List[str] = Field(default_factory=list, description="Factors that contribute to success")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization and search")
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_reviewed: Optional[datetime] = Field(None, description="When this context was last reviewed")
    
    # Relationships
    similar_projects: List[str] = Field(default_factory=list, description="IDs of similar projects")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('architectural_decisions')
    def validate_architectural_decisions(cls, v):
        """Validate architectural decisions have required structure."""
        if not v:
            return v
        
        for i, decision in enumerate(v):
            if not isinstance(decision, dict):
                raise ValueError(f"Decision {i} must be a dictionary")
            
            required_fields = ['decision', 'reasoning', 'date']
            for field in required_fields:
                if field not in decision:
                    raise ValueError(f"Decision {i} missing required field: {field}")
        
        return v
    
    @validator('lessons_learned')
    def validate_lessons_learned(cls, v):
        """Validate lessons learned have required structure."""
        if not v:
            return v
        
        for i, lesson in enumerate(v):
            if not isinstance(lesson, dict):
                raise ValueError(f"Lesson {i} must be a dictionary")
            
            required_fields = ['lesson', 'context', 'date']
            for field in required_fields:
                if field not in lesson:
                    raise ValueError(f"Lesson {i} missing required field: {field}")
        
        return v
    
    def add_technology(self, category: str, technology: str) -> None:
        """Add a technology to the stack under a specific category."""
        if category not in self.technology_stack:
            self.technology_stack[category] = []
        
        if technology.strip() and technology not in self.technology_stack[category]:
            self.technology_stack[category].append(technology.strip())
            self.updated_at = datetime.now(timezone.utc)
    
    def remove_technology(self, category: str, technology: str) -> bool:
        """Remove a technology from the stack. Returns True if found and removed."""
        if category in self.technology_stack and technology in self.technology_stack[category]:
            self.technology_stack[category].remove(technology)
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def add_architectural_decision(self, decision: str, reasoning: str, confidence: float = 0.8,
                                 impact: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add an architectural decision."""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        decision_record = {
            "decision": decision,
            "reasoning": reasoning,
            "confidence": confidence,
            "impact": impact,
            "date": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }
        
        self.architectural_decisions.append(decision_record)
        self.updated_at = datetime.now(timezone.utc)
    
    def add_lesson_learned(self, lesson: str, context: str, impact: Optional[str] = None,
                          category: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a lesson learned."""
        lesson_record = {
            "lesson": lesson,
            "context": context,
            "impact": impact,
            "category": category,
            "date": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }
        
        self.lessons_learned.append(lesson_record)
        self.updated_at = datetime.now(timezone.utc)
    
    def add_pain_point(self, pain_point: str) -> None:
        """Add a pain point if it doesn't already exist."""
        if pain_point.strip() and pain_point not in self.pain_points:
            self.pain_points.append(pain_point.strip())
            self.updated_at = datetime.now(timezone.utc)
    
    def add_success_factor(self, factor: str) -> None:
        """Add a success factor if it doesn't already exist."""
        if factor.strip() and factor not in self.success_factors:
            self.success_factors.append(factor.strip())
            self.updated_at = datetime.now(timezone.utc)
    
    def set_coding_standard(self, language: str, standard: Dict[str, Any]) -> None:
        """Set coding standards for a specific language."""
        if language not in self.coding_standards:
            self.coding_standards[language] = {}
        
        self.coding_standards[language].update(standard)
        self.updated_at = datetime.now(timezone.utc)
    
    def set_team_preference(self, preference_type: str, value: Any) -> None:
        """Set a team preference."""
        self.team_preferences[preference_type] = value
        self.updated_at = datetime.now(timezone.utc)
    
    def get_all_technologies(self) -> List[str]:
        """Get all technologies from all categories."""
        all_techs = []
        for techs in self.technology_stack.values():
            all_techs.extend(techs)
        
        # Add primary languages and frameworks
        all_techs.extend(self.primary_languages)
        all_techs.extend(self.frameworks)
        
        return list(set(all_techs))  # Remove duplicates
    
    def has_technology(self, technology: str) -> bool:
        """Check if project uses a specific technology."""
        return technology in self.get_all_technologies()
    
    def get_recent_decisions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most recent architectural decisions."""
        sorted_decisions = sorted(
            self.architectural_decisions,
            key=lambda x: x.get('date', ''),
            reverse=True
        )
        return sorted_decisions[:limit]
    
    def get_recent_lessons(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most recent lessons learned."""
        sorted_lessons = sorted(
            self.lessons_learned,
            key=lambda x: x.get('date', ''),
            reverse=True
        )
        return sorted_lessons[:limit]
    
    def calculate_similarity_score(self, other_project: ProjectContext) -> float:
        """Calculate similarity score with another project (0.0 to 1.0)."""
        score = 0.0
        factors = 0
        
        # Project type match (20% weight)
        if self.project_type == other_project.project_type:
            score += 0.2
        factors += 0.2
        
        # Team size match (10% weight)
        if self.team_size and other_project.team_size:
            if self.team_size == other_project.team_size:
                score += 0.1
            factors += 0.1
        
        # Technology overlap (50% weight)
        self_techs = set(self.get_all_technologies())
        other_techs = set(other_project.get_all_technologies())
        
        if self_techs and other_techs:
            tech_overlap = len(self_techs.intersection(other_techs))
            tech_union = len(self_techs.union(other_techs))
            tech_similarity = tech_overlap / tech_union if tech_union > 0 else 0
            score += tech_similarity * 0.5
        factors += 0.5
        
        # Design patterns overlap (20% weight)
        self_patterns = set(self.design_patterns)
        other_patterns = set(other_project.design_patterns)
        
        if self_patterns and other_patterns:
            pattern_overlap = len(self_patterns.intersection(other_patterns))
            pattern_union = len(self_patterns.union(other_patterns))
            pattern_similarity = pattern_overlap / pattern_union if pattern_union > 0 else 0
            score += pattern_similarity * 0.2
        factors += 0.2
        
        return score / factors if factors > 0 else 0.0
    
    def mark_reviewed(self) -> None:
        """Mark this context as reviewed."""
        self.last_reviewed = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def has_tag(self, tag: str) -> bool:
        """Check if this context has a specific tag."""
        return tag.lower() in [t.lower() for t in self.tags]
    
    def add_tag(self, tag: str) -> None:
        """Add a tag if it doesn't already exist."""
        if not self.has_tag(tag) and tag.strip():
            self.tags.append(tag.strip())
            self.updated_at = datetime.now(timezone.utc)
    
    def to_search_text(self) -> str:
        """Generate searchable text representation."""
        parts = [
            self.project_name or '',
            self.project_type.value,
            self.development_workflow or '',
            ' '.join(self.get_all_technologies()),
            ' '.join(self.design_patterns),
            ' '.join(self.deployment_targets),
            ' '.join(self.security_requirements),
            ' '.join(self.pain_points),
            ' '.join(self.success_factors),
            ' '.join(self.tags)
        ]
        
        # Add decision text
        decision_text = [d.get('decision', '') for d in self.architectural_decisions]
        parts.extend(decision_text)
        
        # Add lesson text
        lesson_text = [l.get('lesson', '') for l in self.lessons_learned]
        parts.extend(lesson_text)
        
        return ' '.join(parts)
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary for API responses."""
        return {
            "context_id": self.context_id,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "project_type": self.project_type.value,
            "team_size": self.team_size.value if self.team_size else None,
            "primary_languages": self.primary_languages,
            "frameworks": self.frameworks[:5],  # Limit for summary
            "decision_count": len(self.architectural_decisions),
            "lesson_count": len(self.lessons_learned),
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_reviewed": self.last_reviewed.isoformat() if self.last_reviewed else None
        }
    
    @classmethod
    def create_from_api_data(cls, data: Dict[str, Any]) -> ProjectContext:
        """Create ProjectContext from API request data."""
        return cls(
            project_id=data['project_id'],
            project_name=data.get('project_name'),
            project_type=ProjectType(data['project_type']),
            team_size=TeamSize(data['team_size']) if data.get('team_size') else None,
            technology_stack=data.get('technology_stack', {}),
            primary_languages=data.get('primary_languages', []),
            frameworks=data.get('frameworks', []),
            coding_standards=data.get('coding_standards', {}),
            team_preferences=data.get('team_preferences', {}),
            development_workflow=data.get('development_workflow'),
            deployment_targets=data.get('deployment_targets', []),
            performance_requirements=data.get('performance_requirements', {}),
            security_requirements=data.get('security_requirements', []),
            tags=data.get('tags', [])
        )