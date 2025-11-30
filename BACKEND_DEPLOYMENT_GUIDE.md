# Backend Deployment Guide

Complete guide to deploy the RAG backend and make the chatbot functional on your deployed site.

## Prerequisites

Before deploying, you'll need API keys for these services:

### Required Services (Free Tiers Available)

1. **OpenAI API** - For embeddings and LLM
   - Sign up: https://platform.openai.com/signup
   - Get API key: https://platform.openai.com/api-keys
   - Cost: ~$0.01-0.10 per query (pay-as-you-go)

2. **Qdrant Cloud** - Vector database for embeddings
   - Sign up: https://cloud.qdrant.io/
   - Free tier: 1GB cluster (sufficient for textbook)
   - Get cluster URL and API key from dashboard

3. **Upstash Redis** - For rate limiting (alternative to local Redis)
   - Sign up: https://upstash.com/
   - Free tier: 10,000 commands/day
   - Get Redis URL from dashboard

4. **Neon Postgres** - Serverless database (optional for hackathon)
   - Sign up: https://neon.tech/
   - Free tier: 0.5GB storage
   - Get connection string from dashboard
   - **NOTE**: Can be disabled for MVP (see below)

---

## Deployment Options

Choose one based on your preference:

### Option 1: Railway (Recommended - Easiest)
- ✅ Free $5/month credit
- ✅ Auto-deploy from GitHub
- ✅ Built-in environment variables
- ✅ Custom domains
- ⏱️ 5-10 minutes setup

### Option 2: Render
- ✅ Completely free tier
- ✅ Auto-deploy from GitHub
- ✅ Slower cold starts (free tier)
- ⏱️ 10-15 minutes setup

### Option 3: Fly.io
- ✅ Free tier: 3 shared VMs
- ⚠️ Requires credit card
- ⏱️ 15-20 minutes setup

---

## OPTION 1: Deploy to Railway (Recommended)

### Step 1: Prepare Backend Code

First, let's simplify the backend for MVP by making optional services truly optional.

Create a file `backend/src/core/config_simple.py`:

```python
"""Simplified configuration for hackathon deployment."""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Required: OpenAI
    openai_api_key: str
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4-turbo-preview"

    # Required: Qdrant
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "textbook-chapters"

    # Optional: Redis (disable rate limiting if not provided)
    redis_url: str = ""

    # Optional: Postgres (skip subscription checks if not provided)
    neon_connection_string: str = ""

    # Optional: Auth (allow guest users only if not provided)
    better_auth_secret: str = "hackathon-demo-secret-key-12345678"
    better_auth_issuer: str = "better-auth"

    # Rate limiting (disabled if no Redis)
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Timeouts
    vector_db_timeout: int = 5
    llm_timeout: int = 25
    total_timeout: int = 30

    # Application
    env: str = "production"
    log_level: str = "INFO"
    debug: bool = False
    api_version: str = "v1"

    # CORS
    cors_origins: List[str] = ["*"]

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False
```

### Step 2: Create Railway Account & Project

1. Go to https://railway.app/
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Authorize Railway to access your repository
6. Select `hackathon-book` repository

### Step 3: Configure Railway

In Railway dashboard:

1. **Root Directory**: Set to `backend`
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
4. **Healthcheck Path**: `/health`

### Step 4: Add Environment Variables

In Railway → Variables tab, add:

```bash
# Required - OpenAI
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Required - Qdrant
QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key

# Optional - Redis (Upstash)
REDIS_URL=redis://default:password@url.upstash.io:port

# Application
ENV=production
LOG_LEVEL=INFO
DEBUG=false
PORT=8000
```

### Step 5: Setup Qdrant Collection

Before deploying, you need to populate Qdrant with your textbook content.

**Run locally** (one-time setup):

```bash
cd backend

# Set environment variables
export OPENAI_API_KEY=your-key
export QDRANT_URL=your-url
export QDRANT_API_KEY=your-key

# Create collection
python scripts/setup_qdrant_collection.py

# Ingest textbook chapters (if you have a script)
# python scripts/ingest_chapters.py
```

**Note**: If you don't have chapter ingestion ready, you can manually create test data:

```bash
python scripts/add_test_data_http.py
```

### Step 6: Deploy

1. Railway will auto-deploy when you push to GitHub
2. Or click "Deploy Now" in Railway dashboard
3. Wait 2-3 minutes for deployment
4. Railway will provide a URL like: `https://your-app.railway.app`

### Step 7: Test Backend

```bash
# Health check
curl https://your-app.railway.app/health

# Test query
curl -X POST https://your-app.railway.app/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "What are ROS 2 nodes?",
    "chapter_id": "ch-ros2-nodes",
    "user_id": "guest-user"
  }'
```

### Step 8: Update Frontend

Update `frontend/.env.production`:

```bash
REACT_APP_API_URL=https://your-app.railway.app
REACT_APP_API_TIMEOUT=10000
```

### Step 9: Redeploy Frontend

Commit and push to trigger GitHub Actions:

```bash
git add frontend/.env.production
git commit -m "Update production API URL to Railway backend"
git push
```

Wait for GitHub Actions to complete (~2-3 minutes).

### Step 10: Test Live Site

Visit: https://ismail-ahmed-shah.github.io/Hackathon-Book/docs/intro

