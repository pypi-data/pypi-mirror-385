"""Agent Context Integration for Memory-Aware Responses

Provides agents with memory context to enhance their responses with
historical knowledge, previous decisions, and project understanding.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from .manager import MemoryManager
from .config import MemoryConfig
from .models.conversation import AgentType


class AgentContextEnricher:
    """Enriches agent context with relevant memory information.

    Automatically provides agents with:
    - Relevant past conversations
    - Configuration insights
    - Agent knowledge
    - Project context
    """

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        """Initialize the context enricher.

        Args:
            memory_manager: Optional MemoryManager instance. Creates new if None.
        """
        self.manager = memory_manager
        self._initialized = False

    async def _ensure_initialized(self):
        """Ensure memory manager is initialized."""
        if not self._initialized:
            if self.manager is None:
                config = MemoryConfig()
                self.manager = MemoryManager(config)
            if not self.manager._initialized:
                await self.manager.initialize()
            self._initialized = True

    async def enrich_context(
        self,
        agent_id: str,
        current_query: str,
        project_id: Optional[str] = None,
        max_conversations: int = 3,
        max_insights: int = 2
    ) -> Dict[str, Any]:
        """Enrich agent context with relevant memories.

        Args:
            agent_id: Agent requesting context (claude, copilot, qwen, etc)
            current_query: Current user query or task
            project_id: Current project context
            max_conversations: Maximum past conversations to include
            max_insights: Maximum config insights to include

        Returns:
            Dict with enriched context including:
                - relevant_conversations: Past relevant discussions
                - configuration_insights: Learned patterns
                - agent_expertise: Agent's known skills
                - project_context: Project understanding
                - context_summary: Text summary for agent prompt
        """
        await self._ensure_initialized()

        context = {
            "agent_id": agent_id,
            "project_id": project_id,
            "query": current_query,
            "timestamp": datetime.now().isoformat(),
            "relevant_conversations": [],
            "configuration_insights": [],
            "agent_expertise": [],
            "project_context": None,
            "context_summary": ""
        }

        try:
            # Search relevant past conversations (with error handling)
            try:
                conv_results = await self.manager.search_conversations(
                    query=current_query,
                    project_id=project_id,
                    limit=max_conversations
                )

                for conv, score in conv_results:
                    context["relevant_conversations"].append({
                        "topic": conv.topic,
                        "participants": [p.value for p in conv.participants],
                        "summary": conv.turns[-1].message[:200] if conv.turns else "",
                        "relevance": round(score, 2),
                        "date": conv.created_at.isoformat()
                    })
            except Exception as search_err:
                # Graceful degradation - log but continue
                context["warnings"] = context.get("warnings", [])
                context["warnings"].append(f"Conversation search unavailable: {str(search_err)}")

            # Search relevant configuration insights
            insight_results = await self.manager.search_configuration_insights(
                query=current_query,
                project_id=project_id,
                limit=max_insights
            )

            for insight, score in insight_results:
                context["configuration_insights"].append({
                    "title": insight.title,
                    "recommendation": insight.recommendation,
                    "category": insight.category.value,
                    "confidence": insight.confidence_score,
                    "relevance": round(score, 2)
                })

            # Get agent's known expertise
            knowledge_results = await self.manager.search_agent_knowledge(
                query=current_query,
                agent_id=agent_id,
                limit=3
            )

            for knowledge, score in knowledge_results:
                context["agent_expertise"].append({
                    "skill": knowledge.skill_name,
                    "domain": knowledge.domain,
                    "proficiency": knowledge.proficiency_level.value,
                    "relevance": round(score, 2)
                })

            # Get project context if available
            if project_id:
                project_ctx = await self.manager.get_project_context(project_id)
                if project_ctx:
                    context["project_context"] = {
                        "name": project_ctx.name,
                        "type": project_ctx.project_type.value,
                        "tech_stack": project_ctx.tech_stack[:10],
                        "key_decisions": project_ctx.architectural_decisions[:5]
                    }

            # Generate summary for agent prompt
            context["context_summary"] = self._generate_context_summary(context)

        except Exception as e:
            # Graceful degradation - return empty context on error
            context["error"] = str(e)
            context["context_summary"] = "Memory context unavailable."

        return context

    def _generate_context_summary(self, context: Dict[str, Any]) -> str:
        """Generate human-readable context summary for agent prompt.

        Args:
            context: Enriched context dictionary

        Returns:
            Formatted text summary
        """
        lines = ["## Memory Context"]

        # Project context
        if context.get("project_context"):
            proj = context["project_context"]
            lines.append(f"\n### Current Project: {proj['name']}")
            lines.append(f"- Type: {proj['type']}")
            if proj["tech_stack"]:
                lines.append(f"- Stack: {', '.join(proj['tech_stack'][:5])}")

        # Relevant conversations
        if context["relevant_conversations"]:
            lines.append("\n### Relevant Past Discussions:")
            for conv in context["relevant_conversations"][:3]:
                lines.append(f"- **{conv['topic']}** (relevance: {conv['relevance']})")
                lines.append(f"  Participants: {', '.join(conv['participants'])}")
                if conv["summary"]:
                    lines.append(f"  Summary: {conv['summary']}")

        # Configuration insights
        if context["configuration_insights"]:
            lines.append("\n### Learned Configuration Patterns:")
            for insight in context["configuration_insights"][:2]:
                lines.append(f"- **{insight['title']}** ({insight['category']})")
                lines.append(f"  Recommendation: {insight['recommendation']}")
                lines.append(f"  Confidence: {insight['confidence']:.0%}")

        # Agent expertise
        if context["agent_expertise"]:
            lines.append(f"\n### Your Known Expertise (relevant to this task):")
            for exp in context["agent_expertise"][:3]:
                lines.append(f"- {exp['skill']} ({exp['proficiency']}) in {exp['domain']}")

        if len(lines) == 1:
            lines.append("\nNo relevant memory context found for this task.")

        return "\n".join(lines)

    async def update_from_response(
        self,
        agent_id: str,
        project_id: str,
        query: str,
        response: str,
        learned_insights: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Update memory based on agent's response.

        Call this after an agent completes a task to store learnings.

        Args:
            agent_id: Agent that provided the response
            project_id: Project context
            query: Original query
            response: Agent's response
            learned_insights: Optional insights to store
        """
        await self._ensure_initialized()

        # Store the conversation turn
        from .models.conversation import ConversationMemory, ConversationTurn
        from uuid import uuid4

        conversation = ConversationMemory(
            conversation_id=str(uuid4()),
            project_id=project_id,
            topic=query[:100],  # Use first 100 chars of query as topic
            participants=[AgentType(agent_id.lower())],
            turns=[
                ConversationTurn(
                    speaker=AgentType(agent_id.lower()),
                    message=response[:1000],  # Store first 1000 chars
                    timestamp=datetime.now()
                )
            ],
            tags=["auto-captured"],
            created_at=datetime.now()
        )

        await self.manager.add_conversation(conversation)

        # Store any learned insights
        if learned_insights:
            from .models.config_insight import ConfigurationInsight, InsightCategory

            for insight_data in learned_insights:
                insight = ConfigurationInsight(
                    insight_id=str(uuid4()),
                    project_id=project_id,
                    title=insight_data.get("title", "Auto-learned insight"),
                    description=insight_data.get("description", ""),
                    category=InsightCategory(insight_data.get("category", "structure").lower()),
                    recommendation=insight_data.get("recommendation", ""),
                    confidence_score=insight_data.get("confidence", 0.5),
                    applicable_contexts=[],
                    learned_from_projects=[project_id],
                    created_at=datetime.now()
                )

                await self.manager.add_configuration_insight(insight)


# Global enricher instance for easy access
_global_enricher: Optional[AgentContextEnricher] = None


async def get_agent_context(
    agent_id: str,
    query: str,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """Convenience function to get enriched context for an agent.

    Args:
        agent_id: Agent requesting context
        query: Current query or task
        project_id: Optional project context

    Returns:
        Enriched context dictionary

    Example:
        >>> context = await get_agent_context("claude", "implement auth", "myproject")
        >>> print(context["context_summary"])
    """
    global _global_enricher

    if _global_enricher is None:
        _global_enricher = AgentContextEnricher()

    return await _global_enricher.enrich_context(agent_id, query, project_id)
