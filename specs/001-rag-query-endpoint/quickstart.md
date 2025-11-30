# Quickstart Guide: RAG Pipeline Query Endpoint

**Feature**: RAG Pipeline Query Endpoint
**Date**: 2025-11-28
**Status**: Complete

## Prerequisites

- Python 3.11+
- OpenAI API key
- Qdrant Cloud account (free tier)
- Neon Serverless Postgres account (free tier)
- Better-Auth configured (see project-req.md)

---

## Step 1: Environment Setup

Create `.env` file in project root:

```bash
# OpenAI API
OPENAI_API_KEY=sk-proj-your-key-here

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-key

# Neon Postgres
NEON_CONNECTION_STRING=postgres://user:pass@ep-xyz.neon.tech/dbname

# Better-Auth
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_ISSUER=better-auth

# Redis (Upstash or local)
REDIS_URL=redis://localhost:6379/0

# Environment
ENV=development
LOG_LEVEL=DEBUG
```

---

## Step 2: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**requirements.txt**:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
qdrant-client==1.7.0
openai==1.6.1
python-jose[cryptography]==3.3.0
asyncpg==0.29.0
redis==5.0.1
httpx==0.25.2
python-dotenv==1.0.0
prometheus-client==0.19.0
tiktoken==0.5.2

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
mypy==1.7.1
black==23.12.0
flake8==6.1.0
```

---

## Step 3: Database Initialization

### 3.1 Neon Postgres Schema

Connect to Neon and run:

```sql
-- Subscriptions table
CREATE TABLE subscriptions (
    user_id UUID PRIMARY KEY,
    accessible_chapters TEXT[] NOT NULL,
    subscription_tier VARCHAR(50) NOT NULL,
    expiration_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_chapters ON subscriptions USING GIN (accessible_chapters);

-- Query audit log
CREATE TABLE query_audit_log (
    log_id BIGSERIAL PRIMARY KEY,
    query_id VARCHAR(36) UNIQUE NOT NULL,
    user_id_hash VARCHAR(64) NOT NULL,
    chapter_id VARCHAR(100) NOT NULL,
    status_code INTEGER NOT NULL,
    error_code VARCHAR(50),
    latency_ms INTEGER NOT NULL,
    confidence_score NUMERIC(3,2),
    grounding_status VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_user_hash ON query_audit_log(user_id_hash);
CREATE INDEX idx_audit_chapter ON query_audit_log(chapter_id);
CREATE INDEX idx_audit_created_at ON query_audit_log(created_at);

-- Insert test subscription
INSERT INTO subscriptions (user_id, accessible_chapters, subscription_tier)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    ARRAY['ch-ros2-fundamentals', 'ch-isaac-sim-intro', 'ch-gazebo-basics'],
    'premium'
);
```

### 3.2 Qdrant Collection

Run Python script to create collection:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, HnswConfigDiff
import os

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

client.create_collection(
    collection_name="textbook-chapters",
    vectors_config=VectorParams(
        size=1536,  # text-embedding-3-small dimensions
        distance=Distance.COSINE
    ),
    hnsw_config=HnswConfigDiff(
        m=16,
        ef_construction=100
    )
)

print("✅ Qdrant collection 'textbook-chapters' created")
```

---

## Step 4: Content Ingestion (Chapter Embedding)

Run ingestion script to chunk and embed chapters:

```python
import tiktoken
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import os
import hashlib

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
tokenizer = tiktoken.get_encoding("cl100k_base")

def chunk_text(text: str, chapter_id: str, chunk_size=512, overlap=64):
    """Chunk text into 512-token segments with 64-token overlap"""
    tokens = tokenizer.encode(text)
    chunks = []

    for i in range(0, len(tokens), chunk_size - overlap):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = tokenizer.decode(chunk_tokens)
        chunk_id = f"{chapter_id}_chunk_{len(chunks):04d}"

        chunks.append({
            "chunk_id": chunk_id,
            "content": chunk_text,
            "token_count": len(chunk_tokens)
        })

    return chunks

def embed_chunks(chunks):
    """Generate embeddings using OpenAI text-embedding-3-small"""
    texts = [chunk["content"] for chunk in chunks]

    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )

    for chunk, embedding_obj in zip(chunks, response.data):
        chunk["embedding"] = embedding_obj.embedding

    return chunks

def ingest_chapter(chapter_id: str, chapter_text: str):
    """Full ingestion pipeline: chunk → embed → upload"""
    print(f"Ingesting {chapter_id}...")

    # Step 1: Chunk
    chunks = chunk_text(chapter_text, chapter_id)
    print(f"  ✓ Created {len(chunks)} chunks")

    # Step 2: Embed
    chunks = embed_chunks(chunks)
    print(f"  ✓ Generated embeddings")

    # Step 3: Upload to Qdrant
    points = [
        PointStruct(
            id=hashlib.md5(chunk["chunk_id"].encode()).hexdigest()[:16],  # Unique ID
            vector=chunk["embedding"],
            payload={
                "chunk_id": chunk["chunk_id"],
                "chapter_id": chapter_id,
                "content": chunk["content"],
                "token_count": chunk["token_count"]
            }
        )
        for chunk in chunks
    ]

    qdrant_client.upsert(collection_name="textbook-chapters", points=points)
    print(f"  ✓ Uploaded {len(points)} vectors to Qdrant")

# Example: Ingest ROS 2 Fundamentals chapter
chapter_text = """
ROS 2 Fundamentals

ROS 2 nodes are the fundamental building blocks of ROS applications. A node is an executable that uses ROS 2 to communicate with other nodes. Nodes can publish messages to topics, subscribe to topics, provide services, or use action servers.

[... your full chapter content ...]
"""

ingest_chapter("ch-ros2-fundamentals", chapter_text)
```

---

## Step 5: Run FastAPI Server

```bash
cd backend
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Server starts at: `http://localhost:8000`

API docs available at: `http://localhost:8000/docs`

---

## Step 6: Test the Endpoint

### 6.1 Get Authentication Token

(Assuming Better-Auth is configured)

```bash
# Example: Login via Better-Auth
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "student@example.com", "password": "password123"}'

# Response includes JWT token
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {...}
}
```

### 6.2 Query the RAG Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "What is a ROS 2 node?",
    "chapter_id": "ch-ros2-fundamentals",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "top_k": 5,
    "temperature": 0.7
  }'
