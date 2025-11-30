# Testing the RAG Query Endpoint

This guide shows you how to test the RAG Pipeline Query Endpoint that we just built.

## Prerequisites

You'll need API keys for the following services:

### 1. **OpenAI API Key** (Required)
- Sign up at: https://platform.openai.com/signup
- Get API key: https://platform.openai.com/api-keys
- Cost: ~$0.01 per query (embedding + GPT-4 Turbo)
- **Needed for**: Query embeddings + Answer generation

### 2. **Qdrant Cloud** (Required)
- Sign up at: https://cloud.qdrant.io/
- Free tier: 1GB storage, 100K vectors
- Create a cluster and get API key
- **Needed for**: Vector search over textbook chunks

### 3. **Neon Postgres** (Required)
- Sign up at: https://neon.tech/
- Free tier: 3GB storage, 1 database
- Get connection string from dashboard
- **Needed for**: Subscription data + audit logs

### 4. **Redis** (Optional for now)
- Local: `docker run -d -p 6379:6379 redis:7-alpine`
- Or use Redis Cloud: https://redis.com/try-free/
- **Needed for**: Rate limiting (not yet implemented)

---

## Setup Steps

### Step 1: Copy .env.example to .env

```bash
cd backend
cp .env.example .env
```

### Step 2: Fill in your API keys in `.env`

```bash
# Open .env and add your real keys:
OPENAI_API_KEY=sk-proj-YOUR_REAL_OPENAI_KEY_HERE
QDRANT_URL=https://YOUR_CLUSTER.cloud.qdrant.io:6333
QDRANT_API_KEY=YOUR_QDRANT_API_KEY_HERE
NEON_CONNECTION_STRING=postgresql://user:password@YOUR_NEON_HOST/dbname?sslmode=require
BETTER_AUTH_SECRET=any-random-32-character-string-here-for-testing
REDIS_URL=redis://localhost:6379/0
```

### Step 3: Setup Database Schema

Run the Neon Postgres schema setup:

```bash
# Make sure you have psql installed, or use Neon's SQL Editor in the web UI
psql $NEON_CONNECTION_STRING -f scripts/setup_neon_schema.sql
```

Or copy the contents of `scripts/setup_neon_schema.sql` and paste into Neon's SQL Editor.

### Step 4: Setup Qdrant Collection

```bash
cd backend
python scripts/setup_qdrant_collection.py
```

This will create the `textbook-chapters` collection with proper configuration.

### Step 5: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
# Or if you have Poetry:
poetry install
```

If you don't have a requirements.txt, create one:

```bash
pip install fastapi uvicorn pydantic pydantic-settings qdrant-client openai python-jose asyncpg redis httpx python-dotenv prometheus-client tiktoken
```

---

## Running the API

### Option 1: Direct with Uvicorn

```bash
cd backend
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: With Docker Compose (if configured)

```bash
docker-compose up
```

The API will be available at: **http://localhost:8000**

---

## Testing the Endpoint

### 1. Check Health Endpoint

```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "qdrant": {"status": "healthy", "collections": "1"},
    "redis": {"status": "healthy"},
    "postgres": {"status": "healthy", "pool_size": "2"},
    "openai": {"status": "healthy"}
  }
}
```

If any service shows `"status": "unhealthy"`, check your API keys in `.env`.

### 2. View API Documentation

Open in browser: **http://localhost:8000/v1/docs**

This shows interactive Swagger UI where you can test the API visually.

### 3. Test Query Endpoint (Simple Test - Will Fail)

**Why it will fail**: We haven't ingested any textbook data yet, so Qdrant is empty!

```bash
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "What are ROS 2 nodes?",
    "chapter_id": "ch-ros2-fundamentals",
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Expected Response** (404 CONTEXT_NOT_FOUND):
```json
{
  "detail": {
    "error_code": "CONTEXT_NOT_FOUND",
    "message": "No relevant context found for the query",
    "details": {
      "chapter_id": "ch-ros2-fundamentals",
      "query_id": "qry-abc123..."
    }
  }
}
```

This is **CORRECT**! The endpoint works but there's no data in Qdrant yet.

---

## Adding Test Data to Qdrant

To properly test the endpoint, you need to add some textbook chunks to Qdrant.

### Quick Test: Add Sample Data Manually

Create a file `backend/scripts/add_test_data.py`:

```python
import os
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from openai import OpenAI

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

# Sample textbook content
sample_chunks = [
    {
        "chunk_id": "ch-ros2-fundamentals_chunk_0001",
        "content": "ROS 2 nodes are the fundamental building blocks of ROS applications. Each node is a process that performs computation. Nodes communicate with each other using topics, services, and actions.",
        "chapter_id": "ch-ros2-fundamentals",
        "page_number": 42,
        "section_title": "Understanding ROS 2 Nodes"
    },
    {
        "chunk_id": "ch-ros2-fundamentals_chunk_0002",
        "content": "Creating a ROS 2 node in Python requires importing the rclpy library and creating a class that inherits from Node. You then initialize the node and spin it to start processing callbacks.",
        "chapter_id": "ch-ros2-fundamentals",
        "page_number": 45,
        "section_title": "Creating Your First Node"
    },
]