1. Click chatbot widget (💬 icon)
2. Ask: "What are ROS 2 nodes?"
3. You should receive an AI-generated answer with source citations!

---

## OPTION 2: Deploy to Render

### Step 1: Create Render Account

1. Go to https://render.com/
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Select `hackathon-book`

### Step 2: Configure Service

- **Name**: `hackathon-rag-backend`
- **Region**: Oregon (US West) - closest to free Qdrant
- **Branch**: `main` or your current branch
- **Root Directory**: `backend`
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
- **Instance Type**: Free

### Step 3: Add Environment Variables

In Render dashboard → Environment:

```bash
OPENAI_API_KEY=sk-proj-your-key
QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333
QDRANT_API_KEY=your-key
REDIS_URL=redis://...
ENV=production
LOG_LEVEL=INFO
PORT=10000
```

### Step 4: Deploy

Click "Create Web Service" - Render will auto-deploy.

**Note**: Free tier has cold starts (~30s delay if inactive for 15 minutes).

Your URL: `https://hackathon-rag-backend.onrender.com`

Then follow steps 5-10 from Railway guide above.

---

## OPTION 3: Deploy to Fly.io

### Step 1: Install Fly CLI

```bash
# Windows
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# Mac/Linux
curl -L https://fly.io/install.sh | sh
```

### Step 2: Login & Launch

```bash
cd backend
fly auth login
fly launch
```

Follow prompts:
- App name: `hackathon-rag-backend`
- Region: Choose closest to you
- Database: No
- Deploy now: No

### Step 3: Configure fly.toml

Edit `backend/fly.toml`:

```toml
app = "hackathon-rag-backend"
primary_region = "sea"

[build]
  dockerfile = "Dockerfile"

[env]
  ENV = "production"
  LOG_LEVEL = "INFO"
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  timeout = "5s"
  path = "/health"
```

### Step 4: Set Secrets

```bash
fly secrets set OPENAI_API_KEY=sk-proj-your-key
fly secrets set QDRANT_URL=https://your-url
fly secrets set QDRANT_API_KEY=your-key
fly secrets set REDIS_URL=redis://...
```

### Step 5: Deploy

```bash
fly deploy
```

Your URL: `https://hackathon-rag-backend.fly.dev`

Then follow steps 7-10 from Railway guide.

---

## Minimal Viable Backend (No External Services)

If you want to test WITHOUT setting up Qdrant/Redis/etc., you can create a mock backend:

### Quick Mock API

Create `backend/mock_server.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query_text: str
    chapter_id: str | None = None
    user_id: str

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/v1/query")
def query(req: QueryRequest):
    return {
        "answer": f"Mock answer for: {req.query_text}. This is a demo response showing the chatbot UI works. Deploy the real backend to get AI-powered answers from your textbook content.",
        "sources": [
            {
                "chunk_id": "demo-chunk-1",
                "content_excerpt": "This is a mock source citation to demonstrate the UI.",
                "similarity_score": 0.85,
                "section_title": "Demo Section",
            }
        ],
        "confidence_score": 0.85,
        "grounding_status": "mock",
        "query_id": "demo-query-123",
        "processing_time_ms": 100,
        "created_at": "2025-11-30T00:00:00Z",
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Deploy this to Railway/Render (no external services needed) to test the UI.

---

## Troubleshooting

### Issue: Railway/Render deployment fails

**Solution**: Check logs in dashboard. Common issues:
- Missing `requirements.txt`
- Wrong Python version (must be 3.11+)
- Missing environment variables

### Issue: Chatbot shows CORS error

**Solution**: Verify `cors_origins` in backend config includes your frontend domain:

```python
cors_origins: List[str] = [
    "https://ismail-ahmed-shah.github.io",
    "http://localhost:3000",  # For local testing
]
```

### Issue: Queries timeout

**Solution**:
- Increase `TOTAL_TIMEOUT` to 60 seconds
- Check Qdrant cluster is running
- Verify OpenAI API key is valid

### Issue: "Service temporarily unavailable"

**Solution**:
- Check Railway/Render logs for errors
- Verify all required env vars are set
- Test `/health` endpoint directly

---

## Cost Estimates

### Free Tier (Sufficient for Hackathon Demo)

- **Railway**: $5 credit/month (FREE)
- **Render**: Free tier (with cold starts)
- **Qdrant Cloud**: 1GB free cluster
- **Upstash Redis**: 10K commands/day free
- **OpenAI**: Pay-as-you-go (~$1-5 for 100 queries)

**Total**: $0-5/month for demo

### Production Scale (100 users/day)

- **Railway**: ~$10/month
- **Qdrant**: Free tier sufficient
- **Redis**: Free tier sufficient
- **OpenAI**: ~$20-50/month

**Total**: ~$30-60/month

---

## Next Steps After Deployment

Once backend is deployed:

1. ✅ Test chatbot on live site
2. ✅ Monitor `/metrics` endpoint for performance
3. ✅ Check `/health` for service status
4. ⏭️ Complete remaining frontend tasks (text selection, polish)
5. ⏭️ Add real textbook content to Qdrant
6. ⏭️ Improve prompts for better answers

---

## Questions?

Common next actions:
- Need help setting up Qdrant collection?
- Want to add authentication?
- Need to ingest textbook chapters?
- Want monitoring/analytics?

Let me know which deployment option you chose and I can provide specific help!
