"""Configuration Pattern Learning System

Learns from configuration patterns and insights to improve future recommendations
and adapt to project needs over time.
"""

from typing import List, Dict, Any, Optional, Tuple, Callable
from abc import ABC, abstractmethod
import logging
import asyncio
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
from dataclasses import dataclass

from .models.config_insight import ConfigurationInsight
from .models.project_context import ProjectContext, ProjectType
from .storage.base import StorageManager
from .config import MemoryConfig
from .config_analyzer import ConfigurationInsightAnalyzer

logger = logging.getLogger(__name__)


class LearningEventType(str, Enum):
    """Types of learning events."""
    INSIGHT_CREATED = "insight_created"
    INSIGHT_VALIDATED = "insight_validated"
    INSIGHT_REJECTED = "insight_rejected"
    PATTERN_DISCOVERED = "pattern_discovered"
    RECOMMENDATION_ACCEPTED = "recommendation_accepted"
    RECOMMENDATION_REJECTED = "recommendation_rejected"


class PatternType(str, Enum):
    """Types of configuration patterns."""
    TECH_STACK = "tech_stack"
    ARCHITECTURE = "architecture"
    BEST_PRACTICE = "best_practice"
    PERFORMANCE = "performance"
    SECURITY = "security"


@dataclass
class LearnedPattern:
    """Represents a learned configuration pattern."""
    pattern_id: str
    pattern_type: PatternType
    pattern_data: Dict[str, Any]
    confidence: float
    support_count: int
    last_updated: datetime
    applicability: List[str]  # Contexts where this pattern applies
    effectiveness_score: float
    metadata: Dict[str, Any]


class PatternLearningEngine(ABC):
    """Abstract base class for pattern learning engines."""
    
    @abstractmethod
    async def learn_from_insights(self, insights: List[ConfigurationInsight]) -> List[LearnedPattern]:
        """Learn from a set of configuration insights."""
        pass
    
    @abstractmethod
    async def get_relevant_patterns(self, project_context: ProjectContext) -> List[LearnedPattern]:
        """Get relevant patterns for a specific project context."""
        pass
    
    @abstractmethod
    async def update_pattern_effectiveness(self, pattern_id: str, was_helpful: bool) -> bool:
        """Update the effectiveness score of a pattern based on feedback."""
        pass


