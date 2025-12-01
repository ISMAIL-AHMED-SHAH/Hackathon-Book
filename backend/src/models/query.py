"""
Query request and response models for RAG Pipeline Query Endpoint.

This module defines the Pydantic models for the POST /api/v1/query endpoint,
including request validation, response schemas, and grounding status classification.

Models:
    - QueryRequest: Validates incoming query requests (FR-002)
    - SourceChunk: Metadata for source chunks used in RAG (FR-005)
    - QueryResponse: Complete response with answer and provenance (FR-005)
    - GroundingStatus: Enum for answer quality classification (FR-007)

Constitution Compliance:
    - Rule I: 100% type hints, formatted with Black
    - Rule II: Comprehensive validators for business logic
    - Rule III: Standardized error messages via validators
"""

import re
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# =============================================================================
# Request Models
# =============================================================================


class QueryRequest(BaseModel):
    """
    Request schema for RAG pipeline query endpoint.

    Validates user input for educational content queries with chapter-scoped
    context retrieval per FR-002 (Input Validation).

    Attributes:
        query_text: User's question (1-1000 chars, whitespace stripped)
        chapter_id: Chapter identifier (format: ch-{slug})
        user_id: Authenticated user's UUID (v4 format)
        top_k: Number of context chunks to retrieve (1-10, default 5)
        temperature: LLM sampling temperature (0.0-1.0, default 0.7)
        session_id: Optional session ID for conversation continuity

    Validators:
        - query_text: Strips whitespace, rejects empty strings
        - user_id: Validates UUIDv4 format, normalizes to lowercase
        - chapter_id: Validates pattern, sanitizes for injection prevention

    Example:
        >>> request = QueryRequest(
        ...     query_text="What are ROS 2 nodes?",
        ...     chapter_id="ch-ros2-fundamentals",
        ...     user_id="550e8400-e29b-41d4-a716-446655440000"
        ... )
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

    chapter_id: Optional[str] = Field(
        default=None,
        pattern=r"^ch-[a-z0-9-]{3,50}$",
        description="Chapter identifier to scope context retrieval (format: ch-{slug}), optional for global search",
        examples=["ch-ros2-fundamentals", "ch-isaac-sim-intro", None],
    )

    user_id: str = Field(
        default="guest-user",
        description="User identifier (UUID v4 for authenticated users, or 'guest-user' for anonymous)",
        examples=["550e8400-e29b-41d4-a716-446655440000", "guest-user"],
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
        """
        Ensure query is not just whitespace (FR-002).

        Args:
            v: Query text after whitespace stripping

        Returns:
            Cleaned query text

        Raises:
            ValueError: If query is empty after stripping whitespace
        """
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("query_text cannot be empty or only whitespace")
        return cleaned

    @field_validator("user_id")
    @classmethod
    def validate_user_id_format(cls, v: str) -> str:
        """
        Validate user ID format (FR-002).

        Accepts either:
        - UUIDv4 format for authenticated users
        - "guest-user" literal for anonymous users

        Args:
            v: User ID string

        Returns:
            Normalized user ID (lowercase)

        Raises:
            ValueError: If user_id is neither a valid UUIDv4 nor "guest-user"
        """
        # Allow guest-user for anonymous access
        if v.lower() == "guest-user":
            return "guest-user"

        # Otherwise, validate as UUIDv4
        try:
            UUID(v, version=4)
        except ValueError:
            raise ValueError("user_id must be a valid UUIDv4 or 'guest-user'")
        return v.lower()  # Normalize to lowercase

    @field_validator("chapter_id")
    @classmethod
    def sanitize_chapter_id(cls, v: Optional[str]) -> Optional[str]:
        """
        Sanitize chapter_id to prevent injection (FR-013).

        Args:
            v: Chapter ID string or None for global search

        Returns:
            Sanitized chapter ID (lowercase) or None

        Raises:
            ValueError: If chapter_id doesn't match required pattern
        """
        # Allow None for global search (no chapter filter)
        if v is None:
            return None

        # Validate pattern to prevent injection
        if not re.match(r"^ch-[a-z0-9-]{3,50}$", v):
            raise ValueError("Invalid chapter_id format. Must match pattern: ch-[a-z0-9-]{3,50}")
        return v.lower()


# =============================================================================
# Response Models
# =============================================================================


class GroundingStatus(str, Enum):
    """
    Enum for grounding status classification (FR-007).

    Classifies answer quality based on source relevance:
        - FULLY_GROUNDED: High confidence, well-sourced (similarity >= 0.7)
        - PARTIALLY_GROUNDED: Medium confidence, partial sources (0.5 <= similarity < 0.7)
        - SPECULATIVE: Low confidence, weak sources (0.3 <= similarity < 0.5)

    Used for:
        - QueryResponse.grounding_status field
        - Metrics tracking (grounding quality rate)
        - User transparency about answer reliability
    """

    FULLY_GROUNDED = "fully_grounded"
    PARTIALLY_GROUNDED = "partially_grounded"
    SPECULATIVE = "speculative"


class SourceChunk(BaseModel):
    """
    Metadata for a single source chunk used to generate the answer.

    Provides transparency into RAG pipeline retrieval process per FR-005.
    Includes content excerpt, similarity score, and optional metadata for
    deeper research and citation.

    Attributes:
        chunk_id: Unique identifier for the source chunk
        content: Excerpt from source (max 500 chars for response size)
        similarity_score: Cosine similarity between query and chunk (0.0-1.0)
        page_number: Optional page number in original textbook
        section_title: Optional section/heading title where chunk appears

    Example:
        >>> source = SourceChunk(
        ...     chunk_id="ch-ros2-fundamentals_chunk_0042",
        ...     content="ROS 2 nodes are the fundamental building blocks...",
        ...     similarity_score=0.87,
        ...     page_number=42,
        ...     section_title="Understanding ROS 2 Nodes"
        ... )
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
        None,
        ge=1,
        description="Page number in original textbook (if applicable)",
    )

    section_title: Optional[str] = Field(
        None,
        max_length=200,
        description="Section/heading title where chunk appears",
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


class QueryResponse(BaseModel):
    """
    Successful response schema for RAG query endpoint.

    Contains AI-generated answer with full provenance and confidence metrics
    per FR-005 (Response Structure).

    Attributes:
        answer: AI-generated answer grounded in retrieved source chunks
        sources: Source chunks used (ordered by relevance, 1-10 chunks)
        confidence_score: Confidence score for answer quality (0.0-1.0)
        grounding_status: Classification of answer grounding quality
        query_id: Unique identifier for this query (for analytics/debugging)
        session_id: Session ID if provided in request
        processing_time_ms: Server-side processing time in milliseconds
        created_at: Response timestamp (UTC)
        metadata: Additional metadata (model version, chunk stats, etc.)

    Example:
        >>> response = QueryResponse(
        ...     answer="ROS 2 nodes are the fundamental building blocks...",
        ...     sources=[source1, source2],
        ...     confidence_score=0.87,
        ...     grounding_status=GroundingStatus.FULLY_GROUNDED,
        ...     query_id="qry-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p",
        ...     processing_time_ms=1847
        ... )
    """

    answer: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="AI-generated answer grounded in retrieved source chunks",
    )

    sources: list[SourceChunk] = Field(
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
        ...,
        description="Classification of answer grounding quality",
    )

    query_id: str = Field(
        ...,
        pattern=r"^qry-[a-f0-9]{32}$",
        description="Unique identifier for this query (for analytics/debugging)",
        examples=["qry-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"],
    )

    session_id: Optional[str] = Field(
        None,
        description="Session ID if provided in request",
    )

    processing_time_ms: int = Field(
        ...,
        ge=0,
        description="Server-side processing time in milliseconds",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp (UTC)",
    )

    metadata: Optional[dict[str, Any]] = Field(
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
