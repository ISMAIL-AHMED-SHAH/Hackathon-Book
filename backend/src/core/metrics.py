"""
Prometheus metrics for RAG Pipeline Query Endpoint.

Provides instrumentation for performance monitoring, SLO tracking, and debugging.

Metrics:
    - query_latency_seconds: Histogram of query end-to-end latency
    - grounding_quality_rate: Counter for grounding status distribution
    - query_errors_total: Counter for error types
    - rate_limit_hits_total: Counter for rate limit violations

Constitution Compliance:
    - Rule I: 100% type hints, formatted with Black
    - Rule IV: Comprehensive observability for debugging
    - Performance tracking per FR-015 (30-second timeout target)
"""

from prometheus_client import Counter, Histogram


# =============================================================================
# Query Latency Metrics (FR-015: Performance Monitoring)
# =============================================================================
# Histogram to track p50, p95, p99 latency for RAG queries.
# Target: p95 < 30 seconds (per FR-015)
#
# Buckets (in seconds):
# - 0.1, 0.5, 1, 2, 5: Fast queries (cached, simple)
# - 10, 15, 20, 25: Normal RAG queries (vector search + LLM)
# - 30: Timeout threshold (FR-015)
# - 60: Max timeout (should be rare)
# =============================================================================

query_latency_seconds = Histogram(
    name="rag_query_latency_seconds",
    documentation="End-to-end latency for RAG query requests (seconds)",
    labelnames=["chapter_id", "grounding_status"],
    buckets=(0.1, 0.5, 1, 2, 5, 10, 15, 20, 25, 30, 60),
)

# =============================================================================
# Grounding Quality Metrics (FR-004: RAG Quality Tracking)
# =============================================================================
# Counter to track distribution of grounding status:
# - FULLY_GROUNDED: High-quality responses with citations (target: >70%)
# - PARTIALLY_GROUNDED: Mixed quality (target: <25%)
# - SPECULATIVE: No relevant context found (target: <5%)
#
# Labels:
# - chapter_id: Track per-chapter quality
# - grounding_status: FULLY_GROUNDED | PARTIALLY_GROUNDED | SPECULATIVE
# =============================================================================

grounding_quality_rate = Counter(
    name="rag_grounding_quality_total",
    documentation="Count of responses by grounding status (quality metric)",
    labelnames=["chapter_id", "grounding_status"],
)

# =============================================================================
# Error Metrics (FR-013: Error Handling & Debugging)
# =============================================================================
# Counter to track error types for debugging and alerting.
#
# Labels:
# - error_code: Standardized ErrorCode enum value
# - http_status_code: HTTP status code (400, 401, 403, 429, 500, 503)
#
# Common error codes:
# - RATE_LIMIT_EXCEEDED (429): Rate limiting triggered
# - VECTOR_DB_TIMEOUT (503): Qdrant timeout (>5s)
# - LLM_TIMEOUT (503): OpenAI timeout (>25s)
# - AUTHENTICATION_FAILED (401): JWT validation failed
# - CHAPTER_NOT_ACCESSIBLE (403): User lacks chapter access
# =============================================================================

query_errors_total = Counter(
    name="rag_query_errors_total",
    documentation="Total count of query errors by type",
    labelnames=["error_code", "http_status_code"],
)

# =============================================================================
# Rate Limiting Metrics (FR-014: Rate Limiting Monitoring)
# =============================================================================
# Counter to track rate limit violations (429 errors).
# Target: <1% of total requests should hit rate limit
#
# Labels:
# - user_id_hash: SHA-256 hash of user_id (privacy-compliant)
#
# Use case:
# - Alert if rate limit hit rate spikes (indicates abuse or incorrect limits)
# - Analyze per-user patterns to detect potential abuse
# =============================================================================

rate_limit_hits_total = Counter(
    name="rag_rate_limit_hits_total",
    documentation="Total count of rate limit violations",
    labelnames=["user_id_hash"],
)

# =============================================================================
# Additional Component Metrics
# =============================================================================
# These metrics track individual RAG pipeline component performance
# for detailed debugging and optimization.
# =============================================================================

# Vector search latency (Qdrant query time only, excluding LLM)
vector_search_latency_seconds = Histogram(
    name="rag_vector_search_latency_seconds",
    documentation="Latency for Qdrant vector search only (seconds)",
    labelnames=["chapter_id"],
    buckets=(0.05, 0.1, 0.5, 1, 2, 5),  # Target: <1s for vector search
)

