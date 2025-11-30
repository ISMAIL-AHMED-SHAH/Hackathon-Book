"""
Query service for RAG Pipeline Query Endpoint.

This module implements the core query orchestration logic, including
confidence scoring, grounding status classification, and response assembly.

Services:
    - QueryService: Orchestrates vector search + LLM generation
    - calculate_confidence_score: Computes mean similarity score
    - classify_grounding_status: Classifies answer quality

Constitution Compliance:
    - Rule I: 100% type hints, formatted with Black
    - Rule IV: Comprehensive logging for debugging
    - FR-006: Confidence score calculation (mean similarity)
    - FR-007: Grounding status classification
"""

from typing import List

from src.models.query import GroundingStatus, SourceChunk
from src.models.vector import VectorSearchResult
from src.services.logging import get_logger

logger = get_logger(__name__)


def calculate_confidence_score(chunks: List[VectorSearchResult]) -> float:
    """
    Calculate confidence score from retrieved chunks.

    Computes mean similarity score of all retrieved chunks per FR-006.
    Higher scores indicate better grounding in source material.

    Args:
        chunks: Retrieved vector search results

    Returns:
        Mean similarity score (0.0-1.0)

    Raises:
        ValueError: If chunks list is empty

    Example:
        >>> chunk1 = VectorSearchResult(
        ...     chunk_id="ch1",
        ...     content="...",
        ...     similarity_score=0.8,
        ...     metadata={}
        ... )
        >>> chunk2 = VectorSearchResult(
        ...     chunk_id="ch2",
        ...     content="...",
        ...     similarity_score=0.6,
        ...     metadata={}
        ... )
        >>> calculate_confidence_score([chunk1, chunk2])
        0.7
    """
    if not chunks:
        raise ValueError("Cannot calculate confidence score from empty chunks list")

    # Calculate mean similarity (FR-006)
    total_similarity = sum(chunk.similarity_score for chunk in chunks)
    mean_similarity = total_similarity / len(chunks)

    return round(mean_similarity, 3)  # Round to 3 decimal places


def classify_grounding_status(confidence_score: float) -> GroundingStatus:
    """
    Classify grounding status based on confidence score.

    Classification thresholds per FR-007:
        - >= 0.7: FULLY_GROUNDED (high confidence, well-sourced)
        - >= 0.5: PARTIALLY_GROUNDED (medium confidence, partial sources)
        - >= 0.3: SPECULATIVE (low confidence, weak sources)
        - < 0.3: Error (should raise CONTEXT_NOT_FOUND or INSUFFICIENT_GROUNDING)

    Args:
        confidence_score: Mean similarity score (0.0-1.0)

    Returns:
        GroundingStatus enum value

    Raises:
        ValueError: If confidence_score < 0.3 (should be handled by caller)

    Example:
        >>> classify_grounding_status(0.85)
        <GroundingStatus.FULLY_GROUNDED: 'fully_grounded'>
        >>> classify_grounding_status(0.65)
        <GroundingStatus.PARTIALLY_GROUNDED: 'partially_grounded'>
        >>> classify_grounding_status(0.45)
        <GroundingStatus.SPECULATIVE: 'speculative'>
    """
    # FR-007: Grounding status thresholds
    if confidence_score >= 0.7:
        return GroundingStatus.FULLY_GROUNDED
    elif confidence_score >= 0.5:
        return GroundingStatus.PARTIALLY_GROUNDED
    elif confidence_score >= 0.3:
        return GroundingStatus.SPECULATIVE
    else:
        # < 0.3 should be handled by caller (raise CONTEXT_NOT_FOUND or INSUFFICIENT_GROUNDING)
        raise ValueError(
            f"Confidence score {confidence_score} is below minimum threshold 0.3. "
            "Caller should raise CONTEXT_NOT_FOUND or INSUFFICIENT_GROUNDING error."
        )


def convert_to_source_chunks(
    vector_results: List[VectorSearchResult],
    max_content_length: int = 500,
) -> List[SourceChunk]:
    """
    Convert VectorSearchResult to SourceChunk models.

    Transforms internal vector search results to public API response format.
    Truncates content to max_content_length for response size optimization.

    Args:
        vector_results: Vector search results from Qdrant
        max_content_length: Maximum content length (default 500 per data-model.md)

    Returns:
        List of SourceChunk models for API response

    Example:
        >>> vector_result = VectorSearchResult(
        ...     chunk_id="ch-ros2-fundamentals_chunk_0042",
        ...     content="ROS 2 nodes are the fundamental building blocks..." * 20,
        ...     similarity_score=0.87,
        ...     page_number=42,
        ...     section_title="Understanding ROS 2 Nodes",
        ...     metadata={}
        ... )
        >>> sources = convert_to_source_chunks([vector_result])
        >>> len(sources[0].content) <= 500
        True
    """
    source_chunks = []

    for result in vector_results:
        # Truncate content if needed
        content = result.content
        if len(content) > max_content_length:
            content = content[:max_content_length].rsplit(" ", 1)[0] + "..."

        source_chunk = SourceChunk(
            chunk_id=result.chunk_id,
            content=content,
            similarity_score=result.similarity_score,
            page_number=result.page_number,
            section_title=result.section_title,
        )
        source_chunks.append(source_chunk)

    return source_chunks


