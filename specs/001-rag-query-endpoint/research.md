# Research & Technology Decisions: RAG Pipeline Query Endpoint

**Feature**: RAG Pipeline Query Endpoint
**Date**: 2025-11-28
**Status**: Complete

## Executive Summary

This document captures all architectural and technology decisions for the RAG Pipeline Query Endpoint, including rationale, alternatives considered, and tradeoffs. All decisions align with project requirements (Neon Postgres, Qdrant Cloud, OpenAI, Better-Auth, FastAPI) and constitution principles (type safety, 90% test coverage, standardized errors, secure credential management).

---

## Decision 1: Embedding Model

**Decision**: OpenAI `text-embedding-3-small` (1536 dimensions)

**Rationale**:
- **Cost-Effective**: $0.00002 per 1K tokens (vs $0.00013 for text-embedding-3-large)
- **Performance**: Sufficient for educational content retrieval (MTEB benchmark: 62.3% avg performance)
- **Compatibility**: Native integration with OpenAI SDK (same API as GPT models)
- **Dimension Size**: 1536 dimensions fit Qdrant Cloud Free Tier limits efficiently

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| text-embedding-3-large (3072 dims) | Higher accuracy (64.6% MTEB) | 6.5x more expensive, larger vector storage | Educational content doesn't require max accuracy; cost prohibitive for hackathon |
| text-embedding-ada-002 (1536 dims) | Same price as 3-small | Lower performance (61.0% MTEB), legacy model | Superseded by 3-small with better performance |
| Sentence-Transformers (e.g., all-MiniLM-L6-v2) | Free (self-hosted), faster inference | Requires separate infrastructure, lower quality embeddings | Adds deployment complexity; OpenAI requirement in project spec |

**Implementation Details**:
- Batch size: 100 chunks per embedding API call (rate limit: 3000 req/min)
- Retry logic: Exponential backoff for rate limit errors (429)
- Caching: Store embeddings in Qdrant with metadata (chapter_id, page_number, section_title)

---

## Decision 2: Chunk Strategy

**Decision**: 512 tokens per chunk with 64-token overlap

**Rationale**:
- **Context Window**: GPT-4 Turbo supports 128K tokens; 512-token chunks leave room for 5-10 chunks + system prompt
- **Overlap**: 64 tokens (~12.5% overlap) prevents information loss at chunk boundaries
- **Semantic Coherence**: 512 tokens (~380 words) typically captures complete paragraphs or subsections
- **Retrieval Precision**: Smaller chunks improve relevance matching vs. large chunks

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| 256 tokens, 32 overlap | Higher precision | Fragments sentences, requires more chunks for context | Trades precision for coherence; 256 tokens too small for educational explanations |
| 1024 tokens, 128 overlap | Better context per chunk | Lower retrieval precision, fewer chunks fit in LLM context | Educational queries need specific answers, not broad overviews |
| Sentence-based chunking | Natural boundaries | Variable chunk sizes complicate vector search | Sentences vary wildly (5-50 tokens); fixed size more predictable |

**Implementation Details**:
- Tokenizer: `tiktoken` with GPT-4 encoding (`cl100k_base`)
- Chunking Algorithm:
  ```
  1. Tokenize full chapter markdown
  2. Slide 512-token window with 64-token step (512 - 64 = 448-token stride)
  3. Extract metadata per chunk (page numbers from markdown headers, section titles)
  4. Generate chunk_id: `{chapter_id}_chunk_{index:04d}` (e.g., `ch-ros2-fundamentals_chunk_0042`)
  ```
- Metadata Extraction: Parse markdown headers (`##`, `###`) for section titles; infer page numbers from content structure

---

## Decision 3: LLM Model Selection

**Decision**: OpenAI `gpt-4-turbo-preview` (128K context, $0.01/1K input tokens, $0.03/1K output tokens)

