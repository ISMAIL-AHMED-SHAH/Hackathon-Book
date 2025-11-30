"""
Vector search models for RAG Pipeline Query Endpoint.

This module defines internal models for Qdrant vector search results.
These models wrap raw Qdrant responses for type-safe processing in the
RAG pipeline.

Models:
    - VectorSearchResult: Wrapper for Qdrant search results (FR-003)

Constitution Compliance:
    - Rule I: 100% type hints, formatted with Black
    - Rule III: Type-safe data structures for internal processing
"""

from typing import Any

from pydantic import BaseModel, Field


class VectorSearchResult(BaseModel):
    """
    Wrapper for Qdrant vector search results.

    Used internally for chunk retrieval (FR-003). Provides a type-safe
    wrapper around raw Qdrant results with factory method for easy
    conversion.

    Attributes:
        chunk_id: Chunk identifier from Qdrant payload
        content: Full chunk text content
        similarity_score: Cosine similarity score (0.0-1.0)
        page_number: Optional page number in original textbook
        section_title: Optional section/heading title
        metadata: Additional metadata from Qdrant payload

    Factory Methods:
        from_qdrant_result: Create instance from Qdrant ScoredPoint

    Example:
        >>> from qdrant_client.models import ScoredPoint
        >>> qdrant_result = ScoredPoint(
        ...     id="12345",
        ...     score=0.87,
        ...     payload={
        ...         "chunk_id": "ch-ros2-fundamentals_chunk_0042",
        ...         "content": "ROS 2 nodes are...",
        ...         "page_number": 42,
        ...         "section_title": "Understanding ROS 2 Nodes"
        ...     }
        ... )
        >>> result = VectorSearchResult.from_qdrant_result(qdrant_result)
        >>> result.chunk_id
        'ch-ros2-fundamentals_chunk_0042'
        >>> result.similarity_score
        0.87
    """

    chunk_id: str = Field(
        ...,
        description="Chunk identifier from Qdrant payload",
    )

    content: str = Field(
        ...,
        description="Full chunk text content",
    )

    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Cosine similarity score between query and chunk",
    )

    page_number: int | None = Field(
        None,
        ge=1,
        description="Optional page number in original textbook",
    )

    section_title: str | None = Field(
        None,
        max_length=200,
        description="Optional section/heading title where chunk appears",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata from Qdrant payload",
    )

    @classmethod
    def from_qdrant_result(cls, result: Any) -> "VectorSearchResult":
        """
        Factory method to create VectorSearchResult from Qdrant ScoredPoint.

        Args:
            result: Qdrant ScoredPoint object from search results

        Returns:
            VectorSearchResult instance with extracted data

        Example:
            >>> results = qdrant_client.search(...)
            >>> vector_results = [
            ...     VectorSearchResult.from_qdrant_result(r)
            ...     for r in results
            ... ]

        Note:
            Expects result.payload to contain:
            - chunk_id (required)
            - content (required)
            - page_number (optional)
            - section_title (optional)
        """
        payload = result.payload or {}

        return cls(
            chunk_id=payload.get("chunk_id", ""),
            content=payload.get("content", ""),
            similarity_score=result.score,
            page_number=payload.get("page_number"),
            section_title=payload.get("section_title"),
            metadata=payload,
        )
