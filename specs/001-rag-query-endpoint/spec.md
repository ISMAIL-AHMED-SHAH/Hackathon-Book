# Feature Specification: RAG Pipeline Query Endpoint

**Feature Branch**: `001-rag-query-endpoint`
**Created**: 2025-11-28
**Status**: Draft
**Input**: User description: "RAG Pipeline Query Endpoint for authenticated textbook content queries"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Student Asks Course Question (Priority: P1)

A logged-in student reading a textbook chapter encounters a concept they don't understand. They use the embedded RAG chatbot to ask a question about that specific chapter and receive an AI-generated answer grounded in the chapter's content, with citations to source material.

**Why this priority**: This is the core value proposition of the RAG chatbot - enabling students to get instant, contextual help while learning Physical AI concepts. Without this, the chatbot cannot function.

**Independent Test**: Can be fully tested by authenticating a user, providing a valid chapter ID and question, and verifying the system returns a grounded answer with source citations.

**Acceptance Scenarios**:

1. **Given** a logged-in student is reading "Chapter 3: ROS 2 Fundamentals", **When** they ask "What is a ROS 2 node?", **Then** the system returns an answer grounded in Chapter 3 content with at least one source citation showing similarity score > 0.7

2. **Given** a logged-in student asks a question about transformers in the AI chapter, **When** the vector database finds highly relevant content (similarity > 0.7), **Then** the response includes `grounding_status: "fully_grounded"` and confidence_score >= 0.7

3. **Given** a logged-in student asks a very specific question, **When** the vector database finds only marginally relevant content (similarity 0.5-0.7), **Then** the response includes `grounding_status: "partially_grounded"` and confidence_score between 0.5-0.7

4. **Given** a logged-in student asks a question completely unrelated to the chapter, **When** no relevant context is found (all chunks have similarity < 0.3), **Then** the system returns 404 CONTEXT_NOT_FOUND with message "No relevant context found in this chapter for your query"

---

### User Story 2 - Student Gets Clear Error Feedback (Priority: P2)

When a student makes an invalid request (empty question, wrong chapter ID, expired session), they receive clear, actionable error messages that help them fix the problem without developer intervention.

**Why this priority**: Clear error handling prevents student frustration and reduces support burden. It's essential for usability but can be implemented after the core happy path works.

**Independent Test**: Can be tested by sending various invalid requests and verifying appropriate error codes and helpful messages are returned.

**Acceptance Scenarios**:

1. **Given** a student's authentication token has expired, **When** they submit a query, **Then** the system returns 401 TOKEN_EXPIRED with message "Bearer token has expired" and prompts re-authentication

2. **Given** a student submits an empty question (whitespace only), **When** the request is validated, **Then** the system returns 400 QUERY_TEXT_EMPTY with message "Query text cannot be empty or whitespace"

3. **Given** a student requests a chapter they don't have access to, **When** authorization is checked, **Then** the system returns 403 CHAPTER_ACCESS_DENIED with message "User subscription does not include this chapter"

4. **Given** a student provides an invalid chapter ID format, **When** input validation runs, **Then** the system returns 400 INVALID_CHAPTER_ID with message "Chapter ID format is invalid (expected: ch-{slug})"

---

### User Story 3 - Student Reviews Answer Sources (Priority: P3)

After receiving an AI-generated answer, a student can review the source chunks that were used to generate the answer, including similarity scores and page numbers, to verify accuracy and explore further.

**Why this priority**: Source transparency builds trust in the AI system and enables students to do deeper research. It's valuable but not blocking for the core query functionality.

**Independent Test**: Can be tested by submitting a query and verifying the response includes a sources array with chunk_id, content excerpts, similarity scores, and optional metadata (page numbers, section titles).

**Acceptance Scenarios**:

1. **Given** a student receives an AI-generated answer, **When** they inspect the response, **Then** the sources array contains 1-10 source chunks ordered by similarity_score descending

2. **Given** a source chunk is included in the response, **When** the student examines it, **Then** each source includes chunk_id, content excerpt (max 500 chars), similarity_score (0.0-1.0), and optional page_number and section_title

3. **Given** multiple source chunks contributed to an answer, **When** the response is generated, **Then** the confidence_score equals the mean of all included chunk similarity_scores

---

### Edge Cases