**Rationale**:
- **Accuracy**: GPT-4 Turbo provides higher-quality answers for technical educational content (Physical AI, ROS 2, NVIDIA Isaac)
- **Context Window**: 128K tokens accommodates 5-10 chunks (512 tokens each) + system prompt + conversation history
- **Grounding Quality**: Better instruction-following for "refuse if context insufficient" system prompt
- **Cost-Acceptable**: For educational platform, quality > cost (hackathon context: ~$0.50 per 1000 queries assuming avg 200 tokens output)

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| gpt-3.5-turbo (16K context) | 10x cheaper ($0.001/1K input) | Lower accuracy, weaker instruction-following, smaller context | Educational content requires technical precision; 16K context too small for RAG |
| Claude 3 Sonnet (200K context) | Comparable accuracy, larger context | Not in project requirements (OpenAI specified) | Project explicitly requires OpenAI |
| Open-source (Llama 3, Mistral) | Free (self-hosted) | Requires GPU infrastructure, lower quality grounding | Adds deployment complexity; OpenAI requirement in spec |

**Implementation Details**:
- **System Prompt Template**:
  ```
  You are an expert tutor for a Physical AI & Humanoid Robotics course.
  Answer the student's question using ONLY the provided context chunks below.

  If the context does not contain sufficient information to answer accurately,
  respond with: "I don't have enough information in this chapter to answer that."

  Do not speculate or use knowledge outside the provided context.

  Context chunks:
  {chunks}

  Question: {query_text}
  ```
- **Temperature**: 0.7 (default), configurable via request parameter (0.0-1.0)
- **Max Tokens**: 1500 (limits response to ~750 words, prevents runaway costs)
- **Stop Sequences**: None (let model complete naturally)

---

## Decision 4: Rate Limiting Implementation

**Decision**: Redis-based rate limiting with sliding window algorithm

**Rationale**:
- **Scalability**: Redis supports distributed rate limiting across multiple FastAPI instances
- **Accuracy**: Sliding window prevents burst abuse (vs fixed window allowing 20 req in 2 minutes at window boundary)
- **Persistence**: Rate limit state survives FastAPI restarts
- **Low Latency**: Redis in-memory operations add <5ms overhead

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| In-memory (Python dict) | Zero external dependencies, faster | Doesn't scale beyond single instance, state lost on restart | Fails horizontal scaling requirement (100 QPS needs multiple instances) |
| Database-based (Neon Postgres) | No extra infrastructure | High latency (50-100ms per check), database load | Adds 50ms+ to p95 latency budget (3s total) |
| FastAPI middleware (slowapi) | Easy integration | Uses in-memory by default, limited customization | Doesn't support distributed deployments |

**Implementation Details**:
- **Algorithm**: Sliding window with Redis sorted sets
  ```python
  # Pseudo-code
  current_time = time.time()
  window_start = current_time - 60  # 60-second window

  # Remove old entries outside window
  redis.zremrangebyscore(f"ratelimit:{user_id}", 0, window_start)

  # Count requests in current window
  request_count = redis.zcard(f"ratelimit:{user_id}")

  if request_count >= 10:
      raise HTTPException(429, headers={"Retry-After": "60"})

  # Add current request
  redis.zadd(f"ratelimit:{user_id}", {current_time: current_time})
  redis.expire(f"ratelimit:{user_id}", 60)  # Auto-cleanup
  ```
- **Redis Configuration**: Upstash Redis Free Tier (10K requests/day sufficient for development/hackathon)
- **Fallback**: If Redis unavailable, allow requests (graceful degradation) and log warning

---

## Decision 5: Better-Auth JWT Integration

**Decision**: `python-jose[cryptography]` library for JWT validation with HS256 algorithm

