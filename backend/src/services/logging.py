"""
Structured logging for RAG Pipeline Query Endpoint.

Provides JSON-formatted logging with privacy-compliant fields for
debugging, auditing, and compliance.

Privacy Compliance (FR-016):
    - NO query_text logging (privacy requirement)
    - user_id_hash: SHA-256 hash of user_id (no PII)
    - Structured JSON format for log aggregation

Log Fields:
    - timestamp: ISO-8601 timestamp
    - level: DEBUG | INFO | WARNING | ERROR | CRITICAL
    - query_id: UUID for request tracing
    - user_id_hash: SHA-256 hash of user_id
    - chapter_id: Chapter identifier
    - status_code: HTTP status code
    - latency_ms: Request latency in milliseconds
    - grounding_status: FULLY_GROUNDED | PARTIALLY_GROUNDED | SPECULATIVE
    - error_code: ErrorCode enum value (if error)

Constitution Compliance:
    - Rule I: 100% type hints, formatted with Black
    - Rule IV: Comprehensive logging for debugging
    - Rule V: No sensitive data logged (privacy-first)
"""

import hashlib
import json
import logging
import sys
from datetime import datetime
from typing import Any

from src.core.config import get_settings


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    Formats log records as JSON objects with standardized fields.
    Privacy-compliant: excludes sensitive data like query_text.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON string.

        Args:
            record: Python logging.LogRecord object

        Returns:
            JSON-formatted log string
        """
        # Base log structure
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add optional fields from extra kwargs
        # Example: logger.info("Query completed", extra={"query_id": "...", "latency_ms": 2500})
        if hasattr(record, "query_id"):
            log_data["query_id"] = record.query_id  # type: ignore[attr-defined]

        if hasattr(record, "user_id_hash"):
            log_data["user_id_hash"] = record.user_id_hash  # type: ignore[attr-defined]

        if hasattr(record, "chapter_id"):
            log_data["chapter_id"] = record.chapter_id  # type: ignore[attr-defined]

        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code  # type: ignore[attr-defined]

        if hasattr(record, "latency_ms"):
            log_data["latency_ms"] = record.latency_ms  # type: ignore[attr-defined]

        if hasattr(record, "grounding_status"):
            log_data["grounding_status"] = record.grounding_status  # type: ignore[attr-defined]

        if hasattr(record, "error_code"):
            log_data["error_code"] = record.error_code  # type: ignore[attr-defined]

        if hasattr(record, "citation_count"):
            log_data["citation_count"] = record.citation_count  # type: ignore[attr-defined]

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add stack trace if present
        if record.stack_info:
            log_data["stack_trace"] = self.formatStack(record.stack_info)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging() -> logging.Logger:
    """
    Configure structured JSON logging for the application.

    Returns:
        Configured root logger instance

    Example:
        logger = setup_logging()
        logger.info("Query completed", extra={
            "query_id": "abc123",
            "user_id_hash": "hash...",
            "chapter_id": "chapter-01",
            "status_code": 200,
            "latency_ms": 2500,
            "grounding_status": "FULLY_GROUNDED"
        })
    """
    settings = get_settings()

    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(settings.log_level)

    # Remove existing handlers (avoid duplicate logs)
    logger.handlers.clear()

    # Create console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(settings.log_level)
    handler.setFormatter(JSONFormatter())

    logger.addHandler(handler)

    # Log initial configuration
    logger.info(
        "Structured logging initialized",
        extra={
            "log_level": settings.log_level,
            "environment": settings.env,
        },
    )

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance for a specific module.

    Args:
        name: Module name (e.g., __name__)

    Returns:
        Logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("Processing request")
    """
    return logging.getLogger(name)


def hash_user_id(user_id: str) -> str:
    """
    Hash user_id for privacy-compliant logging.

    Uses SHA-256 to create irreversible hash of user_id.
    Per FR-016: No PII in logs.

    Args:
        user_id: User UUID or identifier

    Returns:
        SHA-256 hash (64-character hex string)

    Example:
        >>> hash_user_id("user-123")
        'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3'
    """
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()


# =============================================================================
# Logging Helper Functions
# =============================================================================
# These functions provide a clean API for logging common RAG pipeline events.
# =============================================================================


def log_query_started(
    logger: logging.Logger,
    query_id: str,
    user_id: str,
    chapter_id: str,
) -> None:
    """
    Log query request start.

    Args:
        logger: Logger instance
        query_id: Query UUID
        user_id: User identifier (will be hashed)
        chapter_id: Chapter identifier

    Privacy:
        - query_text NOT logged per FR-016
        - user_id hashed before logging
    """
    logger.info(
        "RAG query started",
        extra={
            "query_id": query_id,
            "user_id_hash": hash_user_id(user_id),
            "chapter_id": chapter_id,
        },
    )


