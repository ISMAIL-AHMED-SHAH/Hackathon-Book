# Physical AI Textbook - RAG Backend API

FastAPI backend for the Physical AI & Humanoid Robotics interactive textbook.

## Features

- 🔍 Semantic search across textbook chapters using Qdrant vector database
- 🤖 AI-powered answers using OpenAI GPT-4
- 📚 Source citations with confidence scores
- 🎯 Chapter-specific filtering
- 🚀 Production-ready with monitoring and health checks

## API Endpoints

### Query Endpoint
```bash
POST /v1/query
Content-Type: application/json

{
  "query_text": "What are ROS 2 nodes?",
  "chapter_id": null,
  "user_id": "guest-user"
}
```

### Health Check
```bash
GET /health
```

### Metrics
```bash
GET /metrics
```

## Deployment on Hugging Face Spaces

This backend is designed to run on Hugging Face Spaces using Docker.

### Required Secrets

Set these in your HF Space settings under "Repository secrets":

- `OPENAI_API_KEY` - Your OpenAI API key
- `QDRANT_URL` - Qdrant Cloud cluster URL
- `QDRANT_API_KEY` - Qdrant API key
- `NEON_CONNECTION_STRING` - PostgreSQL connection string (optional)

### Configuration

The backend uses environment variables for configuration:

- `PORT` - Server port (default: 7860 for HF Spaces)
- `HOST` - Server host (default: 0.0.0.0)
- `ENV` - Environment (development/production)
- `LOG_LEVEL` - Logging level (INFO/DEBUG/WARNING)

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="sk-..."
export QDRANT_URL="https://..."
export QDRANT_API_KEY="..."
export NEON_CONNECTION_STRING="postgresql://..."

# Run locally
python app.py
```

The API will be available at http://localhost:7860

### Architecture

- **FastAPI**: Web framework for API endpoints
- **Qdrant**: Vector database for semantic search
- **OpenAI**: Embeddings and LLM for RAG pipeline
- **PostgreSQL (Neon)**: Audit logging and analytics (optional)
- **In-Memory Cache**: Rate limiting (Redis fallback)

### Rate Limiting

The backend includes built-in rate limiting:
- Uses in-memory cache by default (suitable for single-instance deployments)
- Automatically falls back if Redis is unavailable
- Default: 10 requests per 60 seconds per user

### Health Monitoring

The `/health` endpoint provides status for all services:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "services": {
    "qdrant": {"status": "healthy", "collections": "1"},
    "redis": {"status": "healthy", "mode": "in-memory"},
    "postgres": {"status": "healthy", "pool_size": "5"},
    "openai": {"status": "healthy"}
  }
}
```

## Tech Stack

- FastAPI 0.104+
- Python 3.11
- Qdrant for vector search
- OpenAI GPT-4 for LLM
- Pydantic for validation
- Prometheus for metrics

## License

MIT
