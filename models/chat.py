from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Message roles in chat"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata")


class ChatSession(BaseModel):
    """Chat session model"""
    session_id: str
    user_id: Optional[str] = Field(None, description="User identifier")
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    context: Optional[Dict[str, Any]] = Field(None, description="Session context")


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Existing session ID")
    user_id: Optional[str] = Field(None, description="User identifier")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="AI agent response")
    session_id: str = Field(..., description="Session identifier")
    recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="Job recommendations if applicable")
    confidence: float = Field(..., ge=0, le=1, description="Response confidence score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional response metadata")


class QueryIntent(BaseModel):
    """Query intent classification"""
    intent: str = Field(..., description="Detected intent")
    confidence: float = Field(..., ge=0, le=1, description="Intent confidence")
    entities: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted entities")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")

