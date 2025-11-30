"""
Custom exception classes for RAG Pipeline Query Endpoint.

All exceptions map to ErrorCode enum from utils.error_handler for
standardized error responses per Constitution Rule III.

Exception Hierarchy:
    RAGBaseException (base class)
    ├── AuthenticationError (401 Unauthorized)
    ├── AuthorizationError (403 Forbidden)
    ├── ValidationError (400 Bad Request)
    ├── RateLimitError (429 Too Many Requests)
    ├── VectorDBError (500/503 Internal Server Error)
    └── LLMServiceError (500/503 Internal Server Error)

Constitution Compliance:
    - Rule I: 100% type hints, formatted with Black
    - Rule III: Standardized error taxonomy with HTTP status codes
    - Rule IV: Explicit error messages for debugging
"""

from typing import Any

from src.utils.error_handler import ErrorCode


class RAGBaseException(Exception):
    """
    Base exception for all RAG pipeline errors.

    All custom exceptions inherit from this base class for consistent
    error handling and logging.

    Attributes:
        message: Human-readable error description
        error_code: Standardized error code from ErrorCode enum
        http_status_code: HTTP status code for API responses
        details: Additional context for debugging (optional)
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        http_status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize base exception.

        Args:
            message: Human-readable error description
            error_code: Standardized error code from ErrorCode enum
            http_status_code: HTTP status code (default: 500)
            details: Additional context dict (optional)
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.http_status_code = http_status_code
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation of exception."""
        return f"[{self.error_code.value}] {self.message}"

    def __repr__(self) -> str:
        """Return detailed representation of exception."""
        return (
            f"{self.__class__.__name__}(message={self.message!r}, "
            f"error_code={self.error_code!r}, "
            f"http_status_code={self.http_status_code}, "
            f"details={self.details!r})"
        )


class AuthenticationError(RAGBaseException):
    """
    Raised when JWT token is invalid or missing.

    Maps to:
        - HTTP 401 Unauthorized
        - ErrorCode.AUTHENTICATION_FAILED
        - ErrorCode.INVALID_TOKEN
        - ErrorCode.EXPIRED_TOKEN

    Used by:
        - FR-001: JWT token validation
        - Better-Auth token verification

    Example:
        raise AuthenticationError(
            message="JWT token has expired",
            error_code=ErrorCode.EXPIRED_TOKEN
        )
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: ErrorCode = ErrorCode.AUTHENTICATION_FAILED,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize authentication error.

        Args:
            message: Human-readable error description
            error_code: ErrorCode (default: AUTHENTICATION_FAILED)
            details: Additional context (optional)
        """
        super().__init__(
            message=message,
            error_code=error_code,
            http_status_code=401,
            details=details,
        )


