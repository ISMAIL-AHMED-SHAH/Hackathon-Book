# Error Taxonomy: RAG Pipeline Query Endpoint

**Feature**: RAG Pipeline Query Endpoint
**Date**: 2025-11-28
**Status**: Complete

## Overview

Complete error code reference for POST /api/v1/query endpoint. All errors return standardized JSON format per FR-010 and constitution Rule III.

---

## Error Response Format

**Standard Structure**:
```json
{
  "error_code": "ERROR_CODE_ENUM",
  "message": "Human-readable description",
  "field": "field_name_if_applicable",
  "details": {  // Optional
    "additional": "context"
  },
  "request_id": "req-unique-id"
}
```

---

## Error Catalog

### 400 Bad Request - Client Input Errors

| Code | HTTP | Message | Field | When | Resolution |
|------|------|---------|-------|------|------------|
| `INVALID_INPUT` | 400 | Request validation failed | varies | Pydantic validation error | Fix request format per schema |
| `QUERY_TEXT_EMPTY` | 400 | Query text cannot be empty or whitespace | query_text | Empty/whitespace query | Provide non-empty query |
| `INVALID_CHAPTER_ID` | 400 | Chapter ID format is invalid (expected: ch-{slug}) | chapter_id | Malformed chapter_id | Use pattern ^ch-[a-z0-9-]{3,50}$ |
| `INVALID_USER_ID` | 400 | User ID must be a valid UUIDv4 | user_id | Non-UUID format | Provide valid UUIDv4 |
| `INVALID_SESSION_ID` | 400 | Session ID format is invalid | session_id | Malformed session_id | Use pattern ^sess-[a-f0-9]{32}$ |

### 401 Unauthorized - Authentication Failures

| Code | HTTP | Message | Field | When | Resolution |
|------|------|---------|-------|------|------------|
| `MISSING_TOKEN` | 401 | Authorization header with Bearer token is required | null | No Authorization header | Add `Authorization: Bearer <token>` |
| `INVALID_TOKEN` | 401 | Bearer token is invalid or malformed | null | JWT signature invalid | Re-authenticate with Better-Auth |
| `TOKEN_EXPIRED` | 401 | Bearer token has expired | null | JWT exp claim past | Refresh authentication token |

### 403 Forbidden - Authorization Failures

| Code | HTTP | Message | Field | When | Resolution |
|------|------|---------|-------|------|------------|
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks access to requested resource | null | Generic authZ failure | Contact administrator |
| `CHAPTER_ACCESS_DENIED` | 403 | User subscription does not include this chapter | chapter_id | User not subscribed to chapter | Upgrade subscription |

### 404 Not Found - Resource Missing

| Code | HTTP | Message | Field | When | Resolution |
|------|------|---------|-------|------|------------|
| `CHAPTER_NOT_FOUND` | 404 | Requested chapter does not exist in the textbook | chapter_id | Invalid chapter_id | Check available chapters |
| `CONTEXT_NOT_FOUND` | 404 | No relevant context found in chapter for this query (try broader terms) | null | All chunks < 0.3 similarity (FR-008) | Rephrase query with broader terms |

### 422 Unprocessable Entity - Business Logic Failures

| Code | HTTP | Message | Field | When | Resolution |
|------|------|---------|-------|------|------------|
| `INSUFFICIENT_GROUNDING` | 422 | Cannot generate grounded answer from available context (confidence < threshold) | null | confidence_score < 0.3 after LLM gen (FR-009) | Try different chapter or rephrase |
| `QUERY_TOO_BROAD` | 422 | Query is too broad or ambiguous - please be more specific | query_text | Semantic ambiguity detected | Add specificity to question |

### 429 Too Many Requests - Rate Limiting

| Code | HTTP | Message | Field | When | Resolution | Headers |
|------|------|---------|-------|------|------------|---------|
| `RATE_LIMIT_EXCEEDED` | 429 | Query rate limit exceeded (max 10/minute per user) | null | >10 requests in 60s (FR-014) | Wait 60 seconds | `Retry-After: 60` |

