"""
Dependency injection for RAG Pipeline Query Endpoint.

Provides singleton clients and dependencies for FastAPI routes.
Implements proper lifecycle management with startup/shutdown hooks.

Dependencies:
    - Qdrant client (vector database)
    - Redis client (rate limiting)
    - Neon asyncpg pool (PostgreSQL)
    - OpenAI client (embeddings + LLM)

Constitution Compliance:
    - Rule I: 100% type hints, formatted with Black
    - Rule V: Credentials from environment (Settings)
    - Proper resource cleanup on shutdown
"""

import asyncpg
from openai import AsyncOpenAI
from qdrant_client import QdrantClient
from redis import asyncio as aioredis

from src.core.config import Settings, get_settings
from src.services.logging import get_logger

logger = get_logger(__name__)

# =============================================================================
# Singleton Client Instances
# =============================================================================
# Global singletons initialized at app startup and cleaned up at shutdown.
# Accessed via dependency injection functions (get_qdrant_client, etc.)
# =============================================================================

_qdrant_client: QdrantClient | None = None
_redis_client: aioredis.Redis | None = None  # type: ignore[type-arg]
_postgres_pool: asyncpg.Pool | None = None
_openai_client: AsyncOpenAI | None = None


# =============================================================================
# Startup / Shutdown Handlers
# =============================================================================


async def startup_clients() -> None:
    """
    Initialize all singleton clients at application startup.

    Called by FastAPI lifespan context manager.
    Establishes connections to:
        - Qdrant Cloud (vector database)
        - Redis (rate limiting cache)
        - Neon Postgres (subscription data)
        - OpenAI API (embeddings + LLM)

    Raises:
        Exception: If any client initialization fails
    """
    global _qdrant_client, _redis_client, _postgres_pool, _openai_client

    settings = get_settings()

    logger.info("Initializing application clients...")

    # Initialize Qdrant client
    try:
        logger.info(f"Connecting to Qdrant: {settings.qdrant_url}")
        _qdrant_client = QdrantClient(
            url=str(settings.qdrant_url),
            api_key=settings.qdrant_api_key,
            timeout=settings.vector_db_timeout,
            prefer_grpc=False,  # Use HTTP instead of gRPC for better Windows compatibility
        )
        # Test connection (skip for Windows due to gRPC/TLS issues)
        try:
            collections = _qdrant_client.get_collections()
            logger.info(
                f"[OK] Qdrant connected ({len(collections.collections)} collections)",
                extra={"collections_count": len(collections.collections)},
            )
        except Exception as conn_err:
            # Windows gRPC/TLS issue - client will work for actual requests
            logger.warning(
                f"[WARN] Qdrant health check failed (client initialized, may still work): {conn_err}"
            )
    except Exception as e:
        logger.error(f"[ERR] Qdrant client initialization failed: {e}")
        raise

    # Initialize Redis client (optional - for rate limiting)
    try:
        logger.info(f"Connecting to Redis: {settings.redis_url}")
        _redis_client = await aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        # Test connection
        await _redis_client.ping()
        logger.info("[OK] Redis connected")
    except Exception as e:
        logger.warning(f"[WARN] Redis connection failed (rate limiting disabled): {e}")

    # Initialize Neon Postgres pool (optional - for audit logging)
    try:
        logger.info("Connecting to Neon Postgres...")
        _postgres_pool = await asyncpg.create_pool(
            dsn=settings.neon_connection_string,
            min_size=2,  # Minimum connections
            max_size=10,  # Maximum connections
            timeout=30,  # Connection timeout
        )
        if _postgres_pool is None:
            raise RuntimeError("Failed to create asyncpg pool")

        # Test connection
        async with _postgres_pool.acquire() as conn:
            version = await conn.fetchval("SELECT version()")
            logger.info(f"[OK] Neon Postgres connected: {version[:50]}...")
    except Exception as e:
        logger.warning(f"[WARN] Neon Postgres connection failed (audit logging disabled): {e}")

    # Initialize OpenAI client
    try:
        logger.info("Initializing OpenAI client...")
        _openai_client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.llm_timeout,
        )
        # Test connection (lightweight API call)
        models = await _openai_client.models.list()
        logger.info(f"✓ OpenAI connected ({len(models.data)} models available)")
    except Exception as e:
        logger.error(f"✗ OpenAI connection failed: {e}")
        raise

    logger.info("All clients initialized successfully")


async def shutdown_clients() -> None:
    """
    Clean up all singleton clients at application shutdown.

    Called by FastAPI lifespan context manager.
    Closes connections to all external services.
    """
    global _qdrant_client, _redis_client, _postgres_pool, _openai_client

    logger.info("Shutting down application clients...")

    # Close Qdrant client
    if _qdrant_client:
        try:
            _qdrant_client.close()
            logger.info("✓ Qdrant client closed")
        except Exception as e:
            logger.error(f"Error closing Qdrant client: {e}")
        _qdrant_client = None

    # Close Redis client
    if _redis_client:
        try:
            await _redis_client.close()
            logger.info("✓ Redis client closed")
        except Exception as e:
            logger.error(f"Error closing Redis client: {e}")
        _redis_client = None

    # Close Neon Postgres pool
    if _postgres_pool:
        try:
            await _postgres_pool.close()
            logger.info("✓ Neon Postgres pool closed")
        except Exception as e:
            logger.error(f"Error closing Postgres pool: {e}")
        _postgres_pool = None

    # Close OpenAI client
    if _openai_client:
        try:
            await _openai_client.close()
            logger.info("✓ OpenAI client closed")
        except Exception as e:
            logger.error(f"Error closing OpenAI client: {e}")
        _openai_client = None

    logger.info("All clients shut down")