class ConfigurationPatternLearner(PatternLearningEngine):
    """Advanced pattern learning system for configuration insights."""
    
    def __init__(self, storage: StorageManager, config: MemoryConfig, 
                 analyzer: Optional[ConfigurationInsightAnalyzer] = None):
        self.storage = storage
        self.config = config
        self.analyzer = analyzer
        self._learned_patterns = {}  # In-memory cache of learned patterns
        self._pattern_usage_stats = {}
        self._feedback_buffer = []  # Buffer for feedback to process periodically
        self._min_support_threshold = config.get('pattern_learning.min_support', 3)
        self._learning_rate = config.get('pattern_learning.learning_rate', 0.1)
        
        # Initialize with default patterns
        self._initialize_default_patterns()
    
    def _initialize_default_patterns(self):
        """Initialize with some default patterns based on common best practices."""
        default_patterns = [
            {
                "pattern_id": "web_stack_postgres_redis",
                "pattern_type": PatternType.TECH_STACK,
                "pattern_data": {
                    "tech_stack": ["PostgreSQL", "Redis", "Nginx"],
                    "description": "Common web application stack with PostgreSQL for persistence, Redis for caching, and Nginx as reverse proxy"
                },
                "confidence": 0.9,
                "support_count": 50,
                "applicability": ["web_application", "high_performance"],
                "effectiveness_score": 0.85
            },
            {
                "pattern_id": "mobile_backend_mongodb",
                "pattern_type": PatternType.TECH_STACK,
                "pattern_data": {
                    "tech_stack": ["Node.js", "MongoDB", "Redis"],
                    "description": "Common mobile backend stack optimized for high read/write throughput"
                },
                "confidence": 0.85,
                "support_count": 30,
                "applicability": ["mobile_application", "high_throughput"],
                "effectiveness_score": 0.78
            }
        ]
        
        for pattern_data in default_patterns:
            pattern = LearnedPattern(
                pattern_id=pattern_data["pattern_id"],
                pattern_type=PatternType(pattern_data["pattern_type"]),
                pattern_data=pattern_data["pattern_data"],
                confidence=pattern_data["confidence"],
                support_count=pattern_data["support_count"],
                last_updated=datetime.now(),
                applicability=pattern_data["applicability"],
                effectiveness_score=pattern_data["effectiveness_score"],
                metadata={}
            )
            self._learned_patterns[pattern.pattern_id] = pattern
    
    async def learn_from_insights(self, insights: List[ConfigurationInsight]) -> List[LearnedPattern]:
        """Learn from a set of configuration insights."""
        new_patterns = []
        
        # Group insights by project to understand context
        project_insights = {}
        for insight in insights:
            if insight.project_id not in project_insights:
                project_insights[insight.project_id] = []
            project_insights[insight.project_id].append(insight)
        
        # Analyze each project's insights for patterns
        for project_id, project_insights_list in project_insights.items():
            # Look for recurring themes and patterns
            patterns_from_project = await self._extract_patterns_from_insights(
                project_insights_list, project_id
            )
            
            # Update existing patterns or create new ones
            for pattern_data in patterns_from_project:
                pattern_id = pattern_data["pattern_id"]
                
                if pattern_id in self._learned_patterns:
                    # Update existing pattern
                    self._update_existing_pattern(pattern_id, pattern_data)
                else:
                    # Create new pattern
                    new_pattern = LearnedPattern(
                        pattern_id=pattern_data["pattern_id"],
                        pattern_type=PatternType(pattern_data["pattern_type"]),
                        pattern_data=pattern_data["pattern_data"],
                        confidence=pattern_data["confidence"],
                        support_count=pattern_data["support_count"],
                        last_updated=datetime.now(),
                        applicability=pattern_data["applicability"],
                        effectiveness_score=pattern_data["effectiveness_score"],
                        metadata=pattern_data.get("metadata", {})
                    )
                    self._learned_patterns[pattern_id] = new_pattern
                    new_patterns.append(new_pattern)
        
        # Process any buffered feedback
        await self._process_feedback_buffer()
        
        logger.info(f"Learned from {len(insights)} insights, identified {len(new_patterns)} new patterns")
        return new_patterns
    
    async def _extract_patterns_from_insights(self, insights: List[ConfigurationInsight], 
                                           project_id: str) -> List[Dict[str, Any]]:
        """Extract patterns from a list of insights."""
        patterns = []
        
        # Count occurrences of different categories
        category_count = {}
        tech_mentions = []
        tags_count = {}
        
        for insight in insights:
            # Count categories
            category = insight.category.value
            category_count[category] = category_count.get(category, 0) + 1
            
            # Collect tech mentions from tags and descriptions
            tech_mentions.extend(insight.tags)
            # Extract tech terms from description (simplified)
            desc_lower = insight.description.lower()
            if "postgre" in desc_lower:
                tech_mentions.append("PostgreSQL")
            if "mongo" in desc_lower:
                tech_mentions.append("MongoDB")
            if "redis" in desc_lower:
                tech_mentions.append("Redis")
            if "node" in desc_lower and "js" in desc_lower:
                tech_mentions.append("Node.js")
            if "react" in desc_lower:
                tech_mentions.append("React")
            if "angular" in desc_lower:
                tech_mentions.append("Angular")
            
            # Count tags
            for tag in insight.tags:
                tags_count[tag] = tags_count.get(tag, 0) + 1
        
        # Create patterns based on common combinations
        if len([cat for cat, count in category_count.items() if count > 1]) > 0:
            # Create a category-based pattern
            primary_categories = [cat for cat, count in category_count.items() if count > 1]
            pattern_id = hashlib.md5(f"{project_id}_categories_{'_'.join(sorted(primary_categories))}".encode()).hexdigest()
            
            patterns.append({
                "pattern_id": pattern_id,
                "pattern_type": PatternType.BEST_PRACTICE,
                "pattern_data": {
                    "categories": primary_categories,
                    "description": f"Projects with {project_id} often have insights related to: {', '.join(primary_categories)}"
                },
                "confidence": min(0.9, len(primary_categories) * 0.2 + 0.5),
                "support_count": len([i for i in insights if i.category.value in primary_categories]),
                "applicability": [project_id] + primary_categories,
                "effectiveness_score": 0.7
            })
        
        # Create tech stack patterns
        if len(tech_mentions) >= 2:
            unique_tech = list(set(tech_mentions))
            if len(unique_tech) >= 2:
                pattern_id = hashlib.md5(f"{project_id}_tech_{'_'.join(sorted(unique_tech))}".encode()).hexdigest()
                
                patterns.append({
                    "pattern_id": pattern_id,
                    "pattern_type": PatternType.TECH_STACK,
                    "pattern_data": {
                        "tech_stack": unique_tech,
                        "description": f"Technology stack commonly used in: {project_id}"
                    },
                    "confidence": min(0.9, len(unique_tech) * 0.1 + 0.5),
                    "support_count": len(insights),
                    "applicability": [project_id, "tech_stack"] + unique_tech,
                    "effectiveness_score": 0.65
                })
        
        return patterns
    
    def _update_existing_pattern(self, pattern_id: str, new_pattern_data: Dict[str, Any]):
        """Update an existing pattern with new information."""
        existing_pattern = self._learned_patterns[pattern_id]
        
        # Update support count
        existing_pattern.support_count += new_pattern_data["support_count"]
        
        # Update confidence with weighted average
        total_support = existing_pattern.support_count
        existing_weight = (existing_pattern.support_count - new_pattern_data["support_count"]) / total_support
        new_weight = new_pattern_data["support_count"] / total_support
        
        existing_pattern.confidence = (
            existing_pattern.confidence * existing_weight + 
            new_pattern_data["confidence"] * new_weight
        )
        
        # Update effectiveness based on new feedback
        old_effectiveness = existing_pattern.effectiveness_score
        new_effectiveness = new_pattern_data["effectiveness_score"]
        existing_pattern.effectiveness_score = (
            old_effectiveness * existing_weight + 
            new_effectiveness * new_weight
        )
        
        # Update last updated time
        existing_pattern.last_updated = datetime.now()
        
        # Merge applicability contexts
        existing_pattern.applicability = list(
            set(existing_pattern.applicability + new_pattern_data["applicability"])
        )
    
    async def get_relevant_patterns(self, project_context: ProjectContext) -> List[LearnedPattern]:
        """Get relevant patterns for a specific project context."""
        relevant_patterns = []
        
        # Determine which patterns might apply based on project characteristics
        project_characteristics = set([
            project_context.project_type.value,
            *project_context.tech_stack,
            *project_context.tags,
            "project"
        ])
        
        # Add any keywords from description
        desc_lower = project_context.description.lower()
        if "web" in desc_lower:
            project_characteristics.add("web_application")
        if "mobile" in desc_lower:
            project_characteristics.add("mobile_application")
        if "data" in desc_lower or "pipeline" in desc_lower:
            project_characteristics.add("data_pipeline")
        if "machine" in desc_lower or "ml" in desc_lower or "ai" in desc_lower:
            project_characteristics.add("machine_learning")
        if "api" in desc_lower or "service" in desc_lower:
            project_characteristics.add("api")
        
        # Find patterns that match these characteristics
        for pattern_id, pattern in self._learned_patterns.items():
            # Check if any applicability matches project characteristics
            if any(char in pattern.applicability for char in project_characteristics):
                # Also check if pattern has minimum support
                if pattern.support_count >= self._min_support_threshold:
                    relevant_patterns.append(pattern)
        
        # Sort by effectiveness score and confidence
        relevant_patterns.sort(
            key=lambda p: (p.effectiveness_score * 0.6 + p.confidence * 0.4), 
            reverse=True
        )
        
        return relevant_patterns
    
    async def update_pattern_effectiveness(self, pattern_id: str, was_helpful: bool) -> bool:
        """Update the effectiveness score of a pattern based on feedback."""
        if pattern_id not in self._learned_patterns:
            return False
        
        pattern = self._learned_patterns[pattern_id]
        
        # Add to feedback buffer to process later
        self._feedback_buffer.append({
            "pattern_id": pattern_id,
            "was_helpful": was_helpful,
            "timestamp": datetime.now()
        })
        
        # Process feedback periodically (every 10 feedback items)
        if len(self._feedback_buffer) >= 10:
            await self._process_feedback_buffer()
        
        return True
    
    async def _process_feedback_buffer(self):
        """Process buffered feedback to update pattern effectiveness."""
        if not self._feedback_buffer:
            return
        
        # Group feedback by pattern ID
        feedback_by_pattern = {}
        for feedback in self._feedback_buffer:
            pid = feedback["pattern_id"]
            if pid not in feedback_by_pattern:
                feedback_by_pattern[pid] = []
            feedback_by_pattern[pid].append(feedback)
        
        # Update each pattern's effectiveness based on its feedback
        for pattern_id, feedback_list in feedback_by_pattern.items():
            if pattern_id in self._learned_patterns:
                pattern = self._learned_patterns[pattern_id]
                
                # Calculate new effectiveness score
                helpful_count = sum(1 for f in feedback_list if f["was_helpful"])
                total_feedback = len(feedback_list)
                
                if total_feedback > 0:
                    feedback_score = helpful_count / total_feedback
                    
                    # Update effectiveness with learning rate
                    old_score = pattern.effectiveness_score
                    new_score = (
                        old_score * (1 - self._learning_rate) + 
                        feedback_score * self._learning_rate
                    )
                    
                    pattern.effectiveness_score = new_score
                    pattern.last_updated = datetime.now()
        
        # Clear the buffer
        self._feedback_buffer = []
    
    async def generate_personalized_recommendations(self, project_context: ProjectContext) -> List[ConfigurationInsight]:
        """Generate personalized configuration recommendations based on learned patterns."""
        relevant_patterns = await self.get_relevant_patterns(project_context)
        
        # Convert patterns to ConfigurationInsight objects
        recommendations = []
        
        for pattern in relevant_patterns[:5]:  # Limit to top 5 patterns
            title = f"Pattern Recommendation: {pattern.pattern_type.value.title().replace('_', ' ')}"
            description = pattern.pattern_data.get("description", f"Learned pattern for {pattern.pattern_type.value}")
            
            # Create a ConfigurationInsight based on the pattern
            recommendation = ConfigurationInsight.create_insight(
                project_id=project_context.project_id,
                title=title,
                description=description,
                category=self._map_pattern_type_to_category(pattern.pattern_type),
                confidence_score=min(0.95, pattern.effectiveness_score),
                recommendation=f"Consider implementing this pattern: {json.dumps(pattern.pattern_data)}",
                applicable_contexts=pattern.applicability,
                tags=[pattern.pattern_type.value, "learned_pattern", "recommendation"]
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _map_pattern_type_to_category(self, pattern_type: PatternType) -> str:
        """Map pattern type to configuration category."""
        # This would typically map to actual enum values
        # For now, return a string representation
        return pattern_type.value.upper()
    
    async def get_learning_statistics(self) -> Dict[str, Any]:
        """Get statistics about the learning system."""
        total_patterns = len(self._learned_patterns)
        total_feedback = len(self._feedback_buffer)
        
        # Calculate average effectiveness and confidence
        if total_patterns > 0:
            avg_effectiveness = sum(p.effectiveness_score for p in self._learned_patterns.values()) / total_patterns
            avg_confidence = sum(p.confidence for p in self._learned_patterns.values()) / total_patterns
        else:
            avg_effectiveness = 0
            avg_confidence = 0
        
        # Breakdown by pattern type
        type_breakdown = {}
        for pattern in self._learned_patterns.values():
            ptype = pattern.pattern_type.value
            if ptype not in type_breakdown:
                type_breakdown[ptype] = 0
            type_breakdown[ptype] += 1
        
        return {
            "total_patterns": total_patterns,
            "average_effectiveness": avg_effectiveness,
            "average_confidence": avg_confidence,
            "patterns_by_type": type_breakdown,
            "total_feedback_buffered": total_feedback,
            "last_learning_update": datetime.now().isoformat()
        }
    
    async def forget_patterns_older_than(self, days: int) -> int:
        """Forget patterns that haven't been updated in the specified number of days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        patterns_to_remove = []
        for pattern_id, pattern in self._learned_patterns.items():
            if pattern.last_updated < cutoff_date:
                patterns_to_remove.append(pattern_id)
        
        for pattern_id in patterns_to_remove:
            del self._learned_patterns[pattern_id]
        
        logger.info(f"Removed {len(patterns_to_remove)} patterns older than {days} days")
        return len(patterns_to_remove)


class AdaptiveConfigurationLearner:
    """Higher-level component that adapts configuration learning to specific project needs."""
    
    def __init__(self, pattern_learner: ConfigurationPatternLearner):
        self.pattern_learner = pattern_learner
        self._adaptation_history = []
        self._project_learning_profiles = {}
    
    async def adapt_to_project(self, project_context: ProjectContext) -> Dict[str, Any]:
        """Adapt learning approach based on project characteristics."""
        project_id = project_context.project_id
        
        # Create or update learning profile for this project
        if project_id not in self._project_learning_profiles:
            self._project_learning_profiles[project_id] = {
                "project_type": project_context.project_type.value,
                "tech_stack": project_context.tech_stack,
                "created_at": datetime.now(),
                "interaction_count": 0,
                "success_rate": 0.0,
                "preferred_patterns": [],
                "avoided_patterns": []
            }
        
        profile = self._project_learning_profiles[project_id]
        profile["interaction_count"] += 1
        
        # Get relevant patterns for this project
        relevant_patterns = await self.pattern_learner.get_relevant_patterns(project_context)
        
        # Identify which patterns have been most successful for this project type
        successful_patterns = [
            p for p in relevant_patterns 
            if p.effectiveness_score > 0.7 and p.confidence > 0.7
        ]
        
        # Update profile with preferred patterns
        profile["preferred_patterns"] = [p.pattern_id for p in successful_patterns[:5]]
        
        adaptation_result = {
            "project_id": project_id,
            "adapted_patterns_count": len(successful_patterns),
            "recommended_actions": [
                "Focus on patterns with high effectiveness scores",
                "Monitor new pattern effectiveness",
                f"Suggested patterns for {project_context.project_type.value} projects"
            ],
            "profile_updated": datetime.now().isoformat()
        }
        
        self._adaptation_history.append(adaptation_result)
        
        return adaptation_result
    
    async def get_adaptation_recommendations(self, project_context: ProjectContext) -> List[str]:
        """Get recommendations for adapting configuration learning to this project."""
        recommendations = []
        
        # Based on project type
        if project_context.project_type == ProjectType.WEB_APPLICATION:
            recommendations.append("Focus on scalability and performance patterns")
            recommendations.append("Prioritize security configuration patterns")
            recommendations.append("Consider deployment and CI/CD patterns")
        elif project_context.project_type == ProjectType.MOBILE_APPLICATION:
            recommendations.append("Emphasize offline capability patterns")
            recommendations.append("Focus on battery and network efficiency patterns")
            recommendations.append("Prioritize security and privacy configurations")
        elif project_context.project_type == ProjectType.DATA_PIPELINE:
            recommendations.append("Prioritize reliability and monitoring patterns")
            recommendations.append("Focus on data quality and lineage configurations")
            recommendations.append("Consider performance optimization patterns")
        elif project_context.project_type == ProjectType.MACHINE_LEARNING:
            recommendations.append("Emphasize model management configurations")
            recommendations.append("Focus on experiment tracking patterns")
            recommendations.append("Prioritize data pipeline configurations")
        
        # Based on tech stack
        if "Kubernetes" in project_context.tech_stack or "Docker" in project_context.tech_stack:
            recommendations.append("Consider container orchestration patterns")
            recommendations.append("Focus on deployment configuration patterns")
        
        if "PostgreSQL" in project_context.tech_stack:
            recommendations.append("Look for database optimization patterns")
            recommendations.append("Consider backup and replication configurations")
        
        return recommendations
    
    def get_learning_adaptation_history(self) -> List[Dict[str, Any]]:
        """Get history of learning adaptations."""
        return self._adaptation_history
    
    async def evaluate_pattern_effectiveness(self, pattern_id: str, project_context: ProjectContext) -> Dict[str, Any]:
        """Evaluate how well a pattern works for a specific project context."""
        # This would normally run a detailed evaluation
        # For now, return a simplified assessment
        if pattern_id not in self.pattern_learner._learned_patterns:
            return {"error": "Pattern not found"}
        
        pattern = self.pattern_learner._learned_patterns[pattern_id]
        
        # Assess applicability based on project characteristics
        applicable = len(set(pattern.applicability) & set([
            project_context.project_type.value,
            *project_context.tech_stack,
            *project_context.tags
        ])) > 0
        
        # Combine pattern metrics
        assessment = {
            "pattern_id": pattern_id,
            "applicable_to_project": applicable,
            "pattern_confidence": pattern.confidence,
            "pattern_effectiveness": pattern.effectiveness_score,
            "support_count": pattern.support_count,
            "project_match_score": 0.0  # Would be calculated based on detailed analysis
        }
        
        # Calculate match score based on project characteristics
        if applicable:
            # Simple scoring based on various factors
            base_score = pattern.effectiveness_score * 0.4 + pattern.confidence * 0.3 + (min(1.0, pattern.support_count / 10) * 0.3)
            assessment["project_match_score"] = base_score
        
        return assessment