# Generate embeddings and upload
points = []
for i, chunk in enumerate(sample_chunks):
    # Generate embedding
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=chunk["content"]
    )
    embedding = response.data[0].embedding

    # Create point
    point = PointStruct(
        id=i + 1,
        vector=embedding,
        payload=chunk
    )
    points.append(point)

# Upload to Qdrant
qdrant_client.upsert(
    collection_name="textbook-chapters",
    points=points
)

print(f"✅ Uploaded {len(points)} test chunks to Qdrant!")
```

Run it:

```bash
cd backend
python scripts/add_test_data.py
```

### Test Query Endpoint Again (Should Work Now!)

```bash
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "What are ROS 2 nodes?",
    "chapter_id": "ch-ros2-fundamentals",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "top_k": 2,
    "temperature": 0.7
  }'
```

**Expected Response** (200 OK):
```json
{
  "answer": "ROS 2 nodes are the fundamental building blocks of ROS applications. Each node is a process that performs computation. Nodes communicate with each other using topics, services, and actions.",
  "sources": [
    {
      "chunk_id": "ch-ros2-fundamentals_chunk_0001",
      "content": "ROS 2 nodes are the fundamental building blocks...",
      "similarity_score": 0.92,
      "page_number": 42,
      "section_title": "Understanding ROS 2 Nodes"
    },
    {
      "chunk_id": "ch-ros2-fundamentals_chunk_0002",
      "content": "Creating a ROS 2 node in Python requires...",
      "similarity_score": 0.78,
      "page_number": 45,
      "section_title": "Creating Your First Node"
    }
  ],
  "confidence_score": 0.85,
  "grounding_status": "fully_grounded",
  "query_id": "qry-a1b2c3d4e5f6...",
  "session_id": null,
  "processing_time_ms": 1847,
  "created_at": "2025-11-29T10:30:45.123Z",
  "metadata": {
    "model_version": "gpt-4-turbo-preview",
    "chunks_retrieved": 2,
    "llm_refusal": false,
    "tokens_used": 456
  }
}
```

---

## Troubleshooting

### "Qdrant client not initialized"
- Check `QDRANT_URL` and `QDRANT_API_KEY` in `.env`
- Verify Qdrant cluster is running (check Qdrant Cloud dashboard)

### "OpenAI client not initialized"
- Check `OPENAI_API_KEY` in `.env`
- Verify API key is valid: https://platform.openai.com/api-keys

### "Postgres pool not initialized"
- Check `NEON_CONNECTION_STRING` in `.env`
- Verify database exists and schema is created
- Run `setup_neon_schema.sql` if not done

### "CONTEXT_NOT_FOUND" error
- This means Qdrant has no data yet
- Run `add_test_data.py` to add sample chunks
- Or ingest real textbook content (Phase 7 task)

### Import errors
- Make sure you're in the `backend` directory
- Install all dependencies: `pip install -r requirements.txt`

---

## Monitoring & Metrics

### View Prometheus Metrics

```bash
curl http://localhost:8000/metrics
```

Shows metrics like:
- `rag_query_latency_seconds`: Query processing time
- `rag_grounding_quality_total`: Grounding status counts
- `rag_query_errors_total`: Error counts

### View Logs

Logs are printed to stdout in JSON format:

```json
{
  "timestamp": "2025-11-29T10:30:45.123Z",
  "level": "INFO",
  "message": "RAG query completed",
  "query_id": "qry-abc123...",
  "user_id_hash": "a1b2c3d4...",
  "chapter_id": "ch-ros2-fundamentals",
  "latency_ms": 1847,
  "grounding_status": "fully_grounded"
}
```

Note: `user_id_hash` is SHA-256 hash (privacy-compliant, no raw user_id).

---

## Next Steps

1. **Add More Test Data**: Create more sample chunks for testing
2. **Test Error Cases**: Try invalid chapter_id, empty query_text
3. **Implement Authentication**: Add JWT token validation (Phase 4)
4. **Add Rate Limiting**: Implement Redis-based rate limiting (Phase 6)
5. **Ingest Real Content**: Load actual textbook chapters (Phase 7)

---

## Cost Estimates

**Per Query** (~$0.01):
- Embedding generation: $0.0001 (1K tokens × $0.0001/1K)
- GPT-4 Turbo generation: $0.01 (200 output tokens × $0.03/1K + 500 input tokens × $0.01/1K)

**For Testing** (100 queries): ~$1.00

**Qdrant**: Free tier supports 100K vectors
**Neon**: Free tier supports 3GB storage
**Redis**: Free (local) or Redis Cloud free tier

---

## Summary

✅ **API is functional** if all health checks pass
✅ **Endpoint works** (returns 404 until you add data)
✅ **After adding test data**: Full RAG pipeline works!

The MVP is ready for testing! 🎉