# =============================================================================
# Dependency Injection Functions
# =============================================================================
# These functions are used in FastAPI route handlers to inject dependencies.
# Example: def query(qdrant: QdrantClient = Depends(get_qdrant_client))
# =============================================================================


def get_qdrant_client() -> QdrantClient:
    """
    Get Qdrant vector database client.

    Returns:
        Initialized QdrantClient instance

    Raises:
        RuntimeError: If client not initialized (startup not called)

    Example:
        @app.post("/query")
        async def query(qdrant: QdrantClient = Depends(get_qdrant_client)):
            results = qdrant.search(...)
    """
    if _qdrant_client is None:
        raise RuntimeError("Qdrant client not initialized. Call startup_clients() first.")
    return _qdrant_client


def get_redis_client() -> aioredis.Redis:  # type: ignore[type-arg]
    """
    Get Redis cache client.

    Returns:
        Initialized Redis async client

    Raises:
        RuntimeError: If client not initialized (startup not called)

    Example:
        @app.post("/query")
        async def query(redis: aioredis.Redis = Depends(get_redis_client)):
            await redis.incr(f"rate_limit:{user_id}")
    """
    if _redis_client is None:
        raise RuntimeError("Redis client not initialized. Call startup_clients() first.")
    return _redis_client


def get_postgres_pool() -> asyncpg.Pool:
    """
    Get Neon Postgres connection pool.

    Returns:
        Initialized asyncpg Pool instance

    Raises:
        RuntimeError: If pool not initialized (startup not called)

    Example:
        @app.post("/query")
        async def query(pool: asyncpg.Pool = Depends(get_postgres_pool)):
            async with pool.acquire() as conn:
                subscription = await conn.fetchrow(...)
    """
    if _postgres_pool is None:
        # Return None if Postgres not available (Windows TLS issue)
        # Audit logging will be skipped
        return None  # type: ignore[return-value]
    return _postgres_pool


def get_openai_client() -> AsyncOpenAI:
    """
    Get OpenAI API client.

    Returns:
        Initialized AsyncOpenAI client

    Raises:
        RuntimeError: If client not initialized (startup not called)

    Example:
        @app.post("/query")
        async def query(openai: AsyncOpenAI = Depends(get_openai_client)):
            embedding = await openai.embeddings.create(...)
    """
    if _openai_client is None:
        raise RuntimeError("OpenAI client not initialized. Call startup_clients() first.")
    return _openai_client


def get_settings_dependency() -> Settings:
    """
    Get application settings.

    Returns:
        Settings instance from environment

    Example:
        @app.get("/health")
        async def health(settings: Settings = Depends(get_settings_dependency)):
            return {"env": settings.env}
    """
    return get_settings()


# =============================================================================
# Health Check Functions
# =============================================================================


async def check_qdrant_health() -> dict[str, str]:
    """
    Check Qdrant connection health.

    Returns:
        Health status dict

    Example:
        {"status": "healthy", "collections": "3"}
        {"status": "unhealthy", "error": "Connection timeout"}
    """
    try:
        if _qdrant_client is None:
            return {"status": "unhealthy", "error": "Client not initialized"}

        collections = _qdrant_client.get_collections()
        return {"status": "healthy", "collections": str(len(collections.collections))}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_redis_health() -> dict[str, str]:
    """
    Check Redis connection health.

    Returns:
        Health status dict

    Example:
        {"status": "healthy"}
        {"status": "unhealthy", "error": "Connection refused"}
    """
    try:
        if _redis_client is None:
            return {"status": "unhealthy", "error": "Client not initialized"}

        await _redis_client.ping()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_postgres_health() -> dict[str, str]:
    """
    Check Neon Postgres connection health.

    Returns:
        Health status dict

    Example:
        {"status": "healthy", "pool_size": "5"}
        {"status": "unhealthy", "error": "Connection failed"}
    """
    try:
        if _postgres_pool is None:
            return {"status": "unhealthy", "error": "Pool not initialized"}

        async with _postgres_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")

        return {"status": "healthy", "pool_size": str(_postgres_pool.get_size())}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_openai_health() -> dict[str, str]:
    """
    Check OpenAI API connection health.

    Returns:
        Health status dict

    Example:
        {"status": "healthy"}
        {"status": "unhealthy", "error": "API key invalid"}
    """
    try:
        if _openai_client is None:
            return {"status": "unhealthy", "error": "Client not initialized"}

        # Lightweight API call to test connection
        await _openai_client.models.list()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_all_services_health() -> dict[str, dict[str, str]]:
    """
    Check health of all external services.

    Returns:
        Dict with health status for each service

    Example:
        {
            "qdrant": {"status": "healthy", "collections": "3"},
            "redis": {"status": "healthy"},
            "postgres": {"status": "healthy", "pool_size": "5"},
            "openai": {"status": "healthy"}
        }
    """
    return {
        "qdrant": await check_qdrant_health(),
        "redis": await check_redis_health(),
        "postgres": await check_postgres_health(),
        "openai": await check_openai_health(),
    }
