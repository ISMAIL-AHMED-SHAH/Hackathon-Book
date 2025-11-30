"""
Query endpoint for RAG Pipeline Query Endpoint.

This module implements POST /api/v1/query endpoint for student questions
with chapter-scoped RAG.

Endpoints:
    - POST /api/v1/query: Process student query and return AI-generated answer

Constitution Compliance:
    - Rule I: 100% type hints, formatted with Black
    - Rule III: Standardized error responses
    - Rule IV: Comprehensive logging and metrics
"""

import asyncio
import hashlib
import time
import uuid
from datetime import datetime

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status
from openai import AsyncOpenAI
from qdrant_client import QdrantClient
from redis import asyncio as aioredis

from src.api.dependencies import (
    get_openai_client,
    get_postgres_pool,
    get_qdrant_client,
    get_redis_client,
    get_settings_dependency,
)
from src.core.config import Settings
from src.core.exceptions import LLMServiceError, VectorDBError
from src.core.metrics import (
    record_citation_count,
    record_grounding_status,
    record_query_latency,
)
from src.models.query import GroundingStatus, QueryRequest, QueryResponse
from src.services.llm import LLMService
from src.services.logging import get_logger, log_query_completed, log_query_started
from src.services.query_service import QueryService
from src.services.vector_search import VectorSearchService
from src.utils.error_handler import ErrorCode, get_standard_error_response

logger = get_logger(__name__)

router = APIRouter()


def generate_query_id() -> str:
    """
    Generate unique query ID.

    Format: qry-{32 hex chars} per data-model.md

    Returns:
        Query ID string matching pattern ^qry-[a-f0-9]{32}$

    Example:
        >>> query_id = generate_query_id()
        >>> query_id.startswith("qry-")
        True
        >>> len(query_id)
        36
    """
    return f"qry-{uuid.uuid4().hex}"


async def log_query_to_audit_table(
    pool: asyncpg.Pool | None,
    query_id: str,
    user_id: str,
    chapter_id: str,
    response_time_ms: int,
    grounding_status: GroundingStatus,
    citation_count: int,
    error_code: str | None,
    http_status_code: int,
) -> None:
    """
    Log query to audit table for analytics.

    Per FR-016, logs all queries WITHOUT query_text (privacy).
    Uses user_id_hash (SHA-256) instead of raw user_id.

    Args:
        pool: Postgres connection pool (None if unavailable)
        query_id: Query UUID
        user_id: User identifier (will be hashed)
        chapter_id: Chapter identifier
        response_time_ms: Processing time in milliseconds
        grounding_status: Answer grounding quality
        citation_count: Number of source citations
        error_code: Error code if failed (None if success)
        http_status_code: HTTP response status code
    """
    # Skip if pool not available
    if pool is None:
        return

    # Hash user_id for privacy (FR-016)
    user_id_hash = hashlib.sha256(user_id.encode("utf-8")).hexdigest()

    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO query_audit_log (
                    query_id,
                    user_id_hash,
                    chapter_id,
                    response_time_ms,
                    grounding_status,
                    citation_count,
                    error_code,
                    http_status_code
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                query_id,
                user_id_hash,
                chapter_id,
                response_time_ms,
                grounding_status.value if grounding_status else None,
                citation_count,
                error_code,
                http_status_code,
            )
    except Exception as e:
        # Don't fail request if audit logging fails
        logger.error(
            f"Failed to log query to audit table: {e}",
            extra={"query_id": query_id, "error": str(e)},
        )