```

**Expected Response (200 OK)**:
```json
{
  "answer": "A ROS 2 node is an executable that uses ROS 2 to communicate with other nodes. Nodes are the fundamental building blocks of ROS applications and can publish messages to topics, subscribe to topics, provide services, or use action servers.",
  "sources": [
    {
      "chunk_id": "ch-ros2-fundamentals_chunk_0001",
      "content": "ROS 2 nodes are the fundamental building blocks of ROS applications...",
      "similarity_score": 0.87,
      "page_number": null,
      "section_title": null
    }
  ],
  "confidence_score": 0.87,
  "grounding_status": "fully_grounded",
  "query_id": "qry-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p",
  "session_id": null,
  "processing_time_ms": 1847,
  "created_at": "2025-11-28T15:30:45.123Z",
  "metadata": {
    "model_version": "gpt-4-turbo-preview",
    "chunks_retrieved": 5
  }
}
```

### 6.3 Test Error Scenarios

**Empty Query (400 QUERY_TEXT_EMPTY)**:
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Authorization: Bearer ..." \
  -H "Content-Type: application/json" \
  -d '{"query_text": "   ", "chapter_id": "ch-ros2-fundamentals", "user_id": "..."}'
```

**Expired Token (401 TOKEN_EXPIRED)**:
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Authorization: Bearer expired-token" \
  -H "Content-Type: application/json" \
  -d '{"query_text": "test", "chapter_id": "ch-ros2-fundamentals", "user_id": "..."}'
