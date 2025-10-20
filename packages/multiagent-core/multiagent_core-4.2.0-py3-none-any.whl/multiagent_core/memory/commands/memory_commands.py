"""Memory System CLI Command Implementations

Interactive slash commands for memory operations.
"""

import asyncio
import json
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

from ..manager import MemoryManager
from ..config import MemoryConfig
from ..models.conversation import ConversationMemory, AgentType, ConversationTurn
from ..models.config_insight import ConfigurationInsight, InsightCategory
from ..models.agent_knowledge import AgentKnowledge, ProficiencyLevel


# Global memory manager instance
_memory_manager: Optional[MemoryManager] = None


async def get_memory_manager() -> MemoryManager:
    """Get or initialize the global memory manager."""
    global _memory_manager
    if _memory_manager is None:
        config = MemoryConfig()
        _memory_manager = MemoryManager(config)
        await _memory_manager.initialize()
    return _memory_manager


async def store_conversation(
    project_id: str,
    topic: str,
    participants: List[str],
    turns: List[dict],
    tags: Optional[List[str]] = None
) -> str:
    """Store a conversation in memory.

    Usage: /memory:store-conversation <project_id> <topic> <participants> <turns_json>

    Args:
        project_id: Project identifier
        topic: Conversation topic
        participants: List of participant agent names (e.g., ["claude", "copilot"])
        turns: List of conversation turn dictionaries
        tags: Optional tags for categorization

    Returns:
        Conversation ID

    Example:
        /memory:store-conversation myproject "auth implementation" ["claude","copilot"] '[{"speaker":"claude","message":"Let me design the schema","timestamp":"2024-01-01T10:00:00Z"}]'
    """
    manager = await get_memory_manager()

    # Convert string participants to AgentType
    agent_participants = [AgentType(p.lower()) for p in participants]

    # Convert turn dicts to ConversationTurn objects
    conversation_turns = [
        ConversationTurn(
            speaker=AgentType(turn["speaker"].lower()),
            message=turn["message"],
            timestamp=datetime.fromisoformat(turn.get("timestamp", datetime.now().isoformat()))
        )
        for turn in turns
    ]

    conversation = ConversationMemory(
        conversation_id=str(uuid4()),
        project_id=project_id,
        topic=topic,
        participants=agent_participants,
        turns=conversation_turns,
        tags=tags or [],
        created_at=datetime.now()
    )

    conversation_id = await manager.add_conversation(conversation)
    print(f"✅ Stored conversation {conversation_id}")
    print(f"   Project: {project_id}")
    print(f"   Topic: {topic}")
    print(f"   Turns: {len(conversation_turns)}")

    return conversation_id


async def search_memories(
    query: str,
    memory_type: str = "conversation",
    project_id: Optional[str] = None,
    limit: int = 5
) -> None:
    """Search memories using semantic similarity.

    Usage: /memory:search <query> [--type=conversation|config|knowledge|context] [--project=<id>] [--limit=N]

    Args:
        query: Search query text
        memory_type: Type of memory to search (conversation, config, knowledge, context)
        project_id: Optional project filter
        limit: Maximum results

    Example:
        /memory:search "authentication design" --type=conversation --project=myproject --limit=3
    """
    manager = await get_memory_manager()

    print(f"\n🔍 Searching {memory_type} memories for: \"{query}\"")
    if project_id:
        print(f"   Project filter: {project_id}")
    print(f"   Limit: {limit}\n")

    if memory_type == "conversation":
        results = await manager.search_conversations(query, project_id, limit)
        for conv, score in results:
            print(f"📝 Conversation: {conv.topic}")
            print(f"   ID: {conv.conversation_id}")
            print(f"   Project: {conv.project_id}")
            print(f"   Participants: {[p.value for p in conv.participants]}")
            print(f"   Relevance: {score:.2f}")
            print(f"   Turns: {len(conv.turns)}")
            if conv.turns:
                print(f"   Latest: {conv.turns[-1].message[:100]}...")
            print()

    elif memory_type == "config":
        results = await manager.search_configuration_insights(query, project_id, limit)
        for insight, score in results:
            print(f"💡 Config Insight: {insight.title}")
            print(f"   ID: {insight.insight_id}")
            print(f"   Category: {insight.category.value}")
            print(f"   Confidence: {insight.confidence_score:.2f}")
            print(f"   Relevance: {score:.2f}")
            print(f"   Recommendation: {insight.recommendation[:100]}...")
            print()

    elif memory_type == "knowledge":
        results = await manager.search_agent_knowledge(query, project_id, limit)
        for knowledge, score in results:
            print(f"🎓 Agent Knowledge: {knowledge.skill_name}")
            print(f"   ID: {knowledge.knowledge_id}")
            print(f"   Agent: {knowledge.agent_id}")
            print(f"   Domain: {knowledge.domain}")
            print(f"   Proficiency: {knowledge.proficiency_level.value}")
            print(f"   Relevance: {score:.2f}")
            print()

    elif memory_type == "context":
        results = await manager.search_project_contexts(query, limit)
        for context, score in results:
            print(f"📦 Project Context: {context.name}")
            print(f"   ID: {context.project_id}")
            print(f"   Type: {context.project_type.value}")
            print(f"   Tech Stack: {', '.join(context.tech_stack[:5])}")
            print(f"   Relevance: {score:.2f}")
            print()

    else:
        print(f"❌ Unknown memory type: {memory_type}")
        print("   Valid types: conversation, config, knowledge, context")


