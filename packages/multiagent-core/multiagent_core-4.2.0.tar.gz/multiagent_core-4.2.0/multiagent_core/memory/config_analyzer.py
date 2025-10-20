"""Configuration Insight Analyzer

Analyzes configuration patterns, trends, and insights from memory system
to provide recommendations and learning for future configuration decisions.
"""

from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
import logging
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, Counter
import re

from .models.config_insight import ConfigurationInsight, ConfigurationCategory
from .models.project_context import ProjectContext, ProjectType
from .storage.base import StorageManager
from .config import MemoryConfig

logger = logging.getLogger(__name__)


class InsightQuality(str, Enum):
    """Enumeration of insight quality levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ConfigurationTrend(str, Enum):
    """Types of configuration trends."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class ConfigurationAnalyzer(ABC):
    """Abstract base class for configuration analysis."""
    
    @abstractmethod
    async def analyze_project_config(self, project_context: ProjectContext) -> List[ConfigurationInsight]:
        """Analyze a project's configuration for insights."""
        pass
    
    @abstractmethod
    async def identify_patterns(self, project_id: str) -> List[Dict[str, Any]]:
        """Identify configuration patterns for a project."""
        pass


class ConfigurationInsightAnalyzer(ConfigurationAnalyzer):
    """Advanced analyzer for configuration insights and patterns."""
    
    def __init__(self, storage: StorageManager, config: MemoryConfig):
        self.storage = storage
        self.config = config
        self._pattern_cache = {}
        self._analysis_cache = {}
        self.cache_ttl = config.get('config_analyzer.cache_ttl', 600)  # 10 minutes default
    
    async def analyze_project_config(self, project_context: ProjectContext) -> List[ConfigurationInsight]:
        """Analyze a project's configuration for insights."""
        start_time = datetime.now()
        
        # Check cache first
        cache_key = f"analysis:{project_context.project_id}"
        if cache_key in self._analysis_cache:
            cached_result, timestamp = self._analysis_cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                logger.debug(f"Cache hit for project config analysis: {project_context.project_id}")
                return cached_result
        
        insights = []
        
        # Analyze tech stack
        tech_insights = await self._analyze_tech_stack(project_context)
        insights.extend(tech_insights)
        
        # Analyze architectural decisions
        arch_insights = await self._analyze_architectural_decisions(project_context)
        insights.extend(arch_insights)
        
        # Analyze project type characteristics
        type_insights = await self._analyze_project_type(project_context)
        insights.extend(type_insights)
        
        # Check for configuration conflicts or issues
        conflict_insights = await self._analyze_for_conflicts(project_context)
        insights.extend(conflict_insights)
        
        # Add context-specific recommendations
        rec_insights = await self._generate_recommendations(project_context)
        insights.extend(rec_insights)
        
        # Cache the results
        self._analysis_cache[cache_key] = (insights, datetime.now())
        
        logger.info(f"Configuration analysis completed for project {project_context.project_id} in {(datetime.now() - start_time).total_seconds():.3f}s. Generated {len(insights)} insights.")
        
        return insights
    
    async def _analyze_tech_stack(self, project_context: ProjectContext) -> List[ConfigurationInsight]:
        """Analyze the technology stack for insights."""
        insights = []
        
        tech_stack = project_context.tech_stack
        if not tech_stack:
            return insights
        
        # Look for common combinations that work well together
        tech_combinations = await self._find_common_tech_combinations()
        
        for i, tech1 in enumerate(tech_stack):
            for tech2 in tech_stack[i+1:]:
                combo_key = f"{tech1.lower()}-{tech2.lower()}"
                if combo_key in tech_combinations or f"{tech2.lower()}-{tech1.lower()}" in tech_combinations:
                    # Found a known good combination
                    insight = ConfigurationInsight.create_insight(
                        project_id=project_context.project_id,
                        title=f"Technology Combination: {tech1} + {tech2}",
                        description=f"The combination of {tech1} and {tech2} has been successful in similar projects.",
                        category=ConfigurationCategory.TECH_STACK,
                        confidence_score=0.85,
                        recommendation=f"Consider leveraging the synergies between {tech1} and {tech2} in your architecture.",
                        applicable_contexts=["tech_stack", "architecture", "integration"],
                        tags=["tech_combination", "integration", "architecture"]
                    )
                    insights.append(insight)
        
        # Analyze for potential issues with tech stack
        known_issues = await self._find_known_tech_issues(tech_stack)
        for tech, issues in known_issues.items():
            for issue, severity in issues:
                insight = ConfigurationInsight.create_insight(
                    project_id=project_context.project_id,
                    title=f"Potential Issue with {tech}",
                    description=issue,
                    category=ConfigurationCategory.PERFORMANCE,
                    confidence_score=severity,
                    recommendation=f"Review your usage of {tech} to address: {issue}",
                    applicable_contexts=["tech_stack", "performance", "security"],
                    tags=["issue", "risk", f"{tech.lower()}_specific"]
                )
                insights.append(insight)
        
        return insights
    
    async def _analyze_architectural_decisions(self, project_context: ProjectContext) -> List[ConfigurationInsight]:
        """Analyze architectural decisions for insights."""
        insights = []
        
        if not project_context.architectural_decisions:
            return insights
        
        # Analyze each architectural decision for patterns
        for decision in project_context.architectural_decisions:
            # Look for common architectural patterns
            if "microservice" in decision.lower():
                insight = ConfigurationInsight.create_insight(
                    project_id=project_context.project_id,
                    title="Microservices Pattern Detected",
                    description="Your architecture includes microservices, which offers scalability benefits.",
                    category=ConfigurationCategory.DESIGN_PATTERN,
                    confidence_score=0.9,
                    recommendation="Ensure proper service boundaries and implement appropriate communication patterns like event-driven architecture or API gateways.",
                    applicable_contexts=["architecture", "microservices", "scalability"],
                    tags=["microservices", "architecture", "scalability"]
                )
                insights.append(insight)
            elif "monolith" in decision.lower() or "monolithic" in decision.lower():
                insight = ConfigurationInsight.create_insight(
                    project_id=project_context.project_id,
                    title="Monolithic Architecture Pattern Detected",
                    description="Your architecture is monolithic, which can simplify initial development but may impact scalability.",
                    category=ConfigurationCategory.DESIGN_PATTERN,
                    confidence_score=0.8,
                    recommendation="Consider future scalability needs and plan for potential refactoring to microservices when appropriate.",
                    applicable_contexts=["architecture", "monolith", "scalability"],
                    tags=["monolith", "architecture", "scalability"]
                )
                insights.append(insight)
            elif "event-driven" in decision.lower() or "event driven" in decision.lower():
                insight = ConfigurationInsight.create_insight(
                    project_id=project_context.project_id,
                    title="Event-Driven Architecture Pattern Detected",
                    description="Your architecture includes event-driven patterns, which can improve scalability and decoupling.",
                    category=ConfigurationCategory.DESIGN_PATTERN,
                    confidence_score=0.85,
                    recommendation="Implement proper event sourcing, consider using message queues, and ensure you handle event ordering and idempotency.",
                    applicable_contexts=["architecture", "event_driven", "scalability"],
                    tags=["event_driven", "architecture", "best_practices"]
                )
                insights.append(insight)
        
        return insights
    
    async def _analyze_project_type(self, project_context: ProjectContext) -> List[ConfigurationInsight]:
        """Analyze based on project type for insights."""
        insights = []
        
        project_type = project_context.project_type
        
        # Common best practices for different project types
        type_best_practices = {
            ProjectType.WEB_APPLICATION: [
                ("Web Application Security", "Web applications need robust security measures including HTTPS, CORS policies, and input validation.", 0.95),
                ("Web Performance", "Web applications should prioritize performance with proper caching, asset optimization, and efficient API design.", 0.9),
            ],
            ProjectType.MOBILE_APPLICATION: [
                ("Mobile Performance", "Mobile applications must optimize for battery life, network efficiency, and offline capabilities.", 0.9),
                ("Mobile Security", "Mobile apps need secure storage, certificate pinning, and proper authentication mechanisms.", 0.85),
            ],
            ProjectType.DATA_PIPELINE: [
                ("Data Pipeline Reliability", "Data pipelines need monitoring, error handling, and retry mechanisms for reliability.", 0.95),
                ("Data Pipeline Performance", "Optimize for throughput and latency, consider parallel processing patterns.", 0.85),
            ],
            ProjectType.MACHINE_LEARNING: [
                ("ML Model Management", "Implement versioning, monitoring, and A/B testing for ML models.", 0.9),
                ("ML Data Management", "Ensure data quality, lineage, and reproducibility in your ML pipeline.", 0.88),
            ]
        }
        
        if project_type in type_best_practices:
            for title, description, confidence in type_best_practices[project_type]:
                insight = ConfigurationInsight.create_insight(
                    project_id=project_context.project_id,
                    title=title,
                    description=description,
                    category=ConfigurationCategory.BEST_PRACTICE,
                    confidence_score=confidence,
                    recommendation=f"Implement the best practice of: {description}",
                    applicable_contexts=["architecture", "best_practices", project_type.value],
                    tags=["best_practice", project_type.value, "configuration"]
                )
                insights.append(insight)
        
        return insights
    
    async def _analyze_for_conflicts(self, project_context: ProjectContext) -> List[ConfigurationInsight]:
        """Analyze for potential configuration conflicts."""
        insights = []
        
        tech_stack = project_context.tech_stack
        if len(tech_stack) < 2:
            return insights
        
        # Look for potentially conflicting technologies
        conflict_patterns = [
            (["Angular", "React", "Vue.js"], "Using multiple competing frontend frameworks can cause bloat and maintenance issues."),
            (["MySQL", "PostgreSQL"], "Using multiple similar databases may complicate data management."),
            (["Docker", "Kubernetes"], "These work together but require careful orchestration planning.")
        ]
        
        for conflict_group, description in conflict_patterns:
            found_conflicts = [tech for tech in tech_stack if tech in conflict_group]
            if len(found_conflicts) > 1:
                insight = ConfigurationInsight.create_insight(
                    project_id=project_context.project_id,
                    title=f"Potential Technology Conflict: {', '.join(found_conflicts)}",
                    description=description,
                    category=ConfigurationCategory.PERFORMANCE,
                    confidence_score=0.75,
                    recommendation=f"Review usage of {', '.join(found_conflicts)} to ensure they complement rather than conflict with each other.",
                    applicable_contexts=["tech_stack", "integration", "conflict_resolution"],
                    tags=["conflict", "integration", "architecture"]
                )
                insights.append(insight)
        
        return insights
    
    async def _generate_recommendations(self, project_context: ProjectContext) -> List[ConfigurationInsight]:
        """Generate context-specific recommendations."""
        insights = []
        
        # Generate recommendations based on project context
        if "real-time" in project_context.description.lower() or "real time" in project_context.description.lower():
            insight = ConfigurationInsight.create_insight(
                project_id=project_context.project_id,
                title="Real-time Application Considerations",
                description="Your project involves real-time processing which has specific performance and architectural requirements.",
                category=ConfigurationCategory.PERFORMANCE,
                confidence_score=0.85,
                recommendation="Consider using WebSocket connections, message queues like Redis or RabbitMQ, and optimizing for low latency.",
                applicable_contexts=["real_time", "performance", "architecture"],
                tags=["real_time", "performance", "best_practices"]
            )
            insights.append(insight)
        
        # Check for high-traffic indicators
        if any(word in project_context.description.lower() for word in ["high traffic", "scalability", "scale", "millions"]):
            insight = ConfigurationInsight.create_insight(
                project_id=project_context.project_id,
                title="High Traffic Application Considerations",
                description="Your project appears to target high traffic which requires special architectural considerations.",
                category=ConfigurationCategory.PERFORMANCE,
                confidence_score=0.9,
                recommendation="Implement caching strategies (Redis, CDN), load balancing, horizontal scaling capabilities, and performance monitoring.",
                applicable_contexts=["performance", "scalability", "high_traffic"],
                tags=["scalability", "performance", "traffic"]
            )
            insights.append(insight)
        
        return insights
    
    async def _find_common_tech_combinations(self) -> List[str]:
        """Find common technology combinations from historical data."""
        # This would normally query historical data to find common tech stack combinations
        # For now, return some common ones
        return [
            "react-node.js",
            "angular-node.js",
            "vue.js-node.js",
            "python-django",
            "python-flask",
            "java-spring",
            "node.js-express",
            "postgresql-redis",
            "mysql-redis"
        ]
    
    async def _find_known_tech_issues(self, tech_stack: List[str]) -> Dict[str, List[Tuple[str, float]]]:
        """Find known issues with technologies in the stack."""
        # This would normally query a knowledge base of known issues
        # For now, return some common ones based on tech names
        issues = {}
        
        tech_lower = [t.lower() for t in tech_stack]
        
        if any("react" in t for t in tech_lower):
            issues["React"] = [("Performance issues with large component trees", 0.7)]
        if any("angular" in t for t in tech_lower):
            issues["Angular"] = [("Bundle size can become large without proper optimization", 0.6)]
        if any("python" in t for t in tech_lower):
            issues["Python"] = [("GIL limitation for CPU-intensive tasks", 0.5)]
        if any("node.js" in t for t in tech_lower):
            issues["Node.js"] = [("Single-threaded nature can be limiting for CPU-intensive operations", 0.6)]
        if any("mysql" in t for t in tech_lower):
            issues["MySQL"] = [("Can have performance issues with complex joins on large datasets", 0.6)]
        
        return issues
    
    async def identify_patterns(self, project_id: str) -> List[Dict[str, Any]]:
        """Identify configuration patterns across projects."""
        start_time = datetime.now()
        
        # Check cache first
        cache_key = f"patterns:{project_id}"
        if cache_key in self._pattern_cache:
            cached_result, timestamp = self._pattern_cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                logger.debug(f"Pattern cache hit for project: {project_id}")
                return cached_result
        
        # Get all configuration insights for this project
        insights = await self._get_config_insights_for_project(project_id)
        
        patterns = []
        
        # Analyze for common themes in insights
        category_counter = Counter([insight.category for insight in insights])
        tag_counter = Counter()
        for insight in insights:
            for tag in insight.tags:
                tag_counter[tag] += 1
        
        # Add category patterns
        for category, count in category_counter.most_common():
            patterns.append({
                "pattern_type": "category_frequency",
                "category": category,
                "frequency": count,
                "percentage": count / len(insights) if insights else 0
            })
        
        # Add tag patterns
        for tag, count in tag_counter.most_common(10):  # Top 10 tags
            patterns.append({
                "pattern_type": "tag_frequency",
                "tag": tag,
                "frequency": count,
                "percentage": count / sum(tag_counter.values()) if tag_counter else 0
            })
        
        # Analyze confidence score trends
        if insights:
            avg_confidence = sum(insight.confidence_score for insight in insights) / len(insights)
            patterns.append({
                "pattern_type": "confidence_trend",
                "average_confidence": avg_confidence,
                "total_insights": len(insights)
            })
        
        # Cache the results
        self._pattern_cache[cache_key] = (patterns, datetime.now())
        
        logger.info(f"Pattern identification completed for project {project_id} in {(datetime.now() - start_time).total_seconds():.3f}s. Found {len(patterns)} patterns.")
        
        return patterns
    
    async def _get_config_insights_for_project(self, project_id: str) -> List[ConfigurationInsight]:
        """Get all configuration insights for a project."""
        # This would normally query the storage for configuration insights
        # For now, we'll create a placeholder implementation
        insights = []
        
        try:
            # Fetch relevant configuration insight records from storage
            # This is a simplified approach - in real implementation, you'd have efficient queries
            results = await self.storage.metadata_store.list_memory_type(
                memory_type=ConfigurationCategory.__class__.__name__  # This needs to be corrected
            )
            
            # In actual implementation, we'd query for CONFIGURATION_INSIGHT type
            # For now, let's assume we have a method to get configuration insights
            # This is a placeholder - real implementation would query the database
            pass
        except Exception as e:
            logger.warning(f"Could not retrieve config insights for project {project_id}: {e}")
        
        # For demo purposes, return some sample insights
        return []
    
    async def get_configuration_recommendations(self, project_id: str) -> List[ConfigurationInsight]:
        """Get configuration recommendations based on analysis."""
        insights = await self._get_config_insights_for_project(project_id)
        
        # Filter for high-confidence recommendations
        recommendations = [
            insight for insight in insights 
            if insight.category in [ConfigurationCategory.BEST_PRACTICE, ConfigurationCategory.PERFORMANCE] 
            and insight.confidence_score >= 0.7
        ]
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        return recommendations
    
    async def analyze_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analyze configuration trends over time."""
        start_date = datetime.now() - timedelta(days=days)
        
        # This would normally query for configuration insights created in the specified time period
        # For now, let's return a placeholder structure
        trends = {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": datetime.now().isoformat(),
            "category_trends": {},
            "technology_trends": {},
            "quality_trends": {}
        }
        
        # In a real implementation, we would:
        # 1. Query insights created in the specified time period
        # 2. Analyze trends in categories
        # 3. Analyze trends in technologies mentioned
        # 4. Analyze trends in quality/confidence scores
        
        # Placeholder implementation
        return trends
    
    async def validate_insights(self, insights: List[ConfigurationInsight]) -> List[Tuple[ConfigurationInsight, bool, str]]:
        """Validate a list of insights for quality and relevance."""
        results = []
        
        for insight in insights:
            is_valid = True
            reason = "Valid"
            
            # Check if the insight has required fields
            if not insight.title or not insight.title.strip():
                is_valid = False
                reason = "Missing title"
            elif not insight.description or not insight.description.strip():
                is_valid = False
                reason = "Missing description"
            elif insight.confidence_score < 0.1 or insight.confidence_score > 1.0:
                is_valid = False
                reason = "Confidence score out of range"
            elif not insight.applicable_contexts:
                is_valid = False
                reason = "Missing applicable contexts"
            
            results.append((insight, is_valid, reason))
        
        return results


class ConfigurationPatternAnalyzer:
    """Analyzes configuration patterns to identify common trends and best practices."""
    
    def __init__(self, analyzer: ConfigurationInsightAnalyzer):
        self.analyzer = analyzer
    
    async def find_best_practices(self, project_type: Optional[ProjectType] = None) -> List[Dict[str, Any]]:
        """Find best practices based on pattern analysis."""
        # This would normally analyze multiple projects to identify effective patterns
        # For now, return a placeholder
        best_practices = []
        
        # In real implementation, analyze multiple projects of the same type
        # to identify the most effective configurations
        return best_practices
    
    async def predict_configuration_success(self, config_elements: List[str]) -> Dict[str, Any]:
        """Predict the success likelihood of a configuration based on patterns."""
        # Analyze the configuration elements against historical patterns
        # This is a simplified implementation
        success_score = 0.5  # Default neutral score
        
        # Look for successful patterns
        successful_patterns = [
            ["PostgreSQL", "Redis", "Nginx"],  # Common successful web stack
            ["Kubernetes", "Docker", "Prometheus"],  # Common successful deployment stack
        ]
        
        for pattern in successful_patterns:
            if all(elem in config_elements for elem in pattern):
                success_score += 0.2
        
        # Look for potentially problematic patterns
        problematic_patterns = [
            ["Angular", "React"],  # Multiple competing frameworks
        ]
        
        for pattern in problematic_patterns:
            if all(elem in config_elements for elem in pattern):
                success_score -= 0.2
        
        # Ensure score is between 0 and 1
        success_score = max(0.0, min(1.0, success_score))
        
        return {
            "success_score": success_score,
            "confidence": 0.7,  # Default confidence
            "factors": [],
            "recommendations": []
        }
    
    async def generate_config_template(self, project_type: ProjectType, 
                                      requirements: List[str] = None) -> Dict[str, Any]:
        """Generate a configuration template based on analysis of similar projects."""
        # This would normally generate a template based on successful projects of the same type
        template = {
            "project_type": project_type.value,
            "recommended_tech_stack": [],
            "architecture_patterns": [],
            "best_practices": [],
            "configuration_considerations": []
        }
        
        # Common templates by project type
        if project_type == ProjectType.WEB_APPLICATION:
            template["recommended_tech_stack"] = ["React or Vue.js", "Node.js or Django", "PostgreSQL or MongoDB", "Redis", "Nginx"]
            template["architecture_patterns"] = ["REST API", "Component-based UI", "Microservices (if complex)"]
            template["best_practices"] = ["Security headers", "CORS policies", "Asset optimization", "Caching strategies"]
        elif project_type == ProjectType.MOBILE_APPLICATION:
            template["recommended_tech_stack"] = ["React Native or Flutter", "Node.js backend", "PostgreSQL", "Redis"]
            template["architecture_patterns"] = ["API-first", "Offline-first approach", "Event-driven"]
            template["best_practices"] = ["Secure storage", "Certificate pinning", "Battery optimization", "Network efficiency"]
        elif project_type == ProjectType.DATA_PIPELINE:
            template["recommended_tech_stack"] = ["Apache Kafka", "Airflow", "PostgreSQL", "Redis", "Docker"]
            template["architecture_patterns"] = ["Event sourcing", "Stream processing", "Micro-batch processing"]
            template["best_practices"] = ["Monitoring", "Error handling", "Data lineage", "Idempotency"]
        elif project_type == ProjectType.MACHINE_LEARNING:
            template["recommended_tech_stack"] = ["Python", "TensorFlow or PyTorch", "MLflow", "Docker", "Kubernetes"]
            template["architecture_patterns"] = ["Model versioning", "Feature stores", "MLOps pipeline"]
            template["best_practices"] = ["Experiment tracking", "Model monitoring", "Data validation", "A/B testing"]
        
        return template