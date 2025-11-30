# Running the RAG Backend API

## Prerequisites Checklist

✅ All environment variables configured in `backend/.env`
✅ OpenAI API key active
✅ Qdrant Cloud collection created
✅ Neon Postgres database accessible
✅ Python 3.11+ installed

## Step 1: Install Dependencies

You have two options:

### Option A: Using pip (Simpler)

```bash
cd backend
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi uvicorn openai qdrant-client asyncpg...
```

### Option B: Using Poetry (Recommended)

If you have Poetry installed:

```bash
cd backend
poetry install
poetry shell  # Activate the virtual environment
```

**Don't have Poetry?** Install it first:
```bash
pip install poetry
```

## Step 2: Add Test Data to Qdrant

Before running the server, you need some test data in your Qdrant collection:

```bash
python scripts/add_test_data.py
```

**Expected output:**
```
✅ Successfully added 5 test chunks to Qdrant
Collection: textbook-chapters
Sample chunk IDs: ch-ros2-fundamentals_chunk_0001, ...
```

**What this does:**
- Generates embeddings for 5 sample ROS 2 text chunks
- Uploads them to your Qdrant collection
- Cost: ~$0.0001 (practically free)

**If you get an error:**
- `401 Unauthorized`: Check your `QDRANT_API_KEY` and `OPENAI_API_KEY`
- `Collection not found`: Run `python scripts/setup_qdrant_collection.py` first
- Connection timeout: Check your `QDRANT_URL`

## Step 3: Start the FastAPI Server

```bash
cd backend
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Step 4: Test in Browser

### Option A: Interactive API Documentation (Swagger UI)

1. **Open your browser** and navigate to:
   ```
   http://localhost:8000/docs
   ```

2. **You should see** the FastAPI automatic interactive documentation with:
   - Green "Query" section
   - POST `/v1/query` endpoint

3. **Click** on `POST /v1/query` to expand it

4. **Click** "Try it out" button (top right of the endpoint section)

5. **Replace the example request** with this test query:
   ```json
   {
     "query_text": "What are ROS 2 nodes?",
     "chapter_id": "ch-ros2-fundamentals",
     "user_id": "test-user-123",
     "top_k": 3,
     "temperature": 0.7
   }
   ```

6. **Click** the blue "Execute" button

7. **Expected Response** (200 OK):
   ```json
   {
     "query_id": "qry_abc123...",
     "answer": "ROS 2 nodes are the fundamental building blocks of a ROS 2 application...",
     "confidence_score": 0.856,
     "grounding_status": "FULLY_GROUNDED",
     "sources": [
       {
         "chunk_id": "ch-ros2-fundamentals_chunk_0001",
         "content": "ROS 2 nodes are the fundamental building blocks...",
         "similarity_score": 0.912,
         "page_number": 42,
         "section_title": "Understanding ROS 2 Nodes"
       },
       ...
     ],
     "metadata": {
       "model_used": "gpt-4-turbo-preview",
       "total_chunks_retrieved": 3,
       "processing_time_ms": 1247
     }
   }
   ```

### Option B: Using Browser Console (Fetch API)

1. **Open** http://localhost:8000/docs in your browser
2. **Press F12** to open Developer Tools
3. **Go to Console tab**
4. **Paste and run** this JavaScript:

```javascript
fetch('http://localhost:8000/v1/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query_text: "What are ROS 2 nodes?",
    chapter_id: "ch-ros2-fundamentals",
    user_id: "test-user-123",
    top_k: 3,
    temperature: 0.7
  })
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

5. **Check the console** for the response object

## Step 5: Verify It's Working

**Green flags (everything working):**
- ✅ Swagger UI loads at http://localhost:8000/docs
- ✅ GET http://localhost:8000/health returns `{"status":"healthy"}`
- ✅ POST /v1/query returns 200 with answer and sources
- ✅ Terminal shows INFO logs for each request

**Common Issues:**

### Issue 1: "Collection 'textbook-chapters' not found"
**Fix:**
```bash
python scripts/setup_qdrant_collection.py
python scripts/add_test_data.py
```

### Issue 2: "401 Unauthorized" from OpenAI
**Fix:**
- Check your `OPENAI_API_KEY` in `.env`
- Verify it starts with `sk-proj-`
- Check if you have credits: https://platform.openai.com/usage

### Issue 3: "404 CONTEXT_NOT_FOUND"
**Cause:** No matching chunks found in Qdrant for that chapter_id
**Fix:**
- Ensure `add_test_data.py` ran successfully
- Use `chapter_id: "ch-ros2-fundamentals"` (matches test data)
- Check Qdrant dashboard to verify chunks were uploaded

### Issue 4: "422 INSUFFICIENT_GROUNDING"
**Cause:** Confidence score < 0.3 or LLM refused to answer
**Fix:**
- This is expected behavior for off-topic questions
- Try questions related to ROS 2 (matches test data)
- Example: "What is a ROS 2 topic?" or "How do ROS 2 services work?"

### Issue 5: Server won't start - "Address already in use"
**Fix:**
```bash
# On Windows (PowerShell):
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# Or change the port:
uvicorn src.api.main:app --reload --port 8001
```

## Test Queries (Copy-Paste Ready)

**Query 1: ROS 2 Nodes**
```json
{
  "query_text": "What are ROS 2 nodes and how do they communicate?",
  "chapter_id": "ch-ros2-fundamentals",
  "user_id": "test-user-123"
}
```

**Query 2: ROS 2 Topics**
```json
{
  "query_text": "Explain ROS 2 topics and pub-sub pattern",
  "chapter_id": "ch-ros2-fundamentals",
  "user_id": "test-user-123"
}
```

**Query 3: ROS 2 Services**
```json
{
  "query_text": "What are ROS 2 services and when should I use them?",
  "chapter_id": "ch-ros2-fundamentals",
  "user_id": "test-user-123"
}
```

**Query 4: Should Fail (Off-topic)**
```json
{
  "query_text": "What is the capital of France?",
  "chapter_id": "ch-ros2-fundamentals",
  "user_id": "test-user-123"
}
```
**Expected:** 422 INSUFFICIENT_GROUNDING (LLM refuses off-topic question)

## Next Steps

Once the basic query is working:

1. **Test error cases** (see Query 4 above)
2. **Monitor costs** at https://platform.openai.com/usage
3. **Add more test data** by modifying `scripts/add_test_data.py`
4. **Implement authentication** (Phase 4 - JWT tokens)
5. **Add rate limiting** (Phase 6 - Redis)

## API Endpoint Reference

**Base URL:** http://localhost:8000

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API docs |
| `/v1/query` | POST | RAG query endpoint |

## Estimated Costs

- **Per query:** ~$0.01 USD
  - Embedding: $0.00001 (text-embedding-3-small)
  - LLM generation: $0.01 (gpt-4-turbo-preview)
- **100 test queries:** ~$1 USD
- **Qdrant:** Free tier (1GB storage)
- **Neon Postgres:** Free tier (0.5GB storage)

## Stopping the Server

Press **CTRL+C** in the terminal where uvicorn is running.

---

**Need help?** Check the detailed troubleshooting guide in `TESTING.md` or review logs in your terminal.