# LLM generation latency (OpenAI API call time only)
llm_generation_latency_seconds = Histogram(
    name="rag_llm_generation_latency_seconds",
    documentation="Latency for LLM response generation only (seconds)",
    labelnames=["model"],
    buckets=(1, 2, 5, 10, 15, 20, 25),  # Target: <15s for LLM generation
)

# Citation count distribution (number of citations per response)
# Useful for understanding retrieval quality
citation_count_distribution = Histogram(
    name="rag_citation_count_distribution",
    documentation="Distribution of citation counts per response",
    labelnames=["grounding_status"],
    buckets=(0, 1, 2, 3, 5, 7, 10, 15),  # Typical range: 3-7 citations
)

# Database connection pool metrics
database_connections_active = Counter(
    name="rag_database_connections_active",
    documentation="Active database connections (Neon Postgres)",
    labelnames=["pool_name"],
)

# Redis cache hit rate
cache_operations_total = Counter(
    name="rag_cache_operations_total",
    documentation="Total cache operations (hit/miss)",
    labelnames=["operation"],  # hit | miss | set
)


# =============================================================================
# Metric Recording Helper Functions
# =============================================================================
# These functions provide a clean API for recording metrics in application code.
# =============================================================================


def record_query_latency(
    latency_seconds: float,
    chapter_id: str,
    grounding_status: str,
) -> None:
    """
    Record end-to-end query latency.

    Args:
        latency_seconds: Total query duration in seconds
        chapter_id: Chapter identifier
        grounding_status: FULLY_GROUNDED | PARTIALLY_GROUNDED | SPECULATIVE
    """
    query_latency_seconds.labels(
        chapter_id=chapter_id,
        grounding_status=grounding_status,
    ).observe(latency_seconds)


def record_grounding_status(chapter_id: str, grounding_status: str) -> None:
    """
    Record grounding quality status.

    Args:
        chapter_id: Chapter identifier
        grounding_status: FULLY_GROUNDED | PARTIALLY_GROUNDED | SPECULATIVE
    """
    grounding_quality_rate.labels(
        chapter_id=chapter_id,
        grounding_status=grounding_status,
    ).inc()


def record_error(error_code: str, http_status_code: int) -> None:
    """
    Record query error.

    Args:
        error_code: ErrorCode enum value (e.g., "RATE_LIMIT_EXCEEDED")
        http_status_code: HTTP status code (400, 401, 403, 429, 500, 503)
    """
    query_errors_total.labels(
        error_code=error_code,
        http_status_code=str(http_status_code),
    ).inc()


def record_rate_limit_hit(user_id_hash: str) -> None:
    """
    Record rate limit violation.

    Args:
        user_id_hash: SHA-256 hash of user_id (privacy-compliant)
    """
    rate_limit_hits_total.labels(user_id_hash=user_id_hash).inc()


def record_vector_search_latency(latency_seconds: float, chapter_id: str) -> None:
    """
    Record Qdrant vector search latency.

    Args:
        latency_seconds: Vector search duration in seconds
        chapter_id: Chapter identifier
    """
    vector_search_latency_seconds.labels(chapter_id=chapter_id).observe(latency_seconds)


def record_llm_generation_latency(latency_seconds: float, model: str) -> None:
    """
    Record OpenAI LLM generation latency.

    Args:
        latency_seconds: LLM generation duration in seconds
        model: OpenAI model name (e.g., "gpt-4-turbo-preview")
    """
    llm_generation_latency_seconds.labels(model=model).observe(latency_seconds)


def record_citation_count(count: int, grounding_status: str) -> None:
    """
    Record number of citations in response.

    Args:
        count: Number of citations
        grounding_status: FULLY_GROUNDED | PARTIALLY_GROUNDED | SPECULATIVE
    """
    citation_count_distribution.labels(grounding_status=grounding_status).observe(count)


def record_cache_hit() -> None:
    """Record Redis cache hit."""
    cache_operations_total.labels(operation="hit").inc()


def record_cache_miss() -> None:
    """Record Redis cache miss."""
    cache_operations_total.labels(operation="miss").inc()


def record_cache_set() -> None:
    """Record Redis cache set operation."""
    cache_operations_total.labels(operation="set").inc()
