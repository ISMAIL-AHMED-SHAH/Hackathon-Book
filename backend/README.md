# RAG Query Backend

Backend service for the Physical AI Textbook RAG (Retrieval-Augmented Generation) pipeline.

## Overview

This FastAPI backend provides an authenticated query endpoint that enables students to ask questions about Physical AI textbook chapters and receive AI-generated answers grounded in course content.

## Tech Stack

- **Python**: 3.11+
- **Framework**: FastAPI 0.104+
- **Database**: Neon Serverless Postgres (subscriptions, audit logs)
- **Vector DB**: Qdrant Cloud (embeddings storage)
- **LLM**: OpenAI GPT-4 Turbo
- **Authentication**: Better-Auth JWT validation
- **Rate Limiting**: Redis (sliding window)
- **Testing**: pytest, pytest-asyncio, pytest-cov

## Project Structure

```
backend/
├── src/
│   ├── api/              # FastAPI routes and endpoints
│   │   ├── main.py       # App initialization
│   │   ├── dependencies.py  # Dependency injection
│   │   └── v1/           # API version 1
│   │       └── query.py  # POST /api/v1/query
│   ├── models/           # Pydantic data models
│   │   ├── query.py      # QueryRequest, QueryResponse
│   │   ├── errors.py     # ErrorDetail, ErrorCode enum
│   │   └── user.py       # User, Subscription models
│   ├── services/         # Business logic
│   │   ├── auth.py       # JWT validation
│   │   ├── vector_search.py  # Qdrant client
│   │   ├── llm.py        # OpenAI client
│   │   ├── subscription.py   # Subscription checks
│   │   ├── rate_limiter.py   # Redis rate limiting
│   │   └── logging.py    # Structured logging
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings from .env
│   │   ├── exceptions.py # Custom exceptions
│   │   └── metrics.py    # Prometheus metrics
│   └── utils/            # Helper functions
│       └── sanitization.py  # Input sanitization
├── tests/
│   ├── contract/         # API contract tests
│   ├── integration/      # End-to-end tests
│   └── unit/             # Unit tests
├── scripts/
│   ├── setup_qdrant_collection.py  # Qdrant setup
│   ├── setup_neon_schema.sql       # Postgres schema
│   └── ingest_chapters.py          # Content ingestion
├── .env.example          # Environment variables template
├── pyproject.toml        # Poetry dependencies
└── README.md             # This file
```

## Getting Started

### Prerequisites

- Python 3.11+
- Poetry package manager
- Docker & Docker Compose (for local Redis)
- API keys for:
  - OpenAI (embeddings + LLM)
  - Qdrant Cloud
  - Neon Serverless Postgres
  - Better-Auth

### Installation

1. Clone the repository and navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies with Poetry:
   ```bash
   poetry install
   ```

3. Copy the environment template and fill in your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. Start local services (Redis):
   ```bash
   docker-compose up -d
   ```

### Running the Server

Start the FastAPI development server with hot-reload:

```bash
poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI)
- **Health**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics (Prometheus format)

### Running Tests

Execute the full test suite with coverage:

```bash
poetry run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

View the HTML coverage report:
```bash
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### Code Quality

Format code with Black:
```bash
poetry run black src/ tests/
```

Lint with Flake8:
```bash
poetry run flake8 src/ tests/
```

Type check with mypy:
```bash
poetry run mypy src/ --strict
```

## API Documentation

### POST /api/v1/query

Submit a textbook content query with chapter-scoped context retrieval.

**Request**:
```json
{
  "query_text": "What is a ROS 2 node?",
  "chapter_id": "ch-ros2-fundamentals",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "top_k": 5,
  "temperature": 0.7
}
```

**Response** (200 OK):
```json
{
  "answer": "A ROS 2 node is a fundamental building block...",
  "sources": [
    {
      "chunk_id": "ch-ros2-fundamentals_chunk_0042",
      "content": "ROS 2 nodes are...",
      "similarity_score": 0.87,
      "page_number": 42,
      "section_title": "Understanding ROS 2 Nodes"
    }
  ],
  "confidence_score": 0.87,
  "grounding_status": "fully_grounded",
  "query_id": "qry-1234567890abcdef",
  "processing_time_ms": 2340,
  "created_at": "2025-11-28T10:30:00Z"
}
```

See the [OpenAPI specification](../specs/001-rag-query-endpoint/contracts/query-endpoint.openapi.yaml) for complete documentation.

## Environment Variables

See `.env.example` for a complete list of required environment variables.

Key variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `QDRANT_URL`, `QDRANT_API_KEY`: Qdrant Cloud credentials
- `NEON_CONNECTION_STRING`: Neon Postgres connection string
- `BETTER_AUTH_SECRET`: JWT signing secret
- `REDIS_URL`: Redis connection URL
- `RATE_LIMIT_REQUESTS`: Max requests per user per minute (default: 10)

## Security

- Never commit the `.env` file (excluded in `.gitignore`)
- JWT tokens are validated using HS256 signature verification
- All user input is sanitized to prevent XSS/SQL injection
- Query text is never logged (PII compliance)
- User IDs in logs are SHA256 hashed

## Performance Targets

- **Latency**: p95 < 3s end-to-end
- **Throughput**: 100 QPS system-wide
- **Grounding Quality**: 95% of queries with confidence ≥ 0.5
- **Test Coverage**: ≥ 90%

## Monitoring

Prometheus metrics are exposed at `/metrics`:
- `rag_query_duration_seconds`: Query latency histogram
- `rag_grounding_status_total`: Grounding quality counter
- `rag_errors_total`: Error rate by type
- `rag_rate_limit_exceeded_total`: Rate limit violations

## License

See the main repository LICENSE file.