- What happens when a student submits a query longer than 1000 characters? (System returns 400 INVALID_INPUT with field-specific error)
- What happens when the LLM service is temporarily unavailable? (System returns 503 SERVICE_UNAVAILABLE with retry recommendation)
- What happens when a student exceeds the rate limit of 10 queries per minute? (System returns 429 RATE_LIMIT_EXCEEDED with Retry-After header set to 60 seconds)
- What happens when the vector database query times out after 5 seconds? (System returns 500 VECTOR_DB_ERROR with retry recommendation)
- What happens when a student's session_id is provided but is in an invalid format? (System returns 400 INVALID_INPUT for session_id field)
- What happens when retrieved chunks have very low confidence but the LLM still generates text? (System returns 422 INSUFFICIENT_GROUNDING rather than returning speculative content)
- What happens when the LLM refuses to answer due to insufficient context? (System returns 200 OK with the LLM's refusal message as the answer and grounding_status "speculative")

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST validate Bearer tokens using Better-Auth JWT verification including signature validation, expiration check, issuer verification, and user ID extraction

- **FR-002**: System MUST accept POST requests to `/api/v1/query` with JSON body containing required fields: query_text (string, 1-1000 chars), chapter_id (string, pattern `^ch-[a-z0-9-]{3,50}$`), and user_id (UUIDv4 format)

- **FR-003**: System MUST retrieve top_k context chunks (default 5, range 1-10) from vector database using cosine similarity with minimum threshold of 0.3

- **FR-004**: System MUST generate AI answers using only the retrieved context chunks, with system prompt instructing the LLM to refuse answering if context is insufficient. When the LLM explicitly refuses (responds with "I don't have enough information in this chapter to answer that" or similar), the system MUST return 200 OK with the LLM's refusal message as the answer and grounding_status set to "speculative"

- **FR-005**: System MUST return successful responses (200 OK) with JSON body containing: answer (string), sources array (1-10 SourceChunk objects), confidence_score (float 0.0-1.0), grounding_status (enum), query_id (unique identifier), processing_time_ms (integer), and created_at (ISO 8601 datetime)

- **FR-006**: System MUST calculate confidence_score as the mean similarity score of all retrieved chunks used in answer generation

- **FR-007**: System MUST set grounding_status to "fully_grounded" when confidence_score >= 0.7, "partially_grounded" when 0.5 <= confidence_score < 0.7, and "speculative" when 0.3 <= confidence_score < 0.5

- **FR-008**: System MUST return 404 CONTEXT_NOT_FOUND when all retrieved chunks have similarity < 0.3 (no relevant context found)

- **FR-009**: System MUST return 422 INSUFFICIENT_GROUNDING when confidence_score < 0.3 after LLM generation (answer quality too low). This applies only when the LLM generates substantive content despite low confidence; LLM explicit refusals are handled per FR-004 as 200 OK responses

- **FR-010**: System MUST return standardized error responses for all non-2xx status codes with JSON format: `{"error_code": "...", "message": "...", "field": "...", "request_id": "..."}`

- **FR-011**: System MUST enforce authentication by returning 401 UNAUTHORIZED with specific error codes: MISSING_TOKEN (no Authorization header), INVALID_TOKEN (signature invalid), TOKEN_EXPIRED (exp claim in past)

- **FR-012**: System MUST enforce authorization by verifying user has access to requested chapter_id and returning 403 CHAPTER_ACCESS_DENIED if user subscription does not include the chapter

- **FR-013**: System MUST sanitize input by stripping HTML/script tags from query_text and rejecting queries containing SQL injection patterns

- **FR-014**: System MUST enforce rate limiting of 10 requests per minute per user and return 429 RATE_LIMIT_EXCEEDED with Retry-After header set to 60 seconds when limit is exceeded

- **FR-015**: System MUST implement timeout policy: 5 seconds for vector database queries, 25 seconds for LLM API calls, 30 seconds total client timeout

- **FR-016**: System MUST log all queries with structured JSON including: query_id, user_id (hashed), chapter_id, status_code, latency_ms, confidence_score, error_code - but NEVER log raw query_text containing PII

- **FR-017**: System MUST expose performance metrics for monitoring including: query latency percentiles (p50/p95/p99), grounding quality rate (percentage of queries with grounding_status "fully_grounded" or "partially_grounded"), error rate by error type, and rate limit hit count

- **FR-018**: System MUST support optional request parameters: top_k (int, 1-10, default 5), temperature (float, 0.0-1.0, default 0.7), session_id (string, pattern `^sess-[a-f0-9]{32}$`)

- **FR-019**: System MUST order sources array by similarity_score in descending order (highest relevance first)

### Key Entities

- **Query**: Represents a student's question about course content
  - Attributes: query_id (unique identifier), query_text (the question), chapter_id (scope), user_id (authenticated user), timestamp, processing_time, confidence_score
  - Relationships: belongs to User, scoped to Chapter, contains multiple SourceChunks

- **SourceChunk**: Represents a piece of textbook content used to answer a query
  - Attributes: chunk_id (unique identifier), content (text excerpt), similarity_score (relevance to query), page_number (optional), section_title (optional), embedding (vector representation)
  - Relationships: belongs to Chapter, retrieved by Query

- **User**: Represents an authenticated student
  - Attributes: user_id (UUID), subscription (access permissions), authentication_token (JWT)
  - Relationships: has Subscription, makes Queries

- **Chapter**: Represents a textbook chapter with embedded content
  - Attributes: chapter_id (identifier), title, content (chunked text), embeddings (vector representations)
  - Relationships: contains SourceChunks, accessed by Users based on Subscription

- **Subscription**: Represents a user's access permissions
  - Attributes: user_id, accessible_chapters (array of chapter_ids), expiration_date
  - Relationships: belongs to User, grants access to Chapters

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Students receive query responses with p95 latency under 3 seconds (measured from request received to response sent)

- **SC-002**: The system successfully handles 100 queries per second system-wide without degradation

- **SC-003**: For queries where relevant context exists (similarity > 0.5), 95% of responses have grounding_status of "fully_grounded" or "partially_grounded" (not "speculative")

- **SC-004**: Invalid requests (authentication failures, validation errors, authorization denials) return appropriate 4xx error codes with actionable error messages in 100% of cases

- **SC-005**: The system maintains 90% test coverage across all acceptance criteria with specific test cases for authentication, input validation, grounding logic, and error handling

- **SC-006**: Students can independently understand error messages and take corrective action without developer support in 90% of error scenarios (measured via support ticket reduction)

- **SC-007**: Source citations in responses include valid chunk_ids, similarity_scores, and content excerpts in 100% of successful queries

- **SC-008**: The system enforces rate limiting correctly, rejecting the 11th request within a 1-minute window with 429 status code

## Assumptions *(optional)*

- Users are already authenticated before reaching this endpoint (Better-Auth handles the auth flow separately)
- The vector database (Qdrant) is pre-populated with chapter content embeddings
- The LLM service API is configured and accessible
- Chapter access control is managed via a subscription service/database
- User subscriptions include an `accessible_chapters` array that can be queried
- Embedding model uses 1536 dimensions
- LLM model supports approximately 1500 max tokens for responses
- Session tracking (session_id) is optional and used for conversation continuity if provided
- Costs for LLM API calls are acceptable for educational use case
- Privacy requirements prohibit logging raw query_text
- Audit logs are retained for 90 days for compliance

## Dependencies *(optional)*

- **Better-Auth Service**: Provides JWT token generation and validation for user authentication
- **Vector Database (Qdrant Cloud Free Tier)**: Stores chapter content embeddings and provides similarity search
- **LLM API**: Generates AI answers based on retrieved context
- **Neon Serverless Postgres**: Stores user subscriptions, chapter metadata, and query audit logs
- **Pydantic**: Schema validation library for request/response models (enforced by constitution Rule 1.1)

## Out of Scope *(optional)*

- **Conversation History**: Multi-turn conversations with context from previous queries (session_id support is included but conversation history persistence is future work)
- **Answer Caching**: Caching identical queries to reduce LLM costs (future optimization)
- **Multi-Chapter Queries**: Asking questions that span multiple chapters (current scope: single chapter_id per query)
- **Voice Input**: Speech-to-text for voice queries (text-only for MVP)
- **Answer Translation**: Translating answers to Urdu or other languages (separate feature)
- **Content Personalization**: Adjusting answer complexity based on user background (separate feature)
- **Admin Analytics Dashboard**: Viewing query analytics and user behavior patterns (separate feature)
- **Custom Embedding Models**: Using domain-specific embedding models (using standard embeddings for MVP)

## Clarifications

### Session 2025-11-28

- Q: When the LLM system prompt instructs it to refuse answering due to insufficient context, should the system treat this as a successful grounding check or an error? → A: Treat as successful 200 OK response with answer "I don't have enough information in this chapter to answer that" and grounding_status "speculative"
- Q: What value should the Retry-After header contain when rate limit is exceeded? → A: 60 seconds (wait until the next minute window starts)
- Q: What key metrics should the system expose for monitoring and alerting? → A: Query latency (p50/p95/p99), grounding quality rate, error rate by type, rate limit hits
