"""Memory System for Multiagent Framework."""

from __future__ import annotations

from .config import MemoryConfig
from .manager import MemoryManager
from .agent_context import AgentContextEnricher, get_agent_context
from .errors import (
    MemoryError,
    MemoryInitializationError,
    MemoryStorageError,
    MemorySearchError,
    MemoryDegradedModeError,
    safe_memory_operation
)

# Initialize model classes and enums to None for graceful degradation
ConversationMemory = None
AgentType = None
MessageRole = None
Message = None

ConfigurationInsight = None
InsightType = None
InsightCategory = None
ConfidenceLevel = None

AgentKnowledge = None
KnowledgeType = None
KnowledgeCategory = None
ProficiencyLevel = None

ProjectContext = None
ProjectType = None
TeamSize = None

MemoryAssociation = None
AssociationType = None
MemoryType = None

_IMPORT_ERROR = None

try:
    from .models import conversation as _conversation
    ConversationMemory = _conversation.ConversationMemory
    AgentType = _conversation.AgentType
    MessageRole = _conversation.MessageRole
    Message = _conversation.Message

    from .models import config_insight as _config_insight
    ConfigurationInsight = _config_insight.ConfigurationInsight
    InsightType = _config_insight.InsightType
    InsightCategory = _config_insight.InsightCategory
    ConfidenceLevel = _config_insight.ConfidenceLevel

    from .models import agent_knowledge as _agent_knowledge
    AgentKnowledge = _agent_knowledge.AgentKnowledge
    KnowledgeType = _agent_knowledge.KnowledgeType
    KnowledgeCategory = _agent_knowledge.KnowledgeCategory
    ProficiencyLevel = _agent_knowledge.ProficiencyLevel

    from .models import project_context as _project_context
    ProjectContext = _project_context.ProjectContext
    ProjectType = _project_context.ProjectType
    TeamSize = _project_context.TeamSize

    from .models import association as _association
    MemoryAssociation = _association.MemoryAssociation
    AssociationType = _association.AssociationType
    MemoryType = _association.MemoryType
except Exception as exc:  # pragma: no cover
    _IMPORT_ERROR = exc

__all__ = [
    'MemoryManager',
    'MemoryConfig',
    'ConversationMemory',
    'ConfigurationInsight',
    'AgentKnowledge',
    'ProjectContext',
    'MemoryAssociation',
    'AgentType',
    'MessageRole',
    'Message',
    'InsightType',
    'InsightCategory',
    'ConfidenceLevel',
    'KnowledgeType',
    'KnowledgeCategory',
    'ProficiencyLevel',
    'ProjectType',
    'TeamSize',
    'AssociationType',
    'MemoryType',
    'AgentContextEnricher',
    'get_agent_context',
    'MemoryError',
    'MemoryInitializationError',
    'MemoryStorageError',
    'MemorySearchError',
    'MemoryDegradedModeError',
    'safe_memory_operation'
]

__version__ = '0.1.0'
