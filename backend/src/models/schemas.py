"""
Pydantic schemas for RAG Pipeline Query Endpoint.

This module defines request/response models with 100% type hints per Constitution Rule I.
All models include comprehensive validation per Constitution Rule III.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class QueryRequest(BaseModel):
    """
    Request schema for RAG pipeline query endpoint.

    Validates user input for educational content queries with chapter-scoped
    context retrieval.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,  # Auto-strip whitespace
        validate_assignment=True,  # Re-validate on field updates
        frozen=False,  # Allow mutation for testing
    )

    query_text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User's question about course content",
        examples=[
            "What are the key principles of ROS 2?",
            "How do I create a ROS 2 node in Python?",
        ],
    )

    chapter_id: str = Field(
        ...,
        pattern=r"^ch-[a-z0-9-]{3,50}$",
        description="Chapter identifier to scope context retrieval (format: ch-{slug})",
        examples=["ch-ros2-fundamentals", "ch-isaac-sim-intro"],
    )

    user_id: str = Field(
        ...,
        description="Authenticated user's UUID (v4 format), extracted from JWT token",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of context chunks to retrieve from vector database",
    )

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="LLM sampling temperature (lower = more deterministic)",
    )

    session_id: Optional[str] = Field(
        None,
        pattern=r"^sess-[a-f0-9]{32}$",
        description="Optional session ID for conversation continuity",
        examples=["sess-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"],
    )

    @field_validator("query_text")
    @classmethod
    def validate_query_not_empty(cls, v: str) -> str:
        """Ensure query is not just whitespace (FR-002)."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("query_text cannot be empty or only whitespace")
        return cleaned

    @field_validator("user_id")
    @classmethod
    def validate_user_id_format(cls, v: str) -> str:
        """Validate UUIDv4 format (FR-002)."""
        try:
            UUID(v, version=4)
        except ValueError:
            raise ValueError("user_id must be a valid UUIDv4")
        return v.lower()  # Normalize to lowercase

    @field_validator("chapter_id")
    @classmethod
    def sanitize_chapter_id(cls, v: str) -> str:
        """Sanitize chapter_id to prevent injection (FR-013)."""
        import re

        # Remove any characters that could be used for injection
        if not re.match(r"^ch-[a-z0-9-]{3,50}$", v):
            raise ValueError("Invalid chapter_id format")
        return v.lower()


class Citation(BaseModel):
    """
    Metadata for a single source chunk used to generate the answer.

    Provides transparency into RAG pipeline retrieval process.
    Note: This is an alias for SourceChunk to match the task requirements.
    """

    chunk_id: str = Field(
        ...,
        description="Unique identifier for the source chunk",
        examples=["ch-ros2-fundamentals_chunk_0042"],
    )

    content: str = Field(
        ...,
        max_length=500,
        description="Excerpt from the source content (truncated for response size)",
    )

    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Cosine similarity score between query and chunk embedding",
    )

    page_number: Optional[int] = Field(
        None, ge=1, description="Page number in original textbook (if applicable)"
    )

    section_title: Optional[str] = Field(
        None, max_length=200, description="Section/heading title where chunk appears"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "chunk_id": "ch-ros2-fundamentals_chunk_0042",
                "content": "ROS 2 nodes are the fundamental building blocks of ROS applications...",
                "similarity_score": 0.87,
                "page_number": 42,
                "section_title": "Understanding ROS 2 Nodes",
            }
        }
    )


class GroundingStatus(str, Enum):
    """Enum for grounding status classification (FR-007)."""

    FULLY_GROUNDED = "fully_grounded"
    PARTIALLY_GROUNDED = "partially_grounded"
    SPECULATIVE = "speculative"


class QueryResponse(BaseModel):
    """
    Successful response schema for RAG query endpoint.

    Contains AI-generated answer with full provenance and confidence metrics.
    """

    answer: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="AI-generated answer grounded in retrieved source chunks",
    )

    sources: List[Citation] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Source chunks used to generate the answer (ordered by relevance)",
    )

    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Confidence score for answer quality based on source relevance. "
            "< 0.5 = low confidence (may be speculative), "
            ">= 0.7 = high confidence (well-grounded)"
        ),
    )

    grounding_status: GroundingStatus = Field(
        ..., description="Classification of answer grounding quality"
    )

    query_id: str = Field(
        ...,
        pattern=r"^qry-[a-f0-9]{32}$",
        description="Unique identifier for this query (for analytics/debugging)",
        examples=["qry-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"],
    )

    session_id: Optional[str] = Field(None, description="Session ID if provided in request")

    processing_time_ms: int = Field(
        ..., ge=0, description="Server-side processing time in milliseconds"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Response timestamp (UTC)"
    )

    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata (model version, chunk retrieval stats, etc.)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "answer": "ROS 2 nodes are the fundamental building blocks...",
                "sources": [
                    {
                        "chunk_id": "ch-ros2-fundamentals_chunk_0042",
                        "content": "ROS 2 nodes are independent...",
                        "similarity_score": 0.87,
                        "page_number": 42,
                        "section_title": "Understanding ROS 2 Nodes",
                    }
                ],
                "confidence_score": 0.87,
                "grounding_status": "fully_grounded",
                "query_id": "qry-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p",
                "session_id": None,
                "processing_time_ms": 1847,
                "created_at": "2025-11-28T15:30:45.123Z",
                "metadata": {
                    "model_version": "gpt-4-turbo-preview",
                    "chunks_retrieved": 5,
                    "llm_refusal": False,
                },
            }
        }
    )
