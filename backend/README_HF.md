---
title: Physical AI Textbook RAG
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
---

# Physical AI Textbook - RAG Query Backend

Interactive RAG (Retrieval-Augmented Generation) system for querying the Physical AI & Humanoid Robotics textbook.

## Features

- 🔍 Semantic search across textbook chapters
- 🤖 AI-powered answers using GPT-4
- 📚 Source citations with confidence scores
- 🎯 Chapter-specific filtering

## API Access

This Space exposes a REST API at `/v1/query`:

```bash
curl -X POST https://YOUR-USERNAME-physical-ai-textbook-rag.hf.space/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "What are ROS 2 nodes?",
    "chapter_id": "ch-ros2-nodes",
    "user_id": "demo-user"
  }'
```

## Configuration

Set the following secrets in your Space settings:

- `OPENAI_API_KEY`: Your OpenAI API key
- `QDRANT_URL`: Qdrant cloud cluster URL
- `QDRANT_API_KEY`: Qdrant API key
- `NEON_CONNECTION_STRING`: PostgreSQL connection string (optional)

## Tech Stack

- FastAPI for REST API
- Gradio for web interface
- Qdrant for vector search
- OpenAI for embeddings & LLM