def log_query_completed(
    logger: logging.Logger,
    query_id: str,
    user_id: str,
    chapter_id: str,
    latency_ms: int,
    status_code: int,
    grounding_status: str,
    citation_count: int,
) -> None:
    """
    Log successful query completion.

    Args:
        logger: Logger instance
        query_id: Query UUID
        user_id: User identifier (will be hashed)
        chapter_id: Chapter identifier
        latency_ms: Request latency in milliseconds
        status_code: HTTP status code (200)
        grounding_status: FULLY_GROUNDED | PARTIALLY_GROUNDED | SPECULATIVE
        citation_count: Number of citations in response
    """
    logger.info(
        "RAG query completed",
        extra={
            "query_id": query_id,
            "user_id_hash": hash_user_id(user_id),
            "chapter_id": chapter_id,
            "latency_ms": latency_ms,
            "status_code": status_code,
            "grounding_status": grounding_status,
            "citation_count": citation_count,
        },
    )


def log_query_failed(
    logger: logging.Logger,
    query_id: str,
    user_id: str,
    chapter_id: str,
    latency_ms: int,
    status_code: int,
    error_code: str,
    error_message: str,
) -> None:
    """
    Log failed query.

    Args:
        logger: Logger instance
        query_id: Query UUID
        user_id: User identifier (will be hashed)
        chapter_id: Chapter identifier
        latency_ms: Request latency in milliseconds
        status_code: HTTP error status code (400, 401, 403, 429, 500, 503)
        error_code: ErrorCode enum value
        error_message: Human-readable error description
    """
    logger.error(
        f"RAG query failed: {error_message}",
        extra={
            "query_id": query_id,
            "user_id_hash": hash_user_id(user_id),
            "chapter_id": chapter_id,
            "latency_ms": latency_ms,
            "status_code": status_code,
            "error_code": error_code,
        },
    )


def log_vector_search(
    logger: logging.Logger,
    query_id: str,
    chapter_id: str,
    latency_ms: int,
    results_count: int,
) -> None:
    """
    Log Qdrant vector search completion.

    Args:
        logger: Logger instance
        query_id: Query UUID
        chapter_id: Chapter identifier
        latency_ms: Vector search latency in milliseconds
        results_count: Number of chunks retrieved
    """
    logger.debug(
        "Vector search completed",
        extra={
            "query_id": query_id,
            "chapter_id": chapter_id,
            "latency_ms": latency_ms,
            "results_count": results_count,
        },
    )


def log_llm_generation(
    logger: logging.Logger,
    query_id: str,
    latency_ms: int,
    model: str,
    tokens_used: int | None = None,
) -> None:
    """
    Log OpenAI LLM generation completion.

    Args:
        logger: Logger instance
        query_id: Query UUID
        latency_ms: LLM generation latency in milliseconds
        model: OpenAI model name
        tokens_used: Total tokens consumed (optional)
    """
    extra_fields: dict[str, Any] = {
        "query_id": query_id,
        "latency_ms": latency_ms,
        "model": model,
    }

    if tokens_used is not None:
        extra_fields["tokens_used"] = tokens_used

    logger.debug(
        "LLM generation completed",
        extra=extra_fields,
    )


def log_rate_limit_hit(
    logger: logging.Logger,
    user_id: str,
    retry_after_seconds: int,
) -> None:
    """
    Log rate limit violation.

    Args:
        logger: Logger instance
        user_id: User identifier (will be hashed)
        retry_after_seconds: Seconds until rate limit resets
    """
    logger.warning(
        "Rate limit exceeded",
        extra={
            "user_id_hash": hash_user_id(user_id),
            "retry_after_seconds": retry_after_seconds,
        },
    )


def log_authentication_failed(
    logger: logging.Logger,
    error_message: str,
    user_id: str | None = None,
) -> None:
    """
    Log authentication failure.

    Args:
        logger: Logger instance
        error_message: Reason for authentication failure
        user_id: User identifier if available (will be hashed)
    """
    extra_fields: dict[str, Any] = {}

    if user_id:
        extra_fields["user_id_hash"] = hash_user_id(user_id)

    logger.warning(
        f"Authentication failed: {error_message}",
        extra=extra_fields,
    )


def log_authorization_failed(
    logger: logging.Logger,
    user_id: str,
    chapter_id: str,
    reason: str,
) -> None:
    """
    Log authorization failure.

    Args:
        logger: Logger instance
        user_id: User identifier (will be hashed)
        chapter_id: Chapter identifier
        reason: Reason for authorization failure
    """
    logger.warning(
        f"Authorization failed: {reason}",
        extra={
            "user_id_hash": hash_user_id(user_id),
            "chapter_id": chapter_id,
        },
    )
