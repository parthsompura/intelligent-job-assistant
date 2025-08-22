"""
Data models for the Intelligent Job Assistant System
"""

from .job import (
    Job,
    JobPlatform,
    JobSearchQuery,
    JobRecommendation,
    ResumeAnalysis
)

from .chat import (
    ChatMessage,
    ChatSession,
    ChatRequest,
    ChatResponse,
    QueryIntent,
    MessageRole
)

__all__ = [
    # Job models
    "Job",
    "JobPlatform", 
    "JobSearchQuery",
    "JobRecommendation",
    "ResumeAnalysis",
    
    # Chat models
    "ChatMessage",
    "ChatSession",
    "ChatRequest", 
    "ChatResponse",
    "QueryIntent",
    "MessageRole"
]