```

**Rate Limit (429 RATE_LIMIT_EXCEEDED)**:
```bash
# Send 11 requests within 60 seconds
for i in {1..11}; do
  curl -X POST http://localhost:8000/api/v1/query \
    -H "Authorization: Bearer ..." \
    -H "Content-Type: application/json" \
    -d '{"query_text": "test '$i'", "chapter_id": "ch-ros2-fundamentals", "user_id": "..."}'
done
```

---

## Step 7: Monitoring

### 7.1 Prometheus Metrics

Access metrics at: `http://localhost:8000/metrics`

**Key Metrics**:
- `rag_query_duration_seconds` (histogram): p50, p95, p99 latency
- `rag_grounding_status_total` (counter): Count by status
- `rag_errors_total` (counter): Count by error_code
- `rag_rate_limit_exceeded_total` (counter): Rate limit violations

### 7.2 Structured Logs

Logs in JSON format (stdout):

```json
{
  "timestamp": "2025-11-28T15:30:45.123Z",
  "level": "INFO",
  "query_id": "qry-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p",
  "user_id_hash": "5f4dcc3b...",
  "chapter_id": "ch-ros2-fundamentals",
  "status_code": 200,
  "latency_ms": 1847,
  "confidence_score": 0.87,
  "grounding_status": "fully_grounded"
}
```

---

## Step 8: Run Tests

```bash
# Run all tests with coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Expected: >= 90% coverage (constitution Rule II)

# Run type checking
mypy src/ --strict

# Run linter
flake8 src/

# Run formatter
black src/ --check
```

---

## Integration with Docusaurus Frontend

### Frontend Code Example

```typescript
// src/components/RAGChatbot.tsx
import React, { useState } from 'react';

interface RAGResponse {
  answer: string;
  sources: Array<{
    chunk_id: string;
    content: string;
    similarity_score: number;
  }>;
  confidence_score: number;
  grounding_status: string;
}

export function RAGChatbot({ chapterId }: { chapterId: string }) {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<RAGResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const userId = localStorage.getItem('user_id');

      const res = await fetch('http://localhost:8000/api/v1/query', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query_text: query,
          chapter_id: chapterId,
          user_id: userId,
          top_k: 5
        })
      });

      if (!res.ok) {
        const err = await res.json();
        setError(err.message);
        return;
      }

      const data = await res.json();
      setResponse(data);
      setError(null);
    } catch (err) {
      setError('Failed to query RAG endpoint');
    }
  };

  return (
    <div className="rag-chatbot">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question about this chapter..."
      />
      <button onClick={handleSubmit}>Ask</button>

      {response && (
        <div className="response">
          <p><strong>Answer:</strong> {response.answer}</p>
          <p><em>Confidence: {response.confidence_score.toFixed(2)} ({response.grounding_status})</em></p>
          <details>
            <summary>Sources ({response.sources.length})</summary>
            {response.sources.map((src, i) => (
              <div key={i}>
                <strong>Score: {src.similarity_score.toFixed(2)}</strong>
                <p>{src.content.substring(0, 200)}...</p>
              </div>
            ))}
          </details>
        </div>
      )}

      {error && <div className="error">{error}</div>}
    </div>
  );
}
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| 401 MISSING_TOKEN | No Authorization header | Add `Authorization: Bearer <token>` |
| 500 VECTOR_DB_ERROR | Qdrant connection failed | Check QDRANT_URL and QDRANT_API_KEY in .env |
| 500 LLM_SERVICE_ERROR | OpenAI API error | Check OPENAI_API_KEY, verify quota |
| 404 CONTEXT_NOT_FOUND | No embeddings for chapter | Run ingestion script for that chapter |
| High latency (>3s) | Slow vector search | Check Qdrant cluster status, reduce top_k |

---

## Next Steps

1. ✅ **Quickstart Complete**: Local development environment ready
2. → **Production Deployment**: Dockerize FastAPI app, deploy to cloud
3. → **Monitoring Setup**: Configure Grafana dashboards for Prometheus metrics
4. → **Content Ingestion Pipeline**: Automate chapter embedding on content updates
5. → **Frontend Integration**: Embed RAG chatbot in all Docusaurus chapters