def sort_sources_by_similarity(sources: List[SourceChunk]) -> List[SourceChunk]:
    """
    Sort source chunks by similarity score (descending).

    Orders sources by relevance for better user experience per FR-019.

    Args:
        sources: List of SourceChunk models

    Returns:
        Sorted list (highest similarity first)

    Example:
        >>> source1 = SourceChunk(
        ...     chunk_id="ch1",
        ...     content="...",
        ...     similarity_score=0.6
        ... )
        >>> source2 = SourceChunk(
        ...     chunk_id="ch2",
        ...     content="...",
        ...     similarity_score=0.9
        ... )
        >>> sorted_sources = sort_sources_by_similarity([source1, source2])
        >>> sorted_sources[0].similarity_score
        0.9
    """
    return sorted(sources, key=lambda s: s.similarity_score, reverse=True)


class QueryService:
    """
    Service for orchestrating RAG query pipeline.

    Coordinates vector search, LLM generation, confidence scoring,
    and response assembly.

    Example:
        >>> service = QueryService()
        >>> # After vector search and LLM generation:
        >>> confidence = service.calculate_confidence(vector_results)
        >>> status = service.classify_status(confidence)
        >>> sources = service.prepare_sources(vector_results)
    """

    @staticmethod
    def calculate_confidence(chunks: List[VectorSearchResult]) -> float:
        """
        Calculate confidence score from chunks.

        Wrapper for calculate_confidence_score() function.

        Args:
            chunks: Retrieved vector search results

        Returns:
            Mean similarity score (0.0-1.0)
        """
        return calculate_confidence_score(chunks)

    @staticmethod
    def classify_status(confidence_score: float) -> GroundingStatus:
        """
        Classify grounding status from confidence score.

        Wrapper for classify_grounding_status() function.

        Args:
            confidence_score: Mean similarity score

        Returns:
            GroundingStatus enum value
        """
        return classify_grounding_status(confidence_score)

    @staticmethod
    def prepare_sources(
        vector_results: List[VectorSearchResult],
        sort_by_similarity: bool = True,
    ) -> List[SourceChunk]:
        """
        Prepare source chunks for API response.

        Converts vector results to SourceChunk models and optionally sorts
        by similarity (descending) per FR-019.

        Args:
            vector_results: Vector search results
            sort_by_similarity: Sort by similarity descending (default True)

        Returns:
            List of SourceChunk models ready for API response
        """
        sources = convert_to_source_chunks(vector_results)

        if sort_by_similarity:
            sources = sort_sources_by_similarity(sources)

        return sources

    @staticmethod
    def validate_context_found(chunks: List[VectorSearchResult]) -> bool:
        """
        Check if any chunks meet minimum similarity threshold.

        Per FR-008, should return False if all chunks < 0.3 similarity,
        indicating CONTEXT_NOT_FOUND error.

        Args:
            chunks: Retrieved vector search results

        Returns:
            True if at least one chunk >= 0.3 similarity, False otherwise

        Example:
            >>> chunk_low = VectorSearchResult(
            ...     chunk_id="ch1",
            ...     content="...",
            ...     similarity_score=0.2,
            ...     metadata={}
            ... )
            >>> chunk_ok = VectorSearchResult(
            ...     chunk_id="ch2",
            ...     content="...",
            ...     similarity_score=0.5,
            ...     metadata={}
            ... )
            >>> QueryService.validate_context_found([chunk_low])
            False
            >>> QueryService.validate_context_found([chunk_ok])
            True
        """
        return any(chunk.similarity_score >= 0.3 for chunk in chunks)

    @staticmethod
    def validate_grounding(
        confidence_score: float,
        llm_refused: bool,
    ) -> bool:
        """
        Check if answer has sufficient grounding.

        Per FR-009, should return False if confidence < 0.3 AND LLM did NOT
        explicitly refuse, indicating INSUFFICIENT_GROUNDING error.

        Args:
            confidence_score: Mean similarity score
            llm_refused: True if LLM explicitly refused to answer

        Returns:
            True if grounding is sufficient, False if insufficient

        Example:
            >>> # Low confidence but LLM refused = OK (LLM self-detected)
            >>> QueryService.validate_grounding(0.2, llm_refused=True)
            True
            >>> # Low confidence and LLM didn't refuse = NOT OK
            >>> QueryService.validate_grounding(0.2, llm_refused=False)
            False
            >>> # Good confidence = OK regardless
            >>> QueryService.validate_grounding(0.7, llm_refused=False)
            True
        """
        # If confidence >= 0.3, grounding is sufficient
        if confidence_score >= 0.3:
            return True

        # If confidence < 0.3 but LLM refused, that's OK (LLM self-detected insufficient context)
        if llm_refused:
            return True

        # If confidence < 0.3 and LLM didn't refuse, grounding is insufficient
        return False