### 500 Internal Server Error - Server Failures

| Code | HTTP | Message | Field | When | Resolution |
|------|------|---------|-------|------|------------|
| `INTERNAL_ERROR` | 500 | Internal server error occurred | null | Unhandled exception | Retry; contact support if persists |
| `LLM_SERVICE_ERROR` | 500 | LLM service error (retry recommended) | null | OpenAI API error | Retry with exponential backoff |
| `VECTOR_DB_ERROR` | 500 | Vector database error (retry recommended) | null | Qdrant timeout/error | Retry; check Qdrant status |

### 503 Service Unavailable - Temporary Unavailability

| Code | HTTP | Message | Field | When | Resolution |
|------|------|---------|-------|------|------------|
| `SERVICE_UNAVAILABLE` | 503 | RAG service temporarily unavailable (maintenance or overload) | null | Planned maintenance or overload | Retry after 60 seconds |
| `LLM_QUOTA_EXCEEDED` | 503 | LLM API quota exceeded - service degraded | null | OpenAI quota limit hit | Retry after quota reset |

---

## Error Handling Flow

```
Request → Authentication Check
            ↓ (401 errors)
         Authorization Check
            ↓ (403 errors)
         Input Validation
            ↓ (400 errors)
         Rate Limit Check
            ↓ (429 error)
         Vector DB Query
            ↓ (404 CONTEXT_NOT_FOUND if all < 0.3)
            ↓ (500 VECTOR_DB_ERROR on timeout)
         LLM Generation
            ↓ (500 LLM_SERVICE_ERROR on API error)
            ↓ (200 OK with grounding_status="speculative" if LLM refuses per FR-004)
            ↓ (422 INSUFFICIENT_GROUNDING if confidence < 0.3 per FR-009)
         Success Response (200 OK)
```

---

## Example Error Responses

### 400 QUERY_TEXT_EMPTY
```json
{
  "error_code": "QUERY_TEXT_EMPTY",
  "message": "Query text cannot be empty or whitespace",
  "field": "query_text",
  "details": null,
  "request_id": "req-a1b2c3d4"
}
```

### 401 TOKEN_EXPIRED
```json
{
  "error_code": "TOKEN_EXPIRED",
  "message": "Bearer token has expired",
  "field": null,
  "details": {
    "exp": 1735689600,
    "current_time": 1735690000
  },
  "request_id": "req-e5f6g7h8"
}
```

### 403 CHAPTER_ACCESS_DENIED
```json
{
  "error_code": "CHAPTER_ACCESS_DENIED",
  "message": "User subscription does not include this chapter",
  "field": "chapter_id",
  "details": {
    "chapter_id": "ch-isaac-sim-advanced",
    "user_tier": "free",
    "required_tier": "premium"
  },
  "request_id": "req-i9j0k1l2"
}
```

### 404 CONTEXT_NOT_FOUND
```json
{
  "error_code": "CONTEXT_NOT_FOUND",
  "message": "No relevant context found in chapter for this query (try broader terms)",
  "field": null,
  "details": {
    "chapter_id": "ch-ros2-fundamentals",
    "max_similarity": 0.21,
    "threshold": 0.3
  },
  "request_id": "req-m3n4o5p6"
}
```

### 422 INSUFFICIENT_GROUNDING
```json
{
  "error_code": "INSUFFICIENT_GROUNDING",
  "message": "Cannot generate grounded answer from available context (confidence < threshold)",
  "field": null,
  "details": {
    "confidence_score": 0.27,
    "threshold": 0.3,
    "chunks_retrieved": 5
  },
  "request_id": "req-q7r8s9t0"
}
```

### 429 RATE_LIMIT_EXCEEDED
```json
{
  "error_code": "RATE_LIMIT_EXCEEDED",
  "message": "Query rate limit exceeded (max 10/minute per user)",
  "field": null,
  "details": {
    "limit": 10,
    "window_seconds": 60,
    "retry_after": 60
  },
  "request_id": "req-u1v2w3x4"
}
```