**Rationale**:
- **Better-Auth Compatibility**: Better-Auth uses HS256 (HMAC-SHA256) by default for JWT signing
- **Standard Library**: python-jose is industry-standard for Python JWT handling (used by FastAPI docs)
- **Type Safety**: Integrates well with Pydantic for token payload validation
- **Performance**: HS256 is symmetric (faster than RSA), sufficient for server-to-server validation

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| PyJWT | More popular (10K+ GitHub stars) | Less FastAPI integration examples | python-jose has better FastAPI examples |
| authlib | Comprehensive OAuth support | Heavier dependency, overkill for JWT-only | We only need JWT validation, not full OAuth flow |
| RS256 (asymmetric) | Public/private key separation | Slower validation, Better-Auth default is HS256 | Better-Auth uses HS256; no need for public key distribution |

**Implementation Details**:
- **Token Claims Validation**:
  ```python
  # Expected JWT payload from Better-Auth
  {
    "sub": "550e8400-e29b-41d4-a716-446655440000",  # user_id (UUIDv4)
    "iss": "better-auth",                           # issuer
    "exp": 1735689600,                              # expiration (Unix timestamp)
    "iat": 1735686000,                              # issued at
    "aud": "physical-ai-platform",                  # audience
    "email": "student@example.com"                  # user email
  }
  ```
- **Validation Steps** (per FR-001):
  1. Extract token from `Authorization: Bearer <token>` header
  2. Decode JWT using `BETTER_AUTH_SECRET` from .env
  3. Verify signature (HS256 algorithm)
  4. Check `exp` claim > current time (not expired)
  5. Verify `iss` claim == "better-auth"
  6. Extract `sub` claim as user_id (validate UUIDv4 format)
- **Error Handling**:
  - Missing header → 401 MISSING_TOKEN
  - Invalid signature → 401 INVALID_TOKEN
  - Expired token → 401 TOKEN_EXPIRED

---

## Decision 6: Qdrant Collection Setup

**Decision**: Single collection `textbook-chapters` with HNSW indexing (M=16, ef_construction=100)

**Rationale**:
- **Single Collection**: All chapters in one collection simplifies management; filtering by `chapter_id` metadata
- **HNSW Index**: Qdrant's default; balances query speed (<100ms for top-10) with indexing time
- **M=16**: 16 bidirectional links per node; good recall/speed tradeoff for 2850 chunks
- **ef_construction=100**: Build-time exploration factor; higher = better recall during search

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| Separate collection per chapter | Isolation, easier deletion | 13 collections to manage, quota limits on free tier | Qdrant Free Tier limits collections; single collection with metadata filtering more efficient |
| Flat (brute-force) index | Perfect recall | Slow for >1000 vectors (O(n) search) | 2850 chunks would cause >500ms search latency |
| IVF (Inverted File) index | Faster than flat for huge datasets | Lower recall than HNSW, requires training | HNSW sufficient for 2850 chunks; IVF overkill |

**Implementation Details**:
- **Collection Config**:
  ```python
  from qdrant_client.models import Distance, VectorParams, HnswConfigDiff

  client.create_collection(
      collection_name="textbook-chapters",
      vectors_config=VectorParams(
          size=1536,  # text-embedding-3-small dimensions
          distance=Distance.COSINE  # Cosine similarity (range 0-1)
      ),
      hnsw_config=HnswConfigDiff(
          m=16,  # Max connections per node
          ef_construction=100  # Build-time exploration
      )
  )
  ```
- **Payload Schema** (metadata per vector):
  ```python
  {
      "chunk_id": "ch-ros2-fundamentals_chunk_0042",
      "chapter_id": "ch-ros2-fundamentals",
      "content": "ROS 2 nodes are the fundamental building blocks...",
      "page_number": 42,  # Optional
      "section_title": "Understanding ROS 2 Nodes",  # Optional
      "token_count": 487
  }
  ```
- **Search Query**:
  ```python
  results = client.search(
      collection_name="textbook-chapters",
      query_vector=embedding,  # 1536-dim vector from OpenAI
      query_filter={
          "must": [
              {"key": "chapter_id", "match": {"value": "ch-ros2-fundamentals"}}
          ]
      },
      limit=10,  # top_k parameter from request (default 5, max 10)
      score_threshold=0.3  # Minimum similarity (FR-003)
  )
  ```

