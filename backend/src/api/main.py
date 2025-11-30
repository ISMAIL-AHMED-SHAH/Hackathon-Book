"""
FastAPI application for RAG Pipeline Query Endpoint.

Main application entry point with:
    - FastAPI app initialization
    - CORS middleware
    - Prometheus metrics middleware
    - Exception handlers
    - Health and metrics endpoints
    - Lifespan context manager for client initialization

Constitution Compliance:
    - Rule I: 100% type hints, formatted with Black
    - Rule III: Standardized error responses
    - Rule IV: Comprehensive observability (logging + metrics)
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest
from pydantic import ValidationError
from starlette.responses import Response

from src.api.dependencies import (
    check_all_services_health,
    shutdown_clients,
    startup_clients,
)
from src.core.config import get_settings
from src.core.exceptions import RAGBaseException
from src.core.metrics import record_error
from src.services.logging import get_logger, setup_logging
from src.utils.error_handler import get_standard_error_response

# Initialize structured logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Lifespan context manager for application startup/shutdown.

    Handles:
        - Initialize all singleton clients (Qdrant, Redis, Postgres, OpenAI)
        - Clean up clients on shutdown

    Args:
        app: FastAPI application instance

    Yields:
        None (context manager)
    """
    # Startup
    logger.info("Application startup initiated")
    settings = get_settings()
    logger.info(
        f"Starting RAG Pipeline API",
        extra={
            "environment": settings.env,
            "log_level": settings.log_level,
            "api_version": settings.api_version,
        },
    )

    try:
        await startup_clients()
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Application startup failed: {e}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Application shutdown initiated")
    try:
        await shutdown_clients()
        logger.info("Application shutdown completed successfully")
    except Exception as e:
        logger.error(f"Application shutdown error: {e}", exc_info=True)


# =============================================================================
# FastAPI Application
# =============================================================================

settings = get_settings()

app = FastAPI(
    title="RAG Pipeline Query Endpoint",
    description="Retrieval-Augmented Generation API for Physical AI Textbook",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=f"/{settings.api_version}/docs",
    redoc_url=f"/{settings.api_version}/redoc",
    openapi_url=f"/{settings.api_version}/openapi.json",
)

# =============================================================================
# Middleware
# =============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)


# =============================================================================
# Exception Handlers
# =============================================================================