---

## Client Error Handling Guidelines

**For Frontend Developers**:

1. **Always check error_code** (not just HTTP status) for specific handling
2. **Display message** to users (human-readable, actionable)
3. **Use field** to highlight problematic input fields
4. **Handle rate limits** by respecting Retry-After header
5. **Retry logic**:
   - 429: Wait Retry-After seconds
   - 500/503: Exponential backoff (1s, 2s, 4s, 8s, 16s max)
   - 401 TOKEN_EXPIRED: Refresh token, retry once
   - 4xx (other): Do not retry (client error)

**Example Client Code** (JavaScript):
```javascript
async function queryRAG(queryText, chapterId) {
  try {
    const response = await fetch('/api/v1/query', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query_text: queryText, chapter_id: chapterId })
    });

    if (!response.ok) {
      const error = await response.json();

      switch (error.error_code) {
        case 'TOKEN_EXPIRED':
          await refreshToken();
          return queryRAG(queryText, chapterId); // Retry once

        case 'RATE_LIMIT_EXCEEDED':
          const retryAfter = error.details?.retry_after || 60;
          await sleep(retryAfter * 1000);
          return queryRAG(queryText, chapterId);

        case 'CHAPTER_ACCESS_DENIED':
          showUpgradePrompt(error.details);
          throw error;

        default:
          showErrorMessage(error.message);
          throw error;
      }
    }

    return await response.json();
  } catch (err) {
    console.error('RAG query failed:', err);
    throw err;
  }
}
```

---

## Traceability Matrix

| Error Code | FR | Constitution Rule | Test Case |
|------------|-----|-------------------|-----------|
| MISSING_TOKEN | FR-011 | Rule V (Security) | test_missing_auth_header |
| INVALID_TOKEN | FR-011 | Rule V (Security) | test_invalid_jwt_signature |
| TOKEN_EXPIRED | FR-011 | Rule V (Security) | test_expired_jwt_token |
| QUERY_TEXT_EMPTY | FR-002 | Rule III (Errors) | test_empty_query_validation |
| INVALID_CHAPTER_ID | FR-002 | Rule III (Errors) | test_malformed_chapter_id |
| CHAPTER_ACCESS_DENIED | FR-012 | Rule V (Security) | test_unauthorized_chapter_access |
| CONTEXT_NOT_FOUND | FR-008 | Rule III (Errors) | test_low_similarity_chunks |
| INSUFFICIENT_GROUNDING | FR-009 | Rule III (Errors) | test_confidence_below_threshold |
| RATE_LIMIT_EXCEEDED | FR-014 | Rule III (Errors) | test_rate_limit_enforcement |
| VECTOR_DB_ERROR | FR-015 | Rule III (Errors) | test_qdrant_timeout |
| LLM_SERVICE_ERROR | FR-015 | Rule III (Errors) | test_openai_api_error |

---

## Status Code Summary

| HTTP | Error Codes | Count |
|------|-------------|-------|
| 200 | (success + LLM refusals) | N/A |
| 400 | INVALID_INPUT, QUERY_TEXT_EMPTY, INVALID_CHAPTER_ID, INVALID_USER_ID, INVALID_SESSION_ID | 5 |
| 401 | MISSING_TOKEN, INVALID_TOKEN, TOKEN_EXPIRED | 3 |
| 403 | INSUFFICIENT_PERMISSIONS, CHAPTER_ACCESS_DENIED | 2 |
| 404 | CHAPTER_NOT_FOUND, CONTEXT_NOT_FOUND | 2 |
| 422 | INSUFFICIENT_GROUNDING, QUERY_TOO_BROAD | 2 |
| 429 | RATE_LIMIT_EXCEEDED | 1 |
| 500 | INTERNAL_ERROR, LLM_SERVICE_ERROR, VECTOR_DB_ERROR | 3 |
| 503 | SERVICE_UNAVAILABLE, LLM_QUOTA_EXCEEDED | 2 |

**Total**: 20 unique error codes
