---
id: 002
title: RAG Query Endpoint Specification
stage: spec
date: 2025-11-28
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-rag-query-endpoint
branch: 001-rag-query-endpoint
user: user
command: /sp.specify
labels: ["specification", "rag", "api-design", "authentication", "grounding"]
links:
  spec: specs/001-rag-query-endpoint/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-rag-query-endpoint/spec.md
 - specs/001-rag-query-endpoint/checklists/requirements.md
tests:
 - none
---

## Prompt

```text
I have written the complete specification for the core RAG Pipeline API endpoint: `POST /api/v1/query`.

I need my pre-configured **API Contract Designer** subagent to validate and formalize this specification:

1. **Schema Generation**: Please generate the final, concrete **Pydantic Schemas** (Python code) for the `QueryRequest` and the `QueryResponse` based on my Acceptance Criteria (AC 3.2 and AC 3.4).

2. **SMART Analysis**: Are all Acceptance Criteria (AC 3.1 through AC 3.6) Specific, Measurable, Achievable, Relevant, and Testable? If any are vague (especially AC 3.5 and AC 3.6), suggest a specific, quantifiable fix.

3. **Completeness Check**: Did I miss any critical architectural details or error responses for an authenticated RAG API that is central to an educational platform?

**Current Draft Specification (`specs/rag_api/spec.md`):**

# Specification: RAG Pipeline Query Endpoint

## 1. Overview
The primary API endpoint for the textbook platform. It allows an authenticated user to ask a question about the course content and receive a contextually grounded, AI-generated answer.

## 2. Scope & Endpoint
| Attribute | Detail |
|---|---|
| **Endpoint**| `POST /api/v1/query` |
| **Purpose** | Process user query via RAG and return a concise, sourced answer. |
| **Auth** | Required (Better-Auth Bearer Token in Header) |
| **Service** | FastAPI / RAG Backend Service |

## 3. Requirements (Acceptance Criteria)

**AC 3.1 (Authentication):** The endpoint MUST successfully validate the provided Bearer Token (Rule 5.1). If validation fails, it MUST return a `401 Unauthorized` response (Rule 3.2).

**AC 3.2 (Input Schema):** The endpoint MUST accept a JSON body conforming to the `QueryRequest` schema, including `query_text` (string), `chapter_id` (string), and `user_id` (string).

**AC 3.3 (Content Grounding):** The AI-generated `answer` MUST be exclusively generated from the retrieved source chunks from the vector database. Any ungrounded claims MUST result in a specific error response (e.g., `404 Not Found in Context`).

**AC 3.4 (Output Format):** The successful response MUST return ae implementation MUST use Pydantic for request/response schemas and 100% Python type hints (Rule 1.1).
- **Error Handling:** All non-200 responses MUST follow the standardized JSON error format (`error_code`, `message`) (Rule 3.1).
- **Testing:** The RAG logic MUST be tested for grounding success and failure cases with 90% coverage (Rule 2.1).
```

## Response snapshot

Created comprehensive specification for RAG Pipeline Query Endpoint with API Contract Designer subagent validation.

**Specification deliverables:**
- Created branch: `001-rag-query-endpoint`
- Wrote `specs/001-rag-query-endpoint/spec.md` with 3 prioritized user stories
- Generated quality checklist at `specs/001-rag-query-endpoint/checklists/requirements.md`

**User Stories (independently testable):**
1. **P1 - Student Asks Course Question**: Core RAG functionality with grounding validation (fully_grounded/partially_grounded/speculative status based on confidence scores)
2. **P2 - Student Gets Clear Error Feedback**: Comprehensive error handling (401/403/404/422/429/500/503) with actionable messages
3. **P3 - Student Reviews Answer Sources**: Source transparency with chunk_ids, similarity_scores, content excerpts

**Functional Requirements:** 18 requirements (FR-001 to FR-018) covering:
- Authentication (Better-Auth JWT validation with signature/expiration/issuer checks)
- Input validation (query_text 1-1000 chars, chapter_id pattern, user_id UUIDv4)
- RAG grounding (cosine similarity threshold 0.3, confidence_score calculation, grounding_status classification)
- Error responses (standardized JSON format with error_code/message/field/request_id)
- Security (input sanitization, rate limiting 10 req/min, PII logging prohibitions)
- Performance (timeouts: 5s vector DB, 25s LLM, 30s total)

**Success Criteria:** 8 measurable, technology-agnostic outcomes:
- p95 latency < 3s
- 100 QPS system-wide
- 95% queries with similarity > 0.5 are fully/partially grounded
- 100% error responses with appropriate 4xx codes
- 90% test coverage
- 90% error self-service rate
- 100% responses with valid source citations
- Rate limiting enforced at 11th request

**API Contract Designer Validation:**
- Generated complete Pydantic schemas (QueryRequest, QueryResponse, SourceChunk, ErrorDetail)
- Provided SMART analysis identifying vague ACs (AC 3.1, 3.3) and missing ACs (3.5 Performance, 3.6 Security)
- Identified critical gaps: RAG pipeline config (embedding model, chunk strategy, LLM settings), authentication implementation details, error taxonomy, observability requirements
- Suggested improvements: idempotency support, feature flags, caching strategy, contract testing

**Validation Result:** ✅ ALL CHECKS PASSED - Spec is complete and ready for planning phase (`/sp.plan`)

## Outcome

- ✅ Impact: Complete, production-ready specification for RAG Pipeline Query Endpoint with comprehensive error handling, grounding validation, and performance requirements
- 🧪 Tests: 90% coverage target specified in SC-005 with test categories defined (authentication, input validation, grounding logic, error handling)
- 📁 Files: Created spec.md (191 lines) and requirements checklist with all validation checks passing
- 🔁 Next prompts: `/sp.plan` to create implementation plan including RAG pipeline configuration, authentication flow, and API contracts
- 🧠 Reflection: API Contract Designer subagent provided invaluable validation, identifying missing performance/security requirements and providing concrete Pydantic schemas. Spec successfully balances user-facing requirements with technical rigor while maintaining technology-agnostic success criteria.

## Evaluation notes (flywheel)

- Failure modes observed: None - spec validation passed all quality checks on first iteration
- Graders run and results (PASS/FAIL): Quality checklist validation - PASS (14/14 items)
- Prompt variant (if applicable): Used API Contract Designer subagent for validation and schema generation
- Next experiment (smallest change to try): During planning, incorporate subagent's recommendations for AC 3.5 (Performance) and AC 3.6 (Security) into implementation plan contracts