async def add_config_insight(
    project_id: str,
    title: str,
    description: str,
    category: str,
    recommendation: str,
    confidence: float = 0.8,
    contexts: Optional[List[str]] = None
) -> str:
    """Add a configuration insight learned from a pattern.

    Usage: /memory:add-config-insight <project_id> <title> <description> <category> <recommendation> [--confidence=0.8] [--contexts="ctx1,ctx2"]

    Args:
        project_id: Project identifier
        title: Short insight title
        description: Detailed description
        category: Category (security, performance, structure, dependencies, testing)
        recommendation: Actionable recommendation
        confidence: Confidence score 0-1
        contexts: Applicable contexts

    Example:
        /memory:add-config-insight myproject "Use .env for secrets" "API keys found in code" security "Move all keys to .env file" --confidence=0.9
    """
    manager = await get_memory_manager()

    insight = ConfigurationInsight(
        insight_id=str(uuid4()),
        project_id=project_id,
        title=title,
        description=description,
        category=InsightCategory(category.lower()),
        recommendation=recommendation,
        confidence_score=confidence,
        applicable_contexts=contexts or [],
        learned_from_projects=[project_id],
        created_at=datetime.now()
    )

    insight_id = await manager.add_configuration_insight(insight)
    print(f"✅ Stored configuration insight {insight_id}")
    print(f"   Title: {title}")
    print(f"   Category: {category}")
    print(f"   Confidence: {confidence}")

    return insight_id


async def add_agent_knowledge(
    agent_id: str,
    skill_name: str,
    domain: str,
    description: str,
    proficiency: str = "intermediate",
    examples: Optional[List[str]] = None
) -> str:
    """Add agent knowledge or skill to memory.

    Usage: /memory:add-agent-knowledge <agent_id> <skill_name> <domain> <description> [--proficiency=beginner|intermediate|expert] [--examples="ex1,ex2"]

    Args:
        agent_id: Agent identifier (claude, copilot, qwen, etc)
        skill_name: Name of the skill
        domain: Domain area
        description: Skill description
        proficiency: Proficiency level
        examples: Usage examples

    Example:
        /memory:add-agent-knowledge claude "API Design" "REST APIs" "Designs scalable REST endpoints" --proficiency=expert
    """
    manager = await get_memory_manager()

    knowledge = AgentKnowledge(
        knowledge_id=str(uuid4()),
        agent_id=agent_id,
        skill_name=skill_name,
        domain=domain,
        description=description,
        proficiency_level=ProficiencyLevel(proficiency.lower()),
        examples=examples or [],
        acquired_from_projects=[],
        created_at=datetime.now()
    )

    knowledge_id = await manager.add_agent_knowledge(knowledge)
    print(f"✅ Stored agent knowledge {knowledge_id}")
    print(f"   Agent: {agent_id}")
    print(f"   Skill: {skill_name}")
    print(f"   Proficiency: {proficiency}")

    return knowledge_id


async def cleanup_memories(
    older_than_days: int = 90,
    min_confidence: float = 0.3
) -> None:
    """Clean up old or low-confidence memories.

    Usage: /memory:cleanup [--days=90] [--min-confidence=0.3]

    Args:
        older_than_days: Remove memories older than this
        min_confidence: Remove memories below this confidence

    Example:
        /memory:cleanup --days=30 --min-confidence=0.5
    """
    manager = await get_memory_manager()

    print(f"🧹 Cleaning up memories...")
    print(f"   Older than: {older_than_days} days")
    print(f"   Below confidence: {min_confidence}")

    stats = await manager.cleanup_old_memories(older_than_days, min_confidence)

    print(f"\n✅ Cleanup complete")
    print(f"   Removed: {stats.get('removed', 0)}")
    print(f"   Kept: {stats.get('kept', 0)}")


# Command registry for CLI integration
MEMORY_COMMANDS = {
    "memory:store-conversation": store_conversation,
    "memory:search": search_memories,
    "memory:add-config-insight": add_config_insight,
    "memory:add-agent-knowledge": add_agent_knowledge,
    "memory:cleanup": cleanup_memories
}