---

## Decision 7: Neon Postgres Schema Design

**Decision**: Two tables - `subscriptions` and `query_audit_log`

**Rationale**:
- **Subscriptions Table**: Stores user chapter access permissions (checked per FR-012)
- **Audit Log Table**: Records all queries for compliance (90-day retention per spec assumptions)
- **Async Driver (asyncpg)**: Non-blocking database calls (compatible with FastAPI async endpoints)
- **Connection Pooling**: Reuse connections across requests (20-connection pool for 100 QPS)

**Schema**:
```sql
-- Subscriptions table (FR-012: authorization)
CREATE TABLE subscriptions (
    user_id UUID PRIMARY KEY,
    accessible_chapters TEXT[] NOT NULL,  -- Array of chapter_ids
    subscription_tier VARCHAR(50) NOT NULL,  -- 'free', 'premium', 'enterprise'
    expiration_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast chapter access lookups
CREATE INDEX idx_subscriptions_chapters ON subscriptions USING GIN (accessible_chapters);

-- Query audit log (FR-016: structured logging + compliance)
CREATE TABLE query_audit_log (
    log_id BIGSERIAL PRIMARY KEY,
    query_id VARCHAR(36) UNIQUE NOT NULL,  -- UUID from response
    user_id_hash VARCHAR(64) NOT NULL,  -- SHA256 hash (no PII)
    chapter_id VARCHAR(100) NOT NULL,
    status_code INTEGER NOT NULL,
    error_code VARCHAR(50),  -- NULL for 200 OK
    latency_ms INTEGER NOT NULL,
    confidence_score NUMERIC(3,2),  -- 0.00-1.00
    grounding_status VARCHAR(20),  -- 'fully_grounded', 'partially_grounded', 'speculative'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for analytics queries
CREATE INDEX idx_audit_user_hash ON query_audit_log(user_id_hash);
CREATE INDEX idx_audit_chapter ON query_audit_log(chapter_id);
CREATE INDEX idx_audit_created_at ON query_audit_log(created_at);

-- Partition by month for 90-day retention (auto-cleanup)
CREATE TABLE query_audit_log_2025_11 PARTITION OF query_audit_log
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
```

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| Store query_text in audit log | Full query history for analysis | Violates FR-016 (no PII in logs) | Constitution explicitly prohibits PII logging |
| Use Redis for audit logs | Faster writes | No persistence guarantees, limited querying | Audit logs require 90-day retention and SQL analytics |
| Single table with JSONB subscriptions | Flexible schema | Slower queries, harder to index | Array GIN index on TEXT[] is faster for "chapter IN accessible_chapters" checks |

**Implementation Details**:
- **Connection Pool**: asyncpg pool with min_size=5, max_size=20
- **Query Optimization**: Prepared statements for subscription checks (10ms p50 latency)
- **Retention Policy**: Automated partition drop after 90 days (cron job or pg_cron extension)

---

## Decision 8: Observability Stack

**Decision**: Prometheus metrics + OpenTelemetry structured logging + FastAPI middleware

**Rationale**:
- **Prometheus**: Industry standard for metrics scraping (integrates with Grafana for dashboards)
- **OpenTelemetry**: Vendor-neutral structured logging (JSON format) compatible with multiple backends
- **FastAPI Middleware**: Automatic request/response instrumentation

**Metrics Exposed** (per FR-017):
```python
from prometheus_client import Histogram, Counter, Gauge

# Latency percentiles (p50, p95, p99)
query_latency = Histogram(
    'rag_query_duration_seconds',
    'RAG query latency in seconds',
    buckets=[0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
)

# Grounding quality rate
grounding_quality = Counter(
    'rag_grounding_status_total',
    'Count of queries by grounding status',
    ['status']  # Labels: fully_grounded, partially_grounded, speculative
)

# Error rate by type
error_count = Counter(
    'rag_errors_total',
    'Count of errors by error code',
    ['error_code', 'status_code']
)

# Rate limit hits
rate_limit_hits = Counter(
    'rag_rate_limit_exceeded_total',
    'Number of rate limit violations',
    ['user_id']  # Note: hashed user_id for privacy
)

# Active requests
active_requests = Gauge(
    'rag_active_requests',
    'Number of in-flight requests'
)
```

