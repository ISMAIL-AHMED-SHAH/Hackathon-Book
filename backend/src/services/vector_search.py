"""
Vector search service for RAG Pipeline Query Endpoint.

This module implements semantic search over textbook chapter embeddings
using Qdrant vector database.

Services:
    - VectorSearchService: Performs semantic search with chapter filtering

Constitution Compliance:
    - Rule I: 100% type hints, formatted with Black
    - Rule IV: Comprehensive error handling and logging
    - FR-003: Vector search with similarity threshold
    - FR-015: 5-second timeout enforcement
"""

import asyncio
import httpx
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, SearchParams

from src.core.config import Settings
from src.core.exceptions import VectorDBError, vector_db_timeout
from src.core.metrics import record_vector_search_latency
from src.models.vector import VectorSearchResult
from src.services.logging import get_logger, log_vector_search

logger = get_logger(__name__)


class VectorSearchService:
    """
    Service for semantic search over textbook chapter embeddings.

    Performs vector similarity search using Qdrant with chapter-scoped
    filtering and configurable retrieval parameters per FR-003.

    Attributes:
        client: Qdrant client instance
        settings: Application settings (collection name, thresholds, timeouts)

    Example:
        >>> service = VectorSearchService(qdrant_client, settings)
        >>> results = await service.search(
        ...     query_vector=[0.1, 0.2, ...],  # 1536-dim embedding
        ...     chapter_id="ch-ros2-fundamentals",
        ...     top_k=5
        ... )
        >>> for result in results:
        ...     print(f"{result.chunk_id}: {result.similarity_score}")
    """

    def __init__(self, client: QdrantClient, settings: Settings) -> None:
        """
        Initialize vector search service.

        Args:
            client: Initialized Qdrant client
            settings: Application settings
        """
        self.client = client
        self.settings = settings

    async def search(
        self,
        query_vector: List[float],
        chapter_id: str,
        top_k: int = 5,
        score_threshold: float | None = None,
        query_id: str | None = None,
    ) -> List[VectorSearchResult]:
        """
        Perform semantic search over chapter embeddings.

        Searches Qdrant collection with chapter_id filter and similarity
        threshold per FR-003. Enforces 5-second timeout per FR-015.

        Args:
            query_vector: Query embedding vector (1536 dimensions)
            chapter_id: Chapter to search within (e.g., "ch-ros2-fundamentals")
            top_k: Number of results to retrieve (1-10, default 5)
            score_threshold: Minimum similarity score (default from settings: 0.3)
            query_id: Optional query ID for logging/metrics

        Returns:
            List of VectorSearchResult ordered by similarity (descending)

        Raises:
            VectorDBError: If Qdrant query fails or times out
            ValueError: If query_vector dimensions don't match (should be 1536)

        Example:
            >>> results = await service.search(
            ...     query_vector=embedding,
            ...     chapter_id="ch-ros2-fundamentals",
            ...     top_k=5,
            ...     score_threshold=0.3
            ... )
            >>> len(results)
            5
            >>> results[0].similarity_score >= 0.3
            True
        """
        # Use settings threshold if not specified
        if score_threshold is None:
            score_threshold = self.settings.vector_score_threshold

        # Validate query vector dimensions
        if len(query_vector) != self.settings.embedding_dimensions:
            raise ValueError(
                f"Query vector must have {self.settings.embedding_dimensions} dimensions, "
                f"got {len(query_vector)}"
            )

        # Log search start
        if query_id:
            logger.debug(
                f"Starting vector search for query_id={query_id}, chapter_id={chapter_id}",
                extra={
                    "query_id": query_id,
                    "chapter_id": chapter_id,
                    "top_k": top_k,
                    "score_threshold": score_threshold,
                },
            )

        # Build Qdrant filter for chapter_id
        # Uses GIN index on chapter_id field for fast filtering
        search_filter = Filter(
            must=[
                FieldCondition(
                    key="chapter_id",
                    match=MatchValue(value=chapter_id),
                )
            ]
        )

        # Configure search parameters
        search_params = SearchParams(
            hnsw_ef=128,  # Search depth (higher = more accurate, slower)
            exact=False,  # Use HNSW index (not exact search)
        )

        try:
            # Perform search with timeout enforcement (FR-015: 5 seconds)
            import time

            start_time = time.time()

            # Use HTTP API directly to avoid Windows TLS issues with gRPC
            # Build search request payload
            search_payload = {
                "query": query_vector,
                "filter": {"must": [{"key": "chapter_id", "match": {"value": chapter_id}}]},
                "limit": top_k,
                "score_threshold": score_threshold,
                "with_payload": True,
                "with_vector": False,
            }

            # Make HTTP POST request to Qdrant
            url = f"{self.settings.qdrant_url}/collections/{self.settings.vector_collection_name}/points/query"
            headers = {"api-key": self.settings.qdrant_api_key, "Content-Type": "application/json"}

            async with httpx.AsyncClient(timeout=self.settings.vector_db_timeout) as http_client:
                response = await http_client.post(url, json=search_payload, headers=headers)
                response.raise_for_status()
                result_data = response.json()

            qdrant_results = result_data.get("result", {}).get("points", [])

            # Calculate latency
            latency_seconds = time.time() - start_time
            latency_ms = int(latency_seconds * 1000)

            # Convert HTTP API results to VectorSearchResult models
            # HTTP API returns: {"result": {"points": [{"id": ..., "score": ..., "payload": ...}]}}
            results = []
            for point in qdrant_results:
                results.append(
                    VectorSearchResult(
                        chunk_id=point["payload"]["chunk_id"],
                        content=point["payload"]["content"],
                        similarity_score=point["score"],
                        chapter_id=point["payload"]["chapter_id"],
                        page_number=point["payload"]["page_number"],
                        section_title=point["payload"]["section_title"],
                    )
                )

            # Record metrics
            record_vector_search_latency(latency_seconds, chapter_id)

            # Log completion
            if query_id:
                log_vector_search(
                    logger=logger,
                    query_id=query_id,
                    chapter_id=chapter_id,
                    latency_ms=latency_ms,
                    results_count=len(results),
                )

            logger.info(
                f"Vector search completed: {len(results)} results in {latency_ms}ms",
                extra={
                    "query_id": query_id,
                    "chapter_id": chapter_id,
                    "results_count": len(results),
                    "latency_ms": latency_ms,
                },
            )

            return results

        except (asyncio.TimeoutError, httpx.TimeoutException):
            # FR-015: Handle timeout (5 seconds)
            logger.error(
                f"Vector search timeout after {self.settings.vector_db_timeout}s",
                extra={
                    "query_id": query_id,
                    "chapter_id": chapter_id,
                    "timeout_seconds": self.settings.vector_db_timeout,
                },
            )
            raise vector_db_timeout(timeout_seconds=self.settings.vector_db_timeout)

        except httpx.HTTPStatusError as e:
            # Handle HTTP errors from Qdrant API
            logger.error(
                f"Qdrant HTTP error: {e.response.status_code} - {e.response.text}",
                extra={
                    "query_id": query_id,
                    "chapter_id": chapter_id,
                    "status_code": e.response.status_code,
                },
                exc_info=True,
            )
            raise VectorDBError(
                message=f"Vector database HTTP error: {e.response.status_code}",
                details={
                    "chapter_id": chapter_id,
                    "top_k": top_k,
                    "status_code": e.response.status_code,
                },
            )

        except Exception as e:
            # Handle other errors
            logger.error(
                f"Vector search failed: {str(e)}",
                extra={
                    "query_id": query_id,
                    "chapter_id": chapter_id,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise VectorDBError(
                message=f"Vector database search failed: {str(e)}",
                details={
                    "chapter_id": chapter_id,
                    "top_k": top_k,
                },
            )


async def search_chunks(
    client: QdrantClient,
    settings: Settings,
    query_vector: List[float],
    chapter_id: str,
    top_k: int = 5,
    score_threshold: float | None = None,
    query_id: str | None = None,
) -> List[VectorSearchResult]:
    """
    Convenience function for vector search.

    Creates VectorSearchService instance and performs search.
    Use this for one-off searches without managing service lifecycle.

    Args:
        client: Qdrant client instance
        settings: Application settings
        query_vector: Query embedding vector (1536 dimensions)
        chapter_id: Chapter to search within
        top_k: Number of results (1-10, default 5)
        score_threshold: Minimum similarity score (default 0.3)
        query_id: Optional query ID for logging

    Returns:
        List of VectorSearchResult ordered by similarity

    Raises:
        VectorDBError: If search fails or times out

    Example:
        >>> from src.core.config import get_settings
        >>> results = await search_chunks(
        ...     client=qdrant_client,
        ...     settings=get_settings(),
        ...     query_vector=embedding,
        ...     chapter_id="ch-ros2-fundamentals",
        ...     top_k=5
        ... )
    """
    service = VectorSearchService(client, settings)
    return await service.search(
        query_vector=query_vector,
        chapter_id=chapter_id,
        top_k=top_k,
        score_threshold=score_threshold,
        query_id=query_id,
    )
