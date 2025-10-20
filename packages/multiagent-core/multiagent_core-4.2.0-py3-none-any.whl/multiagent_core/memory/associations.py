"""Memory Association Engine

Advanced association engine for discovering and managing relationships
between different memory items with intelligent pattern recognition.
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from abc import ABC, abstractmethod
import logging
import asyncio
from datetime import datetime, timedelta
from enum import Enum

from .models.association import MemoryAssociation, AssociationType, MemoryType
from .models.conversation import ConversationMemory
from .models.config_insight import ConfigurationInsight
from .models.agent_knowledge import AgentKnowledge
from .models.project_context import ProjectContext
from .storage.base import StorageManager
from .config import MemoryConfig

logger = logging.getLogger(__name__)


class AssociationStrength(str, Enum):
    """Enumeration of association strength levels."""
    WEAK = "weak"       # 0.1 - 0.3
    MODERATE = "moderate"  # 0.3 - 0.6
    STRONG = "strong"     # 0.6 - 0.8
    VERY_STRONG = "very_strong"  # 0.8 - 1.0


class AssociationRule:
    """A rule for creating associations between memories based on patterns."""
    
    def __init__(self, 
                 source_type: MemoryType,
                 target_type: MemoryType,
                 condition_func,
                 strength_func,
                 description: str = ""):
        self.source_type = source_type
        self.target_type = target_type
        self.condition_func = condition_func
        self.strength_func = strength_func
        self.description = description
    
    async def applies(self, source_memory, target_memory) -> bool:
        """Check if this rule applies to the given memory pair."""
        return await self.condition_func(source_memory, target_memory)
    
    async def calculate_strength(self, source_memory, target_memory) -> float:
        """Calculate association strength based on this rule."""
        return await self.strength_func(source_memory, target_memory)


class AssociationEngine(ABC):
    """Abstract base class for association engines."""
    
    @abstractmethod
    async def find_associations(self, memory_id: str, 
                               memory_type: MemoryType, 
                               limit: int = 10) -> List[MemoryAssociation]:
        """Find associations for a specific memory."""
        pass
    
    @abstractmethod
    async def create_association(self, association: MemoryAssociation) -> str:
        """Create a new association."""
        pass
    
    @abstractmethod
    async def discover_associations(self, memory_id: str, 
                                   memory_type: MemoryType) -> List[MemoryAssociation]:
        """Discover potential new associations for a memory."""
        pass


class MemoryAssociationEngine(AssociationEngine):
    """Advanced association engine for discovering and managing memory relationships."""
    
    def __init__(self, storage: StorageManager, config: MemoryConfig):
        self.storage = storage
        self.config = config
        self._association_rules = []
        self._pattern_cache = {}
        self._validation_cache = {}
        
        # Initialize with default association rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default association rules based on memory patterns."""
        # Rule 1: Same project ID associations
        async def same_project_condition(source, target):
            source_proj_id = getattr(source, 'project_id', None)
            target_proj_id = getattr(target, 'project_id', None)
            return source_proj_id and target_proj_id and source_proj_id == target_proj_id
        
        async def same_project_strength(source, target):
            # Strong association if same project
            return 0.8
        
        same_project_rule = AssociationRule(
            source_type=None,  # Applies to all types
            target_type=None,  # Applies to all types
            condition_func=same_project_condition,
            strength_func=same_project_strength,
            description="Memories from the same project"
        )
        self._association_rules.append(same_project_rule)
        
        # Rule 2: Conversations with configuration insights on same topic
        async def conv_config_insight_condition(conv, insight):
            if not isinstance(conv, ConversationMemory) or not isinstance(insight, ConfigurationInsight):
                return False
            
            # Check if conversation topic matches insight keywords
            conv_topic_lower = conv.topic.lower() if conv.topic else ""
            title_lower = insight.title.lower() if insight.title else ""
            desc_lower = insight.description.lower() if insight.description else ""
            
            # Check if any of the insight's contexts match the conversation
            ctx_matches = any(ctx.lower() in conv_topic_lower for ctx in insight.applicable_contexts)
            title_match = title_lower in conv_topic_lower or conv_topic_lower in title_lower
            desc_match = desc_lower in conv_topic_lower or conv_topic_lower in desc_lower
            
            return ctx_matches or title_match or desc_match
        
        async def conv_config_insight_strength(conv, insight):
            # Moderate to strong depending on match quality
            strength = 0.5
            if hasattr(insight, 'confidence_score'):
                strength = (strength + insight.confidence_score) / 2
            return min(strength, 0.9)
        
        conv_config_rule = AssociationRule(
            source_type=MemoryType.CONVERSATION,
            target_type=MemoryType.CONFIGURATION_INSIGHT,
            condition_func=conv_config_insight_condition,
            strength_func=conv_config_insight_strength,
            description="Conversations related to configuration insights"
        )
        self._association_rules.append(conv_config_rule)
        
        # Rule 3: Agent knowledge related to project context
        async def knowledge_context_condition(knowledge, context):
            if not isinstance(knowledge, AgentKnowledge) or not isinstance(context, ProjectContext):
                return False
            
            # Check if knowledge domain matches project tech stack
            domain_lower = knowledge.domain.lower() if knowledge.domain else ""
            tech_stack_matches = any(domain_lower in tech.lower() for tech in context.tech_stack)
            arch_decision_matches = any(domain_lower in decision.lower() for decision in context.architectural_decisions)
            
            return tech_stack_matches or arch_decision_matches
        
        async def knowledge_context_strength(knowledge, context):
            return 0.6  # Moderate strength
        
        knowledge_context_rule = AssociationRule(
            source_type=MemoryType.AGENT_KNOWLEDGE,
            target_type=MemoryType.PROJECT_CONTEXT,
            condition_func=knowledge_context_condition,
            strength_func=knowledge_context_strength,
            description="Agent knowledge relevant to project context"
        )
        self._association_rules.append(knowledge_context_rule)
        
        # Rule 4: Configuration insights related to project context
        async def config_context_condition(insight, context):
            if not isinstance(insight, ConfigurationInsight) or not isinstance(context, ProjectContext):
                return False
            
            # Check if insight contexts match project tech stack or architecture
            insight_contexts_lower = [ctx.lower() for ctx in insight.applicable_contexts]
            tech_stack_lower = [tech.lower() for tech in context.tech_stack]
            arch_decisions_lower = [decision.lower() for decision in context.architectural_decisions]
            
            # Check for matches
            for ctx in insight_contexts_lower:
                for tech in tech_stack_lower:
                    if tech in ctx or ctx in tech:
                        return True
                for decision in arch_decisions_lower:
                    if decision in ctx or ctx in decision:
                        return True
            
            return False
        
        async def config_context_strength(insight, context):
            # Strength based on confidence score
            base_strength = 0.5
            if hasattr(insight, 'confidence_score'):
                return (base_strength + insight.confidence_score) / 2
            return base_strength
        
        config_context_rule = AssociationRule(
            source_type=MemoryType.CONFIGURATION_INSIGHT,
            target_type=MemoryType.PROJECT_CONTEXT,
            condition_func=config_context_condition,
            strength_func=config_context_strength,
            description="Configuration insights relevant to project context"
        )
        self._association_rules.append(config_context_rule)
        
        # Rule 5: Conversations about similar topics
        async def similar_topic_condition(conv1, conv2):
            if not isinstance(conv1, ConversationMemory) or not isinstance(conv2, ConversationMemory):
                return False
            
            if conv1.conversation_id == conv2.conversation_id:  # Don't associate with itself
                return False
            
            # Compare topics
            topic1 = conv1.topic.lower() if conv1.topic else ""
            topic2 = conv2.topic.lower() if conv2.topic else ""
            
            if not topic1 or not topic2:
                return False
            
            # Simple similarity check - in a real implementation, you'd want more sophisticated NLP
            # For now, just check if topics share common words
            words1 = set(topic1.split())
            words2 = set(topic2.split())
            common_words = words1.intersection(words2)
            
            return len(common_words) > 0
        
        async def similar_topic_strength(conv1, conv2):
            topic1 = conv1.topic.lower() if conv1.topic else ""
            topic2 = conv2.topic.lower() if conv2.topic else ""
            
            words1 = set(topic1.split())
            words2 = set(topic2.split())
            common_words = words1.intersection(words2)
            all_words = words1.union(words2)
            
            if len(all_words) == 0:
                return 0.0
            
            # Similarity score based on Jaccard index
            similarity = len(common_words) / len(all_words)
            return min(similarity, 0.7)  # Cap at 0.7 for topic similarity
        
        similar_topic_rule = AssociationRule(
            source_type=MemoryType.CONVERSATION,
            target_type=MemoryType.CONVERSATION,
            condition_func=similar_topic_condition,
            strength_func=similar_topic_strength,
            description="Conversations with similar topics"
        )
        self._association_rules.append(similar_topic_rule)
    
    async def find_associations(self, memory_id: str, 
                               memory_type: MemoryType, 
                               limit: int = 10) -> List[MemoryAssociation]:
        """Find associations for a specific memory."""
        # First, try to find associations in metadata store
        # For now, we'll search for associations where this memory is either source or target
        # In a real implementation, you'd want an efficient index for this
        associations = []
        
        # This is a simplified implementation - in a real system, you'd want:
        # 1. An efficient index to find associations by memory ID
        # 2. Proper filtering and sorting
        
        # For now, let's just get associations where source or target matches
        # This would be inefficient in a real system with many associations
        all_associations = await self._get_all_associations()
        
        for assoc in all_associations:
            if assoc.involves_memory(memory_id):
                associations.append(assoc)
        
        # Sort by strength (descending) and return limited results
        associations.sort(key=lambda x: x.strength, reverse=True)
        return associations[:limit]
    
    async def _get_all_associations(self) -> List[MemoryAssociation]:
        """Get all associations (for demo purposes - not efficient for large datasets)."""
        # This is a placeholder implementation
        # In a real system, you'd query the database efficiently
        try:
            # Fetch all association records from metadata store
            # Note: This assumes associations are stored in the metadata store
            # In a real implementation, you might have them in vector store too
            # for similarity search
            results = await self.storage.metadata_store.list_memory_type(MemoryType.ASSOCIATION)
            
            associations = []
            for record in results:
                assoc = MemoryAssociation(**record["data"])
                associations.append(assoc)
            
            return associations
        except Exception as e:
            logger.warning(f"Could not retrieve associations: {e}")
            return []
    
    async def create_association(self, association: MemoryAssociation) -> str:
        """Create a new association."""
        # Validate the association
        if association.source_memory_id == association.target_memory_id:
            raise ValueError("Source and target memory IDs cannot be the same")
        
        # Calculate relevance score if not provided
        if association.relevance_score is None:
            association.calculate_relevance_score()
        
        # Store in metadata store
        assoc_id = await self.storage.metadata_store.add(
            memory_id=association.association_id,
            memory_type=MemoryType.ASSOCIATION,
            data=association.model_dump(),
            metadata={
                "source_id": association.source_memory_id,
                "target_id": association.target_memory_id,
                "type": association.association_type.value,
                "strength": association.strength,
                "created_at": association.created_at.isoformat()
            }
        )
        
        logger.info(f"Created association {assoc_id} between {association.source_memory_id} and {association.target_memory_id}")
        return assoc_id
    
    async def discover_associations(self, memory_id: str, 
                                   memory_type: MemoryType) -> List[MemoryAssociation]:
        """Discover potential new associations for a memory."""
        # First, get the source memory
        source_memory = await self._get_memory_by_id(memory_id, memory_type)
        if not source_memory:
            logger.warning(f"Source memory {memory_id} not found")
            return []
        
        # Get all other memories to compare against
        all_memories = await self._get_all_memories_of_types([mt for mt in MemoryType if mt != MemoryType.ASSOCIATION])
        
        new_associations = []
        
        # Apply each rule to see if it creates an association
        for rule in self._association_rules:
            # Check if rule applies to this memory type combination
            if (rule.source_type is not None and rule.source_type != memory_type and 
                rule.target_type is not None and rule.target_type != memory_type):
                continue
            
            for memory_data in all_memories:
                other_memory_id = memory_data.get("memory_id")
                other_memory_type = MemoryType(memory_data["metadata"]["type"])
                
                # Skip if it's the same memory
                if other_memory_id == memory_id:
                    continue
                
                # Skip if rule doesn't apply to this combination
                if (rule.source_type is not None and rule.source_type != memory_type and 
                    rule.target_type is not None and rule.target_type != other_memory_type):
                    continue
                
                # Determine which way to apply the rule based on types
                if (rule.source_type == memory_type and rule.target_type == other_memory_type) or \
                   (rule.source_type is None and rule.target_type == other_memory_type):
                    # Source is the current memory, target is the other memory
                    should_apply = await rule.applies(source_memory, memory_data["memory_object"])
                elif (rule.source_type == other_memory_type and rule.target_type == memory_type) or \
                     (rule.source_type == other_memory_type and rule.target_type is None):
                    # Source is the other memory, target is the current memory
                    should_apply = await rule.applies(memory_data["memory_object"], source_memory)
                else:
                    continue  # Rule doesn't apply to this memory pair
                
                if should_apply:
                    strength = await rule.calculate_strength(source_memory, memory_data["memory_object"])
                    
                    # Create association based on which is source and which is target
                    if (rule.source_type == memory_type and rule.target_type == other_memory_type) or \
                       (rule.source_type is None and rule.target_type == other_memory_type):
                        # Current memory is source
                        assoc = MemoryAssociation.create_association(
                            source_memory_id=memory_id,
                            source_memory_type=memory_type,
                            target_memory_id=other_memory_id,
                            target_memory_type=other_memory_type,
                            association_type=AssociationType.RELATED,
                            strength=strength,
                            reasoning=rule.description
                        )
                    else:
                        # Other memory is source
                        assoc = MemoryAssociation.create_association(
                            source_memory_id=other_memory_id,
                            source_memory_type=other_memory_type,
                            target_memory_id=memory_id,
                            target_memory_type=memory_type,
                            association_type=AssociationType.RELATED,
                            strength=strength,
                            reasoning=rule.description
                        )
                    
                    new_associations.append(assoc)
        
        # Sort by strength to return strongest associations first
        new_associations.sort(key=lambda x: x.strength, reverse=True)
        return new_associations
    
    async def _get_memory_by_id(self, memory_id: str, memory_type: MemoryType):
        """Get a memory object by its ID."""
        try:
            result = await self.storage.metadata_store.get(memory_id)
            if not result:
                return None
            
            # Reconstruct the appropriate memory object based on type
            memory_data = result["data"]
            if memory_type == MemoryType.CONVERSATION:
                return ConversationMemory(**memory_data)
            elif memory_type == MemoryType.CONFIGURATION_INSIGHT:
                return ConfigurationInsight(**memory_data)
            elif memory_type == MemoryType.AGENT_KNOWLEDGE:
                return AgentKnowledge(**memory_data)
            elif memory_type == MemoryType.PROJECT_CONTEXT:
                return ProjectContext(**memory_data)
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting memory {memory_id}: {e}")
            return None
    
    async def _get_all_memories_of_types(self, memory_types: List[MemoryType]) -> List[Dict]:
        """Get all memories of specified types."""
        memories = []
        for mtype in memory_types:
            try:
                # This would require a method to list all memories of a type
                # For now, we'll simulate this
                pass
            except Exception as e:
                logger.warning(f"Could not retrieve memories of type {mtype}: {e}")
        
        # This is a placeholder - in a real implementation, you'd query the database
        # and return all memories of the specified types
        return []
    
    async def find_related_memories(self, memory_id: str, memory_type: MemoryType, 
                                   limit: int = 10) -> List[Tuple[Any, float, MemoryAssociation]]:
        """Find related memories based on associations."""
        associations = await self.find_associations(memory_id, memory_type, limit)
        related_memories = []
        
        for assoc in associations:
            # Get the other memory in the association
            other_memory_info = assoc.get_opposite_memory(memory_id)
            if other_memory_info:
                other_id = other_memory_info["memory_id"]
                other_type = MemoryType(other_memory_info["memory_type"])
                
                # Fetch the other memory
                other_memory = await self._get_memory_by_id(other_id, other_type)
                if other_memory:
                    related_memories.append((other_memory, assoc.strength, assoc))
        
        # Sort by association strength
        related_memories.sort(key=lambda x: x[1], reverse=True)
        return related_memories[:limit]
    
    async def validate_association(self, assoc_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate an association is still relevant."""
        # Fetch the association
        assoc = await self._get_association_by_id(assoc_id)
        if not assoc:
            return False, {"reason": "Association not found"}
        
        # Check if either memory in the association still exists
        source_exists = await self._memory_exists(assoc.source_memory_id, assoc.source_memory_type)
        target_exists = await self._memory_exists(assoc.target_memory_id, assoc.target_memory_type)
        
        if not source_exists or not target_exists:
            return False, {"reason": "One or both associated memories no longer exist"}
        
        # Check if association is expired
        if assoc.is_expired():
            return False, {"reason": "Association has expired"}
        
        # Check if association strength has dropped below threshold
        if assoc.strength < 0.1:  # Arbitrary threshold
            return False, {"reason": "Association strength too low"}
        
        # All checks passed
        return True, {"reason": "Association is valid"}
    
    async def _get_association_by_id(self, assoc_id: str) -> Optional[MemoryAssociation]:
        """Get an association by its ID."""
        try:
            result = await self.storage.metadata_store.get(assoc_id)
            if not result:
                return None
            
            return MemoryAssociation(**result["data"])
        except Exception as e:
            logger.error(f"Error getting association {assoc_id}: {e}")
            return None
    
    async def _memory_exists(self, memory_id: str, memory_type: MemoryType) -> bool:
        """Check if a memory exists."""
        try:
            result = await self.storage.metadata_store.get(memory_id)
            return result is not None
        except Exception as e:
            logger.error(f"Error checking if memory {memory_id} exists: {e}")
            return False
    
    async def get_association_network(self, memory_id: str, memory_type: MemoryType, 
                                     depth: int = 1) -> Dict[str, Any]:
        """Get the association network around a memory."""
        network = {
            "center": {"id": memory_id, "type": memory_type.value},
            "nodes": [{"id": memory_id, "type": memory_type.value}],
            "edges": [],
            "depth": depth
        }
        
        # Add direct associations
        associations = await self.find_associations(memory_id, memory_type)
        
        for assoc in associations:
            # Add the other memory as a node
            other_info = assoc.get_opposite_memory(memory_id)
            if other_info:
                other_node = {
                    "id": other_info["memory_id"],
                    "type": other_info["memory_type"]
                }
                
                # Add node if not already present
                if not any(node["id"] == other_node["id"] for node in network["nodes"]):
                    network["nodes"].append(other_node)
                
                # Add edge
                edge = {
                    "source": memory_id,
                    "target": other_info["memory_id"],
                    "strength": assoc.strength,
                    "type": assoc.association_type.value
                }
                network["edges"].append(edge)
        
        return network


class AssociationPatternAnalyzer:
    """Analyzes association patterns to identify common relationships and improve discovery."""
    
    def __init__(self, association_engine: MemoryAssociationEngine):
        self.association_engine = association_engine
        self._pattern_cache = {}
    
    async def find_common_patterns(self) -> List[Dict[str, Any]]:
        """Find common association patterns in the memory system."""
        # Get all associations
        all_associations = await self.association_engine._get_all_associations()
        
        # Analyze patterns
        patterns = {
            "type_combinations": {},
            "common_reasons": {},
            "strength_distributions": {}
        }
        
        for assoc in all_associations:
            # Track type combinations
            type_combo = f"{assoc.source_memory_type.value}-{assoc.target_memory_type.value}"
            patterns["type_combinations"][type_combo] = patterns["type_combinations"].get(type_combo, 0) + 1
            
            # Track common reasons
            if assoc.reasoning:
                patterns["common_reasons"][assoc.reasoning] = patterns["common_reasons"].get(assoc.reasoning, 0) + 1
            
            # Track strength distributions
            strength_range = self._get_strength_range(assoc.strength)
            patterns["strength_distributions"][strength_range] = patterns["strength_distributions"].get(strength_range, 0) + 1
        
        # Convert to list of results
        results = []
        for pattern_type, data in patterns.items():
            for key, value in data.items():
                results.append({
                    "type": pattern_type,
                    "key": key,
                    "value": value
                })
        
        return results
    
    def _get_strength_range(self, strength: float) -> str:
        """Get strength range category."""
        if strength < 0.3:
            return "weak"
        elif strength < 0.6:
            return "moderate"
        elif strength < 0.8:
            return "strong"
        else:
            return "very_strong"
    
    async def suggest_new_rules(self) -> List[Dict[str, Any]]:
        """Suggest new association rules based on common patterns."""
        patterns = await self.find_common_patterns()
        
        # This is a simplified implementation
        # In a real system, you'd use ML or advanced analytics to identify patterns
        suggestions = []
        
        # Look for common type combinations that might benefit from specific rules
        type_combos = {p["key"]: p["value"] for p in patterns if p["type"] == "type_combinations"}
        
        for combo, count in type_combos.items():
            if count > 5:  # Arbitrary threshold for "common"
                source_type, target_type = combo.split("-")
                suggestions.append({
                    "rule_type": "type_based",
                    "source_type": source_type,
                    "target_type": target_type,
                    "frequency": count,
                    "suggestion": f"Consider creating a specific rule for {source_type} to {target_type} associations"
                })
        
        return suggestions

    async def get_association_insights(self) -> Dict[str, Any]:
        """Get insights about the association network."""
        all_associations = await self.association_engine._get_all_associations()
        
        if not all_associations:
            return {"message": "No associations found"}
        
        # Calculate statistics
        total_associations = len(all_associations)
        avg_strength = sum(assoc.strength for assoc in all_associations) / total_associations
        strongest_assoc = max(all_associations, key=lambda x: x.strength)
        weakest_assoc = min(all_associations, key=lambda x: x.strength)
        
        # Count by type
        type_counts = {}
        for assoc in all_associations:
            assoc_type = assoc.association_type.value
            type_counts[assoc_type] = type_counts.get(assoc_type, 0) + 1
        
        return {
            "total_associations": total_associations,
            "average_strength": avg_strength,
            "strongest_association": {
                "id": strongest_assoc.association_id,
                "strength": strongest_assoc.strength,
                "type": strongest_assoc.association_type.value,
                "reasoning": strongest_assoc.reasoning
            },
            "weakest_association": {
                "id": weakest_assoc.association_id,
                "strength": weakest_assoc.strength,
                "type": weakest_assoc.association_type.value,
                "reasoning": weakest_assoc.reasoning
            },
            "type_distribution": type_counts
        }