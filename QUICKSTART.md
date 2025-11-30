# Quick Start Guide - RAG Query Endpoint

Get the RAG endpoint running in **5 minutes**!

## Prerequisites

- Python 3.11+
- API keys (see below)

## Step 1: Get API Keys (5 minutes)

### OpenAI (Required - $5 free credit for new accounts)
1. Sign up: https://platform.openai.com/signup
2. Add payment method (required after free credit)
3. Create API key: https://platform.openai.com/api-keys
4. Copy the key starting with `sk-proj-...`

### Qdrant Cloud (Required - Free tier)
1. Sign up: https://cloud.qdrant.io/
2. Create a cluster (choose free tier)
3. Get cluster URL and API key from dashboard
4. URL looks like: `https://xyz-abc.cloud.qdrant.io:6333`

### Neon Postgres (Required - Free tier)
1. Sign up: https://neon.tech/
2. Create project (choose free tier)
3. Copy connection string from dashboard
4. Looks like: `postgresql://user:pass@ep-xyz.us-east-2.aws.neon.tech/dbname?sslmode=require`

## Step 2: Configure Environment (1 minute)

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your keys:
```bash
# Required - add your real keys:
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
QDRANT_URL=https://YOUR_CLUSTER.cloud.qdrant.io:6333
QDRANT_API_KEY=YOUR_KEY_HERE
NEON_CONNECTION_STRING=postgresql://user:pass@YOUR_HOST/dbname?sslmode=require

# Optional - use defaults:
BETTER_AUTH_SECRET=test-secret-key-32-characters-min
REDIS_URL=redis://localhost:6379/0
```

## Step 3: Setup Database (2 minutes)

### Option A: Using psql
```bash
psql $NEON_CONNECTION_STRING -f scripts/setup_neon_schema.sql
```

### Option B: Using Neon Web UI
1. Go to https://console.neon.tech/
2. Open SQL Editor
3. Copy contents of `backend/scripts/setup_neon_schema.sql`
4. Paste and run

## Step 4: Setup Qdrant Collection (1 minute)

```bash
cd backend
python scripts/setup_qdrant_collection.py
```

## Step 5: Install Dependencies (2 minutes)

```bash
cd backend
pip install fastapi uvicorn pydantic pydantic-settings qdrant-client openai python-jose asyncpg redis httpx python-dotenv prometheus-client tiktoken
```

## Step 6: Start API Server (30 seconds)

```bash
cd backend
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Server running at**: http://localhost:8000

## Step 7: Add Test Data (1 minute)

Open a new terminal:

```bash
cd backend
python scripts/add_test_data.py
```

This adds 5 sample chunks about ROS 2 to Qdrant.

## Step 8: Test It! (30 seconds)

### Option A: Using curl

```bash
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "What are ROS 2 nodes?",
    "chapter_id": "ch-ros2-fundamentals",
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### Option B: Using Swagger UI

Open browser: http://localhost:8000/v1/docs

1. Click on `POST /v1/query`
2. Click "Try it out"
3. Fill in the request:
```json
{
  "query_text": "What are ROS 2 nodes?",
  "chapter_id": "ch-ros2-fundamentals",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```
4. Click "Execute"

### Expected Response ✅

```json
{
  "answer": "ROS 2 nodes are the fundamental building blocks of ROS applications...",
  "sources": [
    {
      "chunk_id": "ch-ros2-fundamentals_chunk_0001",
      "content": "ROS 2 nodes are the fundamental building blocks...",
      "similarity_score": 0.92,
      "page_number": 42,
      "section_title": "Understanding ROS 2 Nodes"
    }
  ],
  "confidence_score": 0.85,
  "grounding_status": "fully_grounded",
  "query_id": "qry-abc123...",
  "processing_time_ms": 1847,
  "metadata": {
    "model_version": "gpt-4-turbo-preview",
    "chunks_retrieved": 2,
    "llm_refusal": false,
    "tokens_used": 456
  }
}
```

## ✅ Success!

Your RAG endpoint is working! You can now:

- **Try different queries**: "How do I create a ROS 2 node?", "What are ROS 2 topics?"
- **View metrics**: http://localhost:8000/metrics
- **Check health**: http://localhost:8000/health
- **View docs**: http://localhost:8000/v1/docs

## Troubleshooting

### "Qdrant client not initialized"
→ Check `QDRANT_URL` and `QDRANT_API_KEY` in `.env`

### "OpenAI client not initialized"
→ Check `OPENAI_API_KEY` in `.env`

### "404 CONTEXT_NOT_FOUND"
→ Run `python scripts/add_test_data.py` to add sample data

### Import errors
→ Make sure you're in `backend` directory when running commands

## What's Next?

See **TESTING.md** for:
- Detailed testing guide
- How to add more test data
- Understanding the response format
- Cost estimates
- Production deployment tips

---

**Total setup time**: ~12 minutes
**Cost for testing**: ~$0.50 for 50 test queries
