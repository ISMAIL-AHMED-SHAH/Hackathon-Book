"""
Standardized error handling for RAG Pipeline Query Endpoint.

This module provides consistent error response structures per Constitution Rule III.
All error responses follow the format: {"error_code": "...", "message": "..."}
"""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class ErrorCode(str, Enum):
    """
    Standardized error codes for RAG Query Endpoint.
    Aligns with FR-010 and FR-011 requirements.
    """

    # 400 Bad Request - Invalid client input
    INVALID_INPUT = "INVALID_INPUT"
    QUERY_TEXT_EMPTY = "QUERY_TEXT_EMPTY"
    INVALID_CHAPTER_ID = "INVALID_CHAPTER_ID"
    INVALID_USER_ID = "INVALID_USER_ID"
    INVALID_SESSION_ID = "INVALID_SESSION_ID"
    # Used for T005, T3.1
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    # 401 Unauthorized - Authentication failures
    MISSING_TOKEN = "MISSING_TOKEN"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"

    # 403 Forbidden - Authorization failures
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    CHAPTER_ACCESS_DENIED = "CHAPTER_ACCESS_DENIED"
    CHAPTER_NOT_ACCESSIBLE = "CHAPTER_NOT_ACCESSIBLE"
    SUBSCRIPTION_REQUIRED = "SUBSCRIPTION_REQUIRED"

    # 404 Not Found - Resource doesn't exist
    CHAPTER_NOT_FOUND = "CHAPTER_NOT_FOUND"
    CONTEXT_NOT_FOUND = "CONTEXT_NOT_FOUND"

    # 422 Unprocessable Entity - Business logic failures
    INSUFFICIENT_GROUNDING = "INSUFFICIENT_GROUNDING"
    QUERY_TOO_BROAD = "QUERY_TOO_BROAD"

    # 429 Too Many Requests - Rate limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # 500 Internal Server Error - Server failures
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    LLM_SERVICE_ERROR = "LLM_SERVICE_ERROR"
    VECTOR_DB_ERROR = "VECTOR_DB_ERROR"

    # 503 Service Unavailable - Temporary unavailability
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    LLM_QUOTA_EXCEEDED = "LLM_QUOTA_EXCEEDED"

    # Used for general validation, server errors (T005)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    SERVER_ERROR = "SERVER_ERROR"

    # Placeholder for future Ingestion tasks (P7)
    INGESTION_ERROR = "INGESTION_ERROR"

    # Placeholder for general errors
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class StandardErrorResponse(BaseModel):
    """
    Standardized error response structure for all non-2xx responses.
    Aligns with Constitution Rule III (Error Handling).
    """

    error_code: ErrorCode = Field(..., description="Machine-readable error code")

    message: str = Field(..., description="Human-readable error message")

    field: Optional[str] = Field(None, description="Field name if error is field-specific")

    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error context (safe for client consumption)"
    )

    request_id: Optional[str] = Field(None, description="Request tracking ID for support/debugging")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "error_code": "QUERY_TEXT_EMPTY",
                    "message": "Query text cannot be empty or whitespace",
                    "field": "query_text",
                    "details": None,
                    "request_id": "req-a1b2c3d4",
                },
                {
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": "Query rate limit exceeded (max 10/minute per user)",
                    "field": None,
                    "details": {"retry_after": 60},
                    "request_id": "req-e5f6g7h8",
                },
            ]
        }
    )


def get_standard_error_response(
    error_code: ErrorCode | str,
    message: Optional[str] = None,
    status_code: int = 400,
    field: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> StandardErrorResponse:
    """
    Generate a standardized error response.

    Args:
        error_code: Machine-readable error code (ErrorCode enum or string)
        message: Human-readable error message (auto-generated if None)
        status_code: HTTP status code (default: 400)
        field: Optional field name if error is field-specific
        details: Optional additional error context
        request_id: Optional request tracking ID

    Returns:
        StandardErrorResponse model

    Raises:
        ValueError: If error_code is not a valid ErrorCode enum value

    Example:
        >>> error = get_standard_error_response(
        ...     error_code=ErrorCode.QUERY_TEXT_EMPTY,
        ...     field="query_text"
        ... )
        >>> error.error_code
        <ErrorCode.QUERY_TEXT_EMPTY: 'QUERY_TEXT_EMPTY'>
    """
    # Convert to ErrorCode enum if string
    if isinstance(error_code, str):
        try:
            error_code_enum = ErrorCode(error_code)
        except ValueError:
            raise ValueError(
                f"Invalid error_code '{error_code}'. Must be one of: "
                f"{', '.join([e.value for e in ErrorCode])}"
            )
    else:
        error_code_enum = error_code

    # Generate default message if not provided
    if message is None:
        message = _get_default_error_message(error_code_enum, details)

    # Create the error response model
    error_response = StandardErrorResponse(
        error_code=error_code_enum,
        message=message,
        field=field,
        details=details,
        request_id=request_id,
    )

    return error_response


def _get_default_error_message(
    error_code: ErrorCode, details: Optional[Dict[str, Any]] = None
) -> str:
    """
    Get default error message for an error code.

    Args:
        error_code: ErrorCode enum value
        details: Optional details dict for context

    Returns:
        Default human-readable error message
    """
    messages = {
        ErrorCode.CONTEXT_NOT_FOUND: "No relevant content found for this query in the specified chapter",
        ErrorCode.INSUFFICIENT_GROUNDING: "Unable to generate a well-grounded answer from available content",
        ErrorCode.CHAPTER_NOT_FOUND: "The specified chapter does not exist",
        ErrorCode.CHAPTER_NOT_ACCESSIBLE: "You do not have access to this chapter",
        ErrorCode.SUBSCRIPTION_REQUIRED: "A subscription is required to access this chapter",
        ErrorCode.AUTHORIZATION_FAILED: "Authorization failed",
        ErrorCode.VECTOR_DB_ERROR: "Vector database error occurred",
        ErrorCode.LLM_SERVICE_ERROR: "Language model service error occurred",
        ErrorCode.INTERNAL_SERVER_ERROR: "An internal server error occurred",
        ErrorCode.INTERNAL_ERROR: "An internal error occurred",
    }

    return messages.get(error_code, f"An error occurred: {error_code.value}")