**Structured Logging Format** (FR-016):
```json
{
  "timestamp": "2025-11-28T15:30:45.123Z",
  "level": "INFO",
  "query_id": "qry-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p",
  "user_id_hash": "5f4dcc3b5aa765d61d8327deb882cf99",
  "chapter_id": "ch-ros2-fundamentals",
  "status_code": 200,
  "latency_ms": 1847,
  "confidence_score": 0.78,
  "grounding_status": "fully_grounded",
  "error_code": null,
  "request_id": "req-a1b2c3d4"
}
```

**Alternatives Considered**:
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| StatsD + Graphite | Simpler setup | Less powerful querying than PromQL | Prometheus is industry standard with better ecosystem |
| CloudWatch Logs (AWS) | Managed service | Vendor lock-in, higher cost | Hackathon should be cloud-agnostic |
| ELK Stack (Elasticsearch) | Powerful log search | Heavy infrastructure, overkill | Structured logs + Prometheus sufficient for hackathon scope |

---

## Decision 9: Development Environment

**Decision**: Docker Compose for local development with `.env` file for secrets

**Rationale**:
- **Reproducibility**: All developers get identical environment (Python 3.11, Redis, mocked services)
- **Fast Iteration**: Hot-reload with uvicorn --reload
- **Secret Management**: .env file (excluded from Git) loaded via python-dotenv

**Docker Compose Services**:
```yaml
version: '3.9'
services:
  fastapi:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./backend:/app  # Hot-reload
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # Note: Qdrant and Neon are cloud services (not containerized locally)
```

**.env Template**:
```bash
# OpenAI API
OPENAI_API_KEY=sk-proj-...

# Qdrant Cloud
QDRANT_URL=https://xyz.qdrant.io
QDRANT_API_KEY=...

# Neon Postgres
NEON_CONNECTION_STRING=postgres://user:pass@ep-xyz.neon.tech/dbname

# Better-Auth
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_ISSUER=better-auth

# Redis (local development)
REDIS_URL=redis://redis:6379/0

# Environment
ENV=development
LOG_LEVEL=DEBUG
```

---

## Summary of Architectural Decisions

| Decision | Choice | Key Tradeoff | ADR Needed? |
|----------|--------|--------------|-------------|
| Embedding Model | OpenAI text-embedding-3-small | Cost vs accuracy | No (clear winner) |
| Chunk Strategy | 512 tokens, 64 overlap | Precision vs coherence | No (standard practice) |
| LLM Model | GPT-4 Turbo | Cost vs quality | **Yes** (significant cost impact) |
| Rate Limiting | Redis sliding window | Complexity vs accuracy | **Yes** (scalability critical) |
| JWT Validation | python-jose HS256 | Speed vs security | No (Better-Auth default) |
| Vector Index | Qdrant HNSW (M=16) | Recall vs speed | No (Qdrant recommendation) |
| Database Schema | Postgres with arrays | Normalization vs performance | No (2-table design is simple) |
| Observability | Prometheus + OTel | Setup complexity vs insight | No (industry standard) |

**Recommended ADRs**:
1. **ADR-001**: LLM Model Selection (GPT-4 Turbo vs GPT-3.5 Turbo)
2. **ADR-002**: Rate Limiting Architecture (Redis vs In-Memory vs Database)

---

## Next Steps

1. ✅ **Research Complete**: All technology decisions documented
2. → **Phase 1**: Create data-model.md with Pydantic schemas
3. → **Phase 1**: Generate API contracts (OpenAPI specs)
4. → **Phase 1**: Write quickstart.md with setup instructions
5. → **Phase 2**: Generate tasks.md from plan.md (/sp.tasks command)