@router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def process_query(
    request: QueryRequest,
    qdrant_client: QdrantClient = Depends(get_qdrant_client),
    openai_client: AsyncOpenAI = Depends(get_openai_client),
    postgres_pool: asyncpg.Pool = Depends(get_postgres_pool),
    redis_client: aioredis.Redis = Depends(get_redis_client),  # type: ignore[type-arg]
    settings: Settings = Depends(get_settings_dependency),
) -> QueryResponse:
    """
    Process student query and return AI-generated answer.

    Orchestrates full RAG pipeline:
        1. Generate query embedding (OpenAI)
        2. Search vector database (Qdrant) with chapter filter
        3. Generate answer from context (OpenAI GPT-4 Turbo)
        4. Calculate confidence score and grounding status
        5. Return response with sources

    Args:
        request: Validated QueryRequest with query_text, chapter_id, user_id
        qdrant_client: Qdrant vector database client
        openai_client: OpenAI API client
        postgres_pool: Postgres connection pool
        redis_client: Redis client (for future rate limiting)
        settings: Application settings

    Returns:
        QueryResponse with answer, sources, confidence_score, grounding_status

    Raises:
        HTTPException 404: CONTEXT_NOT_FOUND (all chunks < 0.3 similarity)
        HTTPException 422: INSUFFICIENT_GROUNDING (confidence < 0.3, LLM didn't refuse)
        HTTPException 500: VectorDBError, LLMServiceError, or unexpected errors

    Example:
        >>> response = await process_query(QueryRequest(
        ...     query_text="What are ROS 2 nodes?",
        ...     chapter_id="ch-ros2-fundamentals",
        ...     user_id="550e8400-e29b-41d4-a716-446655440000"
        ... ))
        >>> response.grounding_status
        <GroundingStatus.FULLY_GROUNDED: 'fully_grounded'>
    """
    # Generate unique query ID
    query_id = generate_query_id()

    # Start timer for latency tracking
    start_time = time.time()

    # Log query start
    log_query_started(
        logger=logger,
        query_id=query_id,
        user_id=request.user_id,
        chapter_id=request.chapter_id,
    )

    try:
        # Step 1: Generate query embedding
        logger.debug(
            f"Generating query embedding for query_id={query_id}",
            extra={"query_id": query_id},
        )

        embedding_response = await openai_client.embeddings.create(
            model=settings.embedding_model,
            input=request.query_text,
        )
        query_vector = embedding_response.data[0].embedding

        # Step 2: Search vector database with chapter filter
        logger.debug(
            f"Searching vector database for query_id={query_id}",
            extra={"query_id": query_id, "chapter_id": request.chapter_id},
        )

        vector_service = VectorSearchService(qdrant_client, settings)
        vector_results = await vector_service.search(
            query_vector=query_vector,
            chapter_id=request.chapter_id,
            top_k=request.top_k,
            query_id=query_id,
        )

        # Check if any context found (FR-008)
        query_service = QueryService()
        if not query_service.validate_context_found(vector_results):
            # All chunks < 0.3 similarity = CONTEXT_NOT_FOUND
            error_response = get_standard_error_response(
                error_code=ErrorCode.CONTEXT_NOT_FOUND,
                details={
                    "chapter_id": request.chapter_id,
                    "query_id": query_id,
                },
            )

            # Log to audit table
            latency_ms = int((time.time() - start_time) * 1000)
            await log_query_to_audit_table(
                pool=postgres_pool,
                query_id=query_id,
                user_id=request.user_id,
                chapter_id=request.chapter_id,
                response_time_ms=latency_ms,
                grounding_status=None,  # type: ignore[arg-type]
                citation_count=0,
                error_code=ErrorCode.CONTEXT_NOT_FOUND.value,
                http_status_code=status.HTTP_404_NOT_FOUND,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response.model_dump(exclude_none=True),
            )

        # Step 3: Generate answer from context
        logger.debug(
            f"Generating LLM answer for query_id={query_id}",
            extra={"query_id": query_id, "chunks_count": len(vector_results)},
        )

        llm_service = LLMService(openai_client, settings)
        llm_result = await llm_service.generate_answer(
            query_text=request.query_text,
            context_chunks=vector_results,
            temperature=request.temperature,
            query_id=query_id,
        )

        # Step 4: Calculate confidence score and grounding status
        confidence_score = query_service.calculate_confidence(vector_results)

        # Check grounding sufficiency (FR-009)
        if not query_service.validate_grounding(
            confidence_score=confidence_score,
            llm_refused=llm_result["refused"],
        ):
            # Confidence < 0.3 AND LLM didn't refuse = INSUFFICIENT_GROUNDING
            error_response = get_standard_error_response(
                error_code=ErrorCode.INSUFFICIENT_GROUNDING,
                details={
                    "confidence_score": confidence_score,
                    "query_id": query_id,
                },
            )

            # Log to audit table
            latency_ms = int((time.time() - start_time) * 1000)
            await log_query_to_audit_table(
                pool=postgres_pool,
                query_id=query_id,
                user_id=request.user_id,
                chapter_id=request.chapter_id,
                response_time_ms=latency_ms,
                grounding_status=None,  # type: ignore[arg-type]
                citation_count=len(vector_results),
                error_code=ErrorCode.INSUFFICIENT_GROUNDING.value,
                http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_response.model_dump(exclude_none=True),
            )

        grounding_status = query_service.classify_status(confidence_score)

        # Step 5: Prepare sources (convert and sort by similarity)
        sources = query_service.prepare_sources(
            vector_results=vector_results,
            sort_by_similarity=True,  # FR-019: Sort by similarity descending
        )

        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = QueryResponse(
            answer=llm_result["answer"],
            sources=sources,
            confidence_score=confidence_score,
            grounding_status=grounding_status,
            query_id=query_id,
            session_id=request.session_id,
            processing_time_ms=latency_ms,
            created_at=datetime.utcnow(),
            metadata={
                "model_version": llm_result["model"],
                "chunks_retrieved": len(vector_results),
                "llm_refusal": llm_result["refused"],
                "tokens_used": llm_result["tokens_used"],
            },
        )

        # Record metrics
        record_query_latency(
            latency_seconds=latency_ms / 1000,
            chapter_id=request.chapter_id,
            grounding_status=grounding_status.value,
        )
        record_grounding_status(
            chapter_id=request.chapter_id,
            grounding_status=grounding_status.value,
        )
        record_citation_count(
            count=len(sources),
            grounding_status=grounding_status.value,
        )

        # Log to audit table
        await log_query_to_audit_table(
            pool=postgres_pool,
            query_id=query_id,
            user_id=request.user_id,
            chapter_id=request.chapter_id,
            response_time_ms=latency_ms,
            grounding_status=grounding_status,
            citation_count=len(sources),
            error_code=None,
            http_status_code=status.HTTP_200_OK,
        )

        # Log query completion
        log_query_completed(
            logger=logger,
            query_id=query_id,
            user_id=request.user_id,
            chapter_id=request.chapter_id,
            latency_ms=latency_ms,
            status_code=status.HTTP_200_OK,
            grounding_status=grounding_status.value,
            citation_count=len(sources),
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions (already handled above)
        raise

    except (VectorDBError, LLMServiceError) as e:
        # Handle known service errors
        latency_ms = int((time.time() - start_time) * 1000)

        # Log to audit table
        await log_query_to_audit_table(
            pool=postgres_pool,
            query_id=query_id,
            user_id=request.user_id,
            chapter_id=request.chapter_id,
            response_time_ms=latency_ms,
            grounding_status=None,  # type: ignore[arg-type]
            citation_count=0,
            error_code=e.error_code.value,
            http_status_code=e.http_status_code,
        )

        # Return standardized error response
        error_response = get_standard_error_response(
            error_code=e.error_code,
            details=e.details,
        )

        raise HTTPException(
            status_code=e.http_status_code,
            detail=error_response.model_dump(exclude_none=True),
        )

    except Exception as e:
        # Handle unexpected errors
        latency_ms = int((time.time() - start_time) * 1000)

        logger.error(
            f"Unexpected error processing query: {str(e)}",
            extra={"query_id": query_id},
            exc_info=True,
        )

        # Log to audit table
        await log_query_to_audit_table(
            pool=postgres_pool,
            query_id=query_id,
            user_id=request.user_id,
            chapter_id=request.chapter_id,
            response_time_ms=latency_ms,
            grounding_status=None,  # type: ignore[arg-type]
            citation_count=0,
            error_code=ErrorCode.INTERNAL_SERVER_ERROR.value,
            http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

        # Return generic internal error
        error_response = get_standard_error_response(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.model_dump(exclude_none=True),
        )
