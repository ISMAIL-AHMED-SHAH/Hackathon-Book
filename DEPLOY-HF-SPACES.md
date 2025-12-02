# Hugging Face Spaces Deployment Guide

## Overview

The backend has been converted from Docker Compose to a single-container deployment compatible with Hugging Face Spaces.

## What Changed

### ✅ Fixed Issues

1. **No more Docker Compose** - Single Dockerfile that HF Spaces can build
2. **No Redis dependency** - Uses in-memory rate limiting (auto-fallback)
3. **No Gradio wrapper** - Direct FastAPI on port 7860
4. **No localhost URLs** - Proper HF Spaces configuration

### 🏗️ Architecture

```
HF Space Container
├── FastAPI (port 7860)
│   ├── POST /v1/query
│   ├── GET /health
│   └── GET /metrics
├── Qdrant Client (cloud)
├── OpenAI Client (API)
├── PostgreSQL Client (cloud, optional)
└── In-Memory Rate Limiter
```

## Deployment Steps

### 1. Deploy to Hugging Face Spaces

```bash
cd backend
bash ../deploy-to-hf.sh ismail-ahmed-shah humanoid-robotics YOUR_HF_TOKEN
```

Or manually:

```bash
cd backend
git init
git add .
git commit -m "Deploy RAG backend"
git remote add hf https://huggingface.co/spaces/ismail-ahmed-shah/humanoid-robotics
git push hf main --force
```

### 2. Configure Space Settings

Go to: https://huggingface.co/spaces/ismail-ahmed-shah/humanoid-robotics/settings

**SDK:** Docker

**Repository Secrets (Required):**
- `OPENAI_API_KEY` - Your OpenAI API key (sk-...)
- `QDRANT_URL` - Qdrant Cloud URL (https://...)
- `QDRANT_API_KEY` - Qdrant API key

**Repository Secrets (Optional):**
- `NEON_CONNECTION_STRING` - PostgreSQL for audit logs
- `ENV` - Set to "production"
- `LOG_LEVEL` - Set to "INFO"

### 3. Wait for Build

The Space will automatically build (3-5 minutes). Monitor at:
https://huggingface.co/spaces/ismail-ahmed-shah/humanoid-robotics

Check logs for:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7860
```

### 4. Verify Deployment

Test the health endpoint:

```bash
curl https://ismail-ahmed-shah-humanoid-robotics.hf.space/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "services": {
    "qdrant": {"status": "healthy", "collections": "1"},
    "redis": {"status": "healthy", "mode": "in-memory"},
    "postgres": {"status": "healthy"},
    "openai": {"status": "healthy"}
  }
}
```

Test the query endpoint:

```bash
curl -X POST https://ismail-ahmed-shah-humanoid-robotics.hf.space/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "What are ROS 2 nodes?",
    "chapter_id": null,
    "user_id": "guest-user"
  }'
```

## File Structure

```
backend/
├── Dockerfile              # HF Spaces Docker config
├── app.py                  # FastAPI entry point (port 7860)
├── requirements.txt        # Minimal production dependencies
├── README.md              # Deployment documentation
└── src/
    ├── api/
    │   ├── main.py        # FastAPI app
    │   ├── dependencies.py # DI with Redis fallback
    │   └── v1/query.py    # Query endpoint
    ├── services/
    │   └── in_memory_cache.py  # Redis replacement
    └── models/
        └── query.py       # Updated schema (optional chapter_id)
```

## Key Changes

### 1. Dockerfile

**Before (Docker Compose):**
```dockerfile
FROM python:3.11-slim as base
# Multi-stage with Poetry
# Separate dev/prod targets
```

**After (HF Spaces):**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY src/ ./src/
COPY app.py ./
EXPOSE 7860
CMD ["python", "app.py"]
```

### 2. app.py

**Before (Gradio Wrapper):**
```python
import gradio as gr
from src.api.main import app as fastapi_app

app = gr.mount_gradio_app(fastapi_app, demo, path="/")
uvicorn.run(app, port=7860)
```

**After (Direct FastAPI):**
```python
import uvicorn
from src.api.main import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### 3. dependencies.py

**Before (Redis Required):**
```python
from redis import asyncio as aioredis
_redis_client = await aioredis.from_url(url)
```

**After (Optional with Fallback):**
```python
try:
    from redis import asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

if REDIS_AVAILABLE:
    try:
        _redis_client = await aioredis.from_url(url)
    except:
        _in_memory_limiter = get_in_memory_limiter()
else:
    _in_memory_limiter = get_in_memory_limiter()
```

### 4. requirements.txt

**Before:**
```
redis>=5.0.0
gradio>=4.0.0
tiktoken>=0.5.2
python-jose[cryptography]>=3.3.0
opentelemetry-api>=1.21.0
# ... many dev dependencies
```

**After:**
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
qdrant-client>=1.7.0
openai>=1.6.0
asyncpg>=0.29.0
httpx>=0.25.0
python-dotenv>=1.0.0
prometheus-client>=0.19.0
```

## Troubleshooting

### Space Not Building

Check Logs tab for errors. Common issues:
- Missing secrets (OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY)
- Invalid Dockerfile syntax
- Missing dependencies in requirements.txt

### 500 Internal Server Error

Check application logs:
```bash
# In HF Spaces logs tab, look for:
ERROR: Qdrant client initialization failed
ERROR: OpenAI connection failed
```

Solutions:
- Verify secrets are set correctly
- Check Qdrant URL format (must start with https://)
- Verify OpenAI API key is valid

### Rate Limiting Issues

In-memory limiter only works for single instance. For multi-instance:
1. Add Redis to HF Spaces (not officially supported)
2. Use external Redis (Upstash, Redis Cloud)
3. Accept single-instance limitation

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `QDRANT_URL` | Yes | - | Qdrant Cloud URL |
| `QDRANT_API_KEY` | Yes | - | Qdrant API key |
| `NEON_CONNECTION_STRING` | No | - | PostgreSQL connection |
| `PORT` | No | 7860 | Server port |
| `HOST` | No | 0.0.0.0 | Server host |
| `ENV` | No | development | Environment |
| `LOG_LEVEL` | No | INFO | Logging level |
| `RATE_LIMIT_REQUESTS` | No | 10 | Max requests per window |
| `RATE_LIMIT_WINDOW_SECONDS` | No | 60 | Rate limit window |

## Next Steps

After successful deployment:

1. ✅ Verify all endpoints work
2. ✅ Load textbook data into Qdrant (separate ingestion process)
3. ✅ Test frontend connection
4. ✅ Monitor health endpoint
5. ✅ Set up error alerting (optional)

## Support

- HF Spaces Docs: https://huggingface.co/docs/hub/spaces
- FastAPI Docs: https://fastapi.tiangolo.com
- Qdrant Docs: https://qdrant.tech/documentation
