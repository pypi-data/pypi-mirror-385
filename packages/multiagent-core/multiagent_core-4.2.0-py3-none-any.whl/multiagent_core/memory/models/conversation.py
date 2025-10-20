"""ConversationMemory model for storing and managing conversation data.

This module defines the ConversationMemory class which represents a stored
conversation with its metadata, context, and associated information.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

from pydantic import BaseModel, Field, validator


class MessageRole(str, Enum):
    """Enumeration of possible message roles in a conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"
    TOOL = "tool"


class AgentType(str, Enum):
    """Enumeration of supported agent types."""
    COPILOT = "copilot"
    CLAUDE = "claude"
    CODEX = "codex"
    QWEN = "qwen"
    GEMINI = "gemini"
    SYSTEM = "system"


@dataclass
class Message:
    """Represents a single message in a conversation."""
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary representation."""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Message:
        """Create Message from dictionary representation."""
        timestamp = None
        if data.get("timestamp"):
            timestamp = datetime.fromisoformat(data["timestamp"])
        
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=timestamp,
            metadata=data.get("metadata", {})
        )


class ConversationMemory(BaseModel):
    """
    Represents a stored conversation with metadata and context.
    
    This model handles the storage and retrieval of conversation data,
    including messages, context tags, agent information, and decision points.
    """
    
    # Core identification
    memory_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = Field(..., description="Project this conversation belongs to")
    
    # Agent and context information
    agent_type: AgentType = Field(..., description="Type of agent that handled this conversation")
    context_tags: List[str] = Field(default_factory=list, description="Tags for categorizing and searching")
    
    # Conversation content
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="List of conversation messages")
    summary: Optional[str] = Field(None, description="AI-generated summary of the conversation")
    
    # Decision tracking
    decisions: List[Dict[str, Any]] = Field(default_factory=list, description="Key decisions made during conversation")
    outcomes: List[Dict[str, Any]] = Field(default_factory=list, description="Results and outcomes from the conversation")
    
    # Metadata
    session_id: Optional[str] = Field(None, description="Session identifier for grouping related conversations")
    user_id: Optional[str] = Field(None, description="User identifier")
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Memory-specific fields
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance of this conversation")
    retrieval_count: int = Field(default=0, description="Number of times this memory has been retrieved")
    last_accessed: Optional[datetime] = Field(None, description="When this memory was last accessed")
    
    # Vector embeddings (stored as metadata, computed externally)
    embedding_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata about embeddings")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('context_tags')
    def validate_context_tags(cls, v):
        """Validate context tags are non-empty strings."""
        if v:
            for tag in v:
                if not isinstance(tag, str) or not tag.strip():
                    raise ValueError("Context tags must be non-empty strings")
        return v
    
    @validator('messages')
    def validate_messages(cls, v):
        """Validate messages have required structure."""
        if not v:
            return v
        
        for i, msg in enumerate(v):
            if not isinstance(msg, dict):
                raise ValueError(f"Message {i} must be a dictionary")
            
            if 'role' not in msg or 'content' not in msg:
                raise ValueError(f"Message {i} must have 'role' and 'content' fields")
            
            # Validate role is valid
            try:
                MessageRole(msg['role'])
            except ValueError:
                raise ValueError(f"Message {i} has invalid role: {msg['role']}")
        
        return v
    
    @validator('decisions')
    def validate_decisions(cls, v):
        """Validate decisions have required structure."""
        if not v:
            return v
        
        for i, decision in enumerate(v):
            if not isinstance(decision, dict):
                raise ValueError(f"Decision {i} must be a dictionary")
            
            required_fields = ['decision', 'reasoning', 'confidence']
            for field in required_fields:
                if field not in decision:
                    raise ValueError(f"Decision {i} missing required field: {field}")
        
        return v
    
    def add_message(self, role: Union[str, MessageRole], content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a new message to the conversation."""
        if isinstance(role, str):
            role = MessageRole(role)
        
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        self.messages.append(message.to_dict())
        self.updated_at = datetime.now(timezone.utc)
    
    def add_decision(self, decision: str, reasoning: str, confidence: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a decision point to the conversation."""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        decision_record = {
            "decision": decision,
            "reasoning": reasoning,
            "confidence": confidence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }
        
        self.decisions.append(decision_record)
        self.updated_at = datetime.now(timezone.utc)
    
    def add_outcome(self, outcome: str, success: bool, impact: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add an outcome record to the conversation."""
        outcome_record = {
            "outcome": outcome,
            "success": success,
            "impact": impact,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }
        
        self.outcomes.append(outcome_record)
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_accessed(self) -> None:
        """Mark this memory as accessed, updating access statistics."""
        self.retrieval_count += 1
        self.last_accessed = datetime.now(timezone.utc)
    
    def get_message_count(self) -> int:
        """Get the total number of messages in this conversation."""
        return len(self.messages)
    
    def get_content_length(self) -> int:
        """Get the total character count of all message content."""
        return sum(len(msg.get('content', '')) for msg in self.messages)
    
    def get_duration_minutes(self) -> Optional[float]:
        """Calculate conversation duration in minutes if timestamps are available."""
        if len(self.messages) < 2:
            return None
        
        timestamps = []
        for msg in self.messages:
            if 'timestamp' in msg and msg['timestamp']:
                try:
                    timestamps.append(datetime.fromisoformat(msg['timestamp']))
                except (ValueError, TypeError):
                    continue
        
        if len(timestamps) < 2:
            return None
        
        duration = max(timestamps) - min(timestamps)
        return duration.total_seconds() / 60.0
    
    def get_agent_messages(self) -> List[Dict[str, Any]]:
        """Get only messages from the agent (not user messages)."""
        return [msg for msg in self.messages if msg.get('role') == MessageRole.ASSISTANT.value]
    
    def get_user_messages(self) -> List[Dict[str, Any]]:
        """Get only messages from the user."""
        return [msg for msg in self.messages if msg.get('role') == MessageRole.USER.value]
    
    def has_tag(self, tag: str) -> bool:
        """Check if this conversation has a specific tag."""
        return tag.lower() in [t.lower() for t in self.context_tags]
    
    def add_tag(self, tag: str) -> None:
        """Add a context tag if it doesn't already exist."""
        if not self.has_tag(tag) and tag.strip():
            self.context_tags.append(tag.strip())
            self.updated_at = datetime.now(timezone.utc)
    
    def remove_tag(self, tag: str) -> bool:
        """Remove a context tag. Returns True if tag was found and removed."""
        original_length = len(self.context_tags)
        self.context_tags = [t for t in self.context_tags if t.lower() != tag.lower()]
        
        if len(self.context_tags) < original_length:
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def to_search_text(self) -> str:
        """Generate searchable text representation of the conversation."""
        parts = []
        
        # Add summary if available
        if self.summary:
            parts.append(self.summary)
        
        # Add message content
        for msg in self.messages:
            content = msg.get('content', '')
            if content:
                parts.append(content)
        
        # Add context tags
        if self.context_tags:
            parts.append(' '.join(self.context_tags))
        
        # Add decisions
        for decision in self.decisions:
            parts.append(decision.get('decision', ''))
            parts.append(decision.get('reasoning', ''))
        
        return ' '.join(parts)
    
    def to_minimal_dict(self) -> Dict[str, Any]:
        """Convert to minimal dictionary for API responses."""
        return {
            "memory_id": self.memory_id,
            "project_id": self.project_id,
            "agent_type": self.agent_type.value,
            "summary": self.summary,
            "context_tags": self.context_tags,
            "message_count": self.get_message_count(),
            "importance_score": self.importance_score,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_api_data(cls, data: Dict[str, Any]) -> ConversationMemory:
        """Create ConversationMemory from API request data."""
        # Handle content field which might contain messages
        messages = []
        if 'content' in data and isinstance(data['content'], dict):
            if 'messages' in data['content']:
                messages = data['content']['messages']
        elif 'messages' in data:
            messages = data['messages']
        
        # Extract other fields
        return cls(
            project_id=data['project_id'],
            agent_type=AgentType(data['agent_type']),
            messages=messages,
            context_tags=data.get('context_tags', []),
            summary=data.get('summary'),
            session_id=data.get('session_id'),
            user_id=data.get('user_id'),
            importance_score=data.get('importance_score', 0.5)
        )