class AuthorizationError(RAGBaseException):
    """
    Raised when user lacks permission to access a resource.

    Maps to:
        - HTTP 403 Forbidden
        - ErrorCode.AUTHORIZATION_FAILED
        - ErrorCode.SUBSCRIPTION_REQUIRED
        - ErrorCode.CHAPTER_NOT_ACCESSIBLE

    Used by:
        - FR-002: Chapter access verification
        - Subscription tier validation

    Example:
        raise AuthorizationError(
            message="User does not have access to chapter-05",
            error_code=ErrorCode.CHAPTER_NOT_ACCESSIBLE,
            details={"chapter_id": "chapter-05", "user_subscription": "free"}
        )
    """

    def __init__(
        self,
        message: str = "Authorization failed",
        error_code: ErrorCode = ErrorCode.AUTHORIZATION_FAILED,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize authorization error.

        Args:
            message: Human-readable error description
            error_code: ErrorCode (default: AUTHORIZATION_FAILED)
            details: Additional context (optional)
        """
        super().__init__(
            message=message,
            error_code=error_code,
            http_status_code=403,
            details=details,
        )


class ValidationError(RAGBaseException):
    """
    Raised when request data fails validation.

    Maps to:
        - HTTP 400 Bad Request
        - ErrorCode.VALIDATION_ERROR
        - ErrorCode.INVALID_QUERY_TEXT
        - ErrorCode.INVALID_CHAPTER_ID
        - ErrorCode.INVALID_USER_ID

    Used by:
        - Pydantic request validation (QueryRequest schema)
        - Custom field validators

    Example:
        raise ValidationError(
            message="Query text cannot be empty",
            error_code=ErrorCode.INVALID_QUERY_TEXT,
            details={"field": "query_text", "constraint": "min_length=1"}
        )
    """

    def __init__(
        self,
        message: str = "Validation failed",
        error_code: ErrorCode = ErrorCode.VALIDATION_ERROR,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Human-readable error description
            error_code: ErrorCode (default: VALIDATION_ERROR)
            details: Additional context (optional)
        """
        super().__init__(
            message=message,
            error_code=error_code,
            http_status_code=400,
            details=details,
        )


class RateLimitError(RAGBaseException):
    """
    Raised when user exceeds rate limit.

    Maps to:
        - HTTP 429 Too Many Requests
        - ErrorCode.RATE_LIMIT_EXCEEDED

    Used by:
        - FR-014: Rate limiting (10 requests/minute/user)
        - Redis rate limit counter

    Example:
        raise RateLimitError(
            message="Rate limit exceeded: 10 requests per minute",
            details={"retry_after_seconds": 45, "limit": 10, "window": 60}
        )
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        error_code: ErrorCode = ErrorCode.RATE_LIMIT_EXCEEDED,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize rate limit error.

        Args:
            message: Human-readable error description
            error_code: ErrorCode (default: RATE_LIMIT_EXCEEDED)
            details: Should include retry_after_seconds (optional)
        """
        super().__init__(
            message=message,
            error_code=error_code,
            http_status_code=429,
            details=details,
        )


class VectorDBError(RAGBaseException):
    """
    Raised when Qdrant vector database operation fails.

    Maps to:
        - HTTP 500 Internal Server Error (connection/unknown errors)
        - HTTP 503 Service Unavailable (timeout errors)
        - ErrorCode.VECTOR_DB_ERROR
        - ErrorCode.VECTOR_DB_TIMEOUT

    Used by:
        - FR-003: Vector search failures
        - FR-015: Qdrant timeout (5-second limit)
        - Qdrant connection errors

    Example:
        raise VectorDBError(
            message="Qdrant search timed out after 5 seconds",
            error_code=ErrorCode.VECTOR_DB_TIMEOUT,
            http_status_code=503,
            details={"timeout_seconds": 5, "query_vector_size": 1536}
        )
    """

    def __init__(
        self,
        message: str = "Vector database error",
        error_code: ErrorCode = ErrorCode.VECTOR_DB_ERROR,
        http_status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize vector database error.

        Args:
            message: Human-readable error description
            error_code: ErrorCode (default: VECTOR_DB_ERROR)
            http_status_code: HTTP status (500 or 503)
            details: Additional context (optional)
        """
        super().__init__(
            message=message,
            error_code=error_code,
            http_status_code=http_status_code,
            details=details,
        )


class LLMServiceError(RAGBaseException):
    """
    Raised when OpenAI LLM service call fails.

    Maps to:
        - HTTP 500 Internal Server Error (connection/unknown errors)
        - HTTP 503 Service Unavailable (timeout/overload errors)
        - ErrorCode.LLM_SERVICE_ERROR
        - ErrorCode.LLM_TIMEOUT

    Used by:
        - FR-004: LLM generation failures
        - FR-015: OpenAI timeout (25-second limit)
        - OpenAI API errors (rate limits, invalid requests)

    Example:
        raise LLMServiceError(
            message="OpenAI API request timed out after 25 seconds",
            error_code=ErrorCode.LLM_TIMEOUT,
            http_status_code=503,
            details={"timeout_seconds": 25, "model": "gpt-4-turbo-preview"}
        )
    """

    def __init__(
        self,
        message: str = "LLM service error",
        error_code: ErrorCode = ErrorCode.LLM_SERVICE_ERROR,
        http_status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize LLM service error.

        Args:
            message: Human-readable error description
            error_code: ErrorCode (default: LLM_SERVICE_ERROR)
            http_status_code: HTTP status (500 or 503)
            details: Additional context (optional)
        """
        super().__init__(
            message=message,
            error_code=error_code,
            http_status_code=http_status_code,
            details=details,
        )


# Convenience functions for common error scenarios


def authentication_failed(
    message: str = "Invalid or missing authentication token",
) -> AuthenticationError:
    """Create AuthenticationError for missing/invalid token."""
    return AuthenticationError(
        message=message,
        error_code=ErrorCode.AUTHENTICATION_FAILED,
    )


def token_expired(message: str = "JWT token has expired") -> AuthenticationError:
    """Create AuthenticationError for expired token."""
    return AuthenticationError(
        message=message,
        error_code=ErrorCode.EXPIRED_TOKEN,
    )


def chapter_not_accessible(chapter_id: str, subscription_tier: str) -> AuthorizationError:
    """Create AuthorizationError for inaccessible chapter."""
    return AuthorizationError(
        message=f"Chapter '{chapter_id}' is not accessible with '{subscription_tier}' subscription",
        error_code=ErrorCode.CHAPTER_NOT_ACCESSIBLE,
        details={"chapter_id": chapter_id, "subscription_tier": subscription_tier},
    )


def rate_limit_exceeded(retry_after: int = 60) -> RateLimitError:
    """Create RateLimitError with retry-after hint."""
    return RateLimitError(
        message=f"Rate limit exceeded. Try again in {retry_after} seconds.",
        details={"retry_after_seconds": retry_after},
    )


def vector_db_timeout(timeout_seconds: int = 5) -> VectorDBError:
    """Create VectorDBError for timeout."""
    return VectorDBError(
        message=f"Vector database query timed out after {timeout_seconds} seconds",
        error_code=ErrorCode.VECTOR_DB_TIMEOUT,
        http_status_code=503,
        details={"timeout_seconds": timeout_seconds},
    )


def llm_timeout(timeout_seconds: int = 25) -> LLMServiceError:
    """Create LLMServiceError for timeout."""
    return LLMServiceError(
        message=f"LLM request timed out after {timeout_seconds} seconds",
        error_code=ErrorCode.LLM_TIMEOUT,
        http_status_code=503,
        details={"timeout_seconds": timeout_seconds},
    )