@app.exception_handler(RAGBaseException)
async def rag_exception_handler(
    request: Request,
    exc: RAGBaseException,
) -> JSONResponse:
    """
    Handle custom RAG pipeline exceptions.

    Args:
        request: FastAPI request
        exc: RAGBaseException or subclass

    Returns:
        JSONResponse with standardized error format
    """
    # Record error metric
    record_error(
        error_code=exc.error_code.value,
        http_status_code=exc.http_status_code,
    )

    # Log error
    logger.error(
        f"RAG exception: {exc.message}",
        extra={
            "error_code": exc.error_code.value,
            "http_status_code": exc.http_status_code,
            "details": exc.details,
            "path": request.url.path,
        },
    )

    # Return standardized error response
    error_response = get_standard_error_response(
        error_code=exc.error_code,
        details=exc.details,
    )

    return JSONResponse(
        status_code=exc.http_status_code,
        content=error_response.model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Handle Pydantic request validation errors.

    Args:
        request: FastAPI request
        exc: RequestValidationError from Pydantic

    Returns:
        JSONResponse with standardized error format
    """
    from src.utils.error_handler import ErrorCode

    # Extract validation error details
    errors = exc.errors()
    details = {
        "validation_errors": [
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in errors
        ]
    }

    # Record error metric
    record_error(
        error_code=ErrorCode.VALIDATION_ERROR.value,
        http_status_code=status.HTTP_400_BAD_REQUEST,
    )

    # Log error
    logger.warning(
        "Request validation failed",
        extra={
            "error_code": ErrorCode.VALIDATION_ERROR.value,
            "http_status_code": status.HTTP_400_BAD_REQUEST,
            "details": details,
            "path": request.url.path,
        },
    )

    # Return standardized error response
    error_response = get_standard_error_response(
        error_code=ErrorCode.VALIDATION_ERROR,
        details=details,
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response.model_dump(),
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(
    request: Request,
    exc: ValidationError,
) -> JSONResponse:
    """
    Handle Pydantic model validation errors.

    Args:
        request: FastAPI request
        exc: ValidationError from Pydantic

    Returns:
        JSONResponse with standardized error format
    """
    from src.utils.error_handler import ErrorCode

    # Extract validation error details
    errors = exc.errors()
    details = {
        "validation_errors": [
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in errors
        ]
    }

    # Record error metric
    record_error(
        error_code=ErrorCode.VALIDATION_ERROR.value,
        http_status_code=status.HTTP_400_BAD_REQUEST,
    )

    # Log error
    logger.warning(
        "Pydantic validation failed",
        extra={
            "error_code": ErrorCode.VALIDATION_ERROR.value,
            "http_status_code": status.HTTP_400_BAD_REQUEST,
            "details": details,
            "path": request.url.path,
        },
    )

    # Return standardized error response
    error_response = get_standard_error_response(
        error_code=ErrorCode.VALIDATION_ERROR,
        details=details,
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response.model_dump(),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Args:
        request: FastAPI request
        exc: Unexpected exception

    Returns:
        JSONResponse with standardized error format
    """
    from src.utils.error_handler import ErrorCode

    # Record error metric
    record_error(
        error_code=ErrorCode.INTERNAL_SERVER_ERROR.value,
        http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

    # Log error with full traceback
    logger.error(
        f"Unexpected exception: {str(exc)}",
        extra={
            "error_code": ErrorCode.INTERNAL_SERVER_ERROR.value,
            "http_status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "exception_type": type(exc).__name__,
            "path": request.url.path,
        },
        exc_info=True,
    )

    # Return standardized error response (no details to avoid leaking internals)
    error_response = get_standard_error_response(
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(exclude_none=True),
    )


# =============================================================================
# Health and Metrics Endpoints
# =============================================================================


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint.

    Returns overall application health and status of all dependencies.

    Returns:
        Health status dict with service details

    Example Response:
        {
            "status": "healthy",
            "version": "1.0.0",
            "environment": "production",
            "services": {
                "qdrant": {"status": "healthy", "collections": "3"},
                "redis": {"status": "healthy"},
                "postgres": {"status": "healthy", "pool_size": "5"},
                "openai": {"status": "healthy"}
            }
        }
    """
    services_health = await check_all_services_health()

    # Determine overall health status
    overall_status = "healthy"
    if any(service["status"] == "unhealthy" for service in services_health.values()):
        overall_status = "degraded"

    return {
        "status": overall_status,
        "version": "1.0.0",
        "environment": settings.env,
        "services": services_health,
    }


@app.get("/metrics", tags=["Metrics"])
async def metrics() -> Response:
    """
    Prometheus metrics endpoint.

    Returns Prometheus-formatted metrics for monitoring.

    Returns:
        Response with Prometheus metrics

    Example Metrics:
        # HELP rag_query_latency_seconds End-to-end latency for RAG queries
        # TYPE rag_query_latency_seconds histogram
        rag_query_latency_seconds_bucket{le="1.0"} 45.0
        rag_query_latency_seconds_bucket{le="5.0"} 120.0
        ...
    """
    metrics_data = generate_latest(REGISTRY)
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """
    Root endpoint.

    Returns:
        API information

    Example Response:
        {
            "message": "RAG Pipeline Query Endpoint API",
            "version": "v1",
            "docs": "/v1/docs"
        }
    """
    return {
        "message": "RAG Pipeline Query Endpoint API",
        "version": settings.api_version,
        "docs": f"/{settings.api_version}/docs",
    }


# =============================================================================
# API Routes
# =============================================================================

from src.api.v1.query import router as query_router

app.include_router(
    query_router,
    prefix=f"/{settings.api_version}",
    tags=["Query"],
)

# =============================================================================
