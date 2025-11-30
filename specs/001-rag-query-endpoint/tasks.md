# Tasks: RAG Pipeline Query Endpoint

**Input**: Design documents from `/specs/001-rag-query-endpoint/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Included per constitution Rule II (90% coverage target)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths follow plan.md structure (FastAPI backend + Docusaurus frontend)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend directory structure per plan.md (backend/src/{api,models,services,core,utils}/, backend/tests/{contract,integration,unit}/, backend/scripts/)
- [X] T002 [P] Initialize Python 3.11+ project with pyproject.toml (Poetry dependencies: FastAPI 0.104+, Pydantic 2.5+, qdrant-client 1.7+, openai 1.6+, python-jose 3.3+, asyncpg 0.29+, redis 5.0+)
- [X] T003 [P] Create .env.example file with all required environment variables per quickstart.md (OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, NEON_CONNECTION_STRING, BETTER_AUTH_SECRET, REDIS_URL)
- [X] T004 [P] Configure Black formatter (line length 100), Flake8 linter, and mypy type checker in setup.cfg per constitution Rule I
- [X] T005 [P] Setup pre-commit hooks for Black, Flake8, and mypy --strict validation
- [X] T006 [P] Create docker-compose.yml with services: fastapi (hot-reload), redis (rate limiting) per research.md Decision 9
- [X] T007 [P] Add .gitignore (exclude .env, __pycache__, .pytest_cache, .mypy_cache, *.pyc)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Create core configuration in backend/src/core/config.py (Settings class with Pydantic BaseSettings for all .env variables: OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, NEON_CONNECTION_STRING, BETTER_AUTH_SECRET, REDIS_URL, RATE_LIMIT_REQUESTS, VECTOR_DB_TIMEOUT, LLM_TIMEOUT)
- [ ] T009 [P] Setup Neon Postgres schema in backend/scripts/setup_neon_schema.sql (subscriptions table with GIN index on accessible_chapters array, query_audit_log table partitioned by month per research.md Decision 7)
- [ ] T010 [P] Create Qdrant collection setup script in backend/scripts/setup_qdrant_collection.py (collection "textbook-chapters" with 1536-dim COSINE, HNSW config M=16, ef_construction=100 per research.md Decision 6)
- [ ] T011 [P] Implement custom exception classes in backend/src/core/exceptions.py (AuthenticationError, AuthorizationError, ValidationError, RateLimitError, VectorDBError, LLMServiceError - all mapping to ErrorCode enum)
- [ ] T012 [P] Setup Prometheus metrics in backend/src/core/metrics.py (query_latency_seconds Histogram, grounding_quality_rate Counter, query_errors_total Counter, rate_limit_hits_total Counter per research.md Decision 8)
- [ ] T013 [P] Implement structured logging in backend/src/services/logging.py (JSON formatter with fields: timestamp, level, query_id, user_id_hash, chapter_id, status_code, latency_ms, NO query_text per FR-016)
- [ ] T014 Create FastAPI app initialization in backend/src/api/main.py (app instance, CORS middleware, Prometheus middleware, exception handlers, /health endpoint, /metrics endpoint)
- [ ] T015 [P] Setup dependency injection in backend/src/api/dependencies.py (Qdrant client, Redis client, Neon asyncpg connection pool, OpenAI client - all singleton instances with health checks)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Student Asks Course Question (Priority: P1) 🎯 MVP

**Goal**: Authenticated students can ask questions about textbook chapters and receive AI-generated answers grounded in chapter content with source citations

**Independent Test**: Authenticate a user, provide valid chapter_id and question, verify system returns 200 OK with answer, sources array, confidence_score, grounding_status

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T016 [P] [US1] Contract test for POST /api/v1/query in backend/tests/contract/test_query_api_contract.py (validate request/response schemas match data-model.md QueryRequest/QueryResponse, verify all required fields present)
- [ ] T017 [P] [US1] Integration test for happy path (fully grounded) in backend/tests/integration/test_query_flow.py (send query with similarity > 0.7, verify 200 OK, grounding_status="fully_grounded", sources ordered by similarity_score desc per FR-019)
- [ ] T018 [P] [US1] Integration test for partially grounded answer in backend/tests/integration/test_query_flow.py (send query with similarity 0.5-0.7, verify grounding_status="partially_grounded")
- [ ] T019 [P] [US1] Integration test for speculative answer in backend/tests/integration/test_query_flow.py (send query with similarity 0.3-0.5, verify grounding_status="speculative")
- [ ] T020 [P] [US1] Integration test for LLM refusal handling in backend/tests/integration/test_query_flow.py (trigger LLM refusal, verify 200 OK with answer="I don't have enough information..." and grounding_status="speculative" per FR-004)

### Implementation for User Story 1

- [ ] T021 [P] [US1] Create QueryRequest model in backend/src/models/query.py (per data-model.md: query_text validator strips whitespace and rejects empty, user_id validator enforces UUIDv4, chapter_id pattern ^ch-[a-z0-9-]{3,50}$, top_k 1-10, temperature 0.0-1.0, optional session_id)
- [ ] T022 [P] [US1] Create SourceChunk model in backend/src/models/query.py (chunk_id, content max 500 chars, similarity_score 0.0-1.0, optional page_number/section_title per data-model.md)
- [ ] T023 [P] [US1] Create QueryResponse model in backend/src/models/query.py (answer, sources List[SourceChunk], confidence_score, GroundingStatus enum, query_id pattern ^qry-[a-f0-9]{32}$, processing_time_ms, created_at, optional metadata per data-model.md)
- [ ] T024 [P] [US1] Create VectorSearchResult model in backend/src/models/vector.py (wrapper for Qdrant results with from_qdrant_result factory method per data-model.md)
- [ ] T025 [US1] Implement vector search service in backend/src/services/vector_search.py (query Qdrant with chapter_id filter, top_k limit, score_threshold=0.3 per FR-003, return List[VectorSearchResult], handle timeouts 5s per FR-015)
- [ ] T026 [US1] Implement LLM service in backend/src/services/llm.py (construct system prompt per research.md Decision 3, call OpenAI GPT-4 Turbo with temperature parameter, max_tokens=1500, timeout 25s per FR-015, detect refusals "I don't have enough information" per FR-004)
- [ ] T027 [US1] Implement confidence scoring logic in backend/src/services/query_service.py (calculate mean similarity of retrieved chunks per FR-006, classify grounding_status per FR-007: ≥0.7 fully_grounded, ≥0.5 partially_grounded, ≥0.3 speculative, <0.3 error)
- [ ] T028 [US1] Implement POST /api/v1/query endpoint in backend/src/api/v1/query.py (validate QueryRequest, call vector_search, call llm_service, calculate confidence_score, return QueryResponse with sources sorted by similarity desc per FR-019, log to query_audit_log table, record metrics)
- [ ] T029 [US1] Add 404 CONTEXT_NOT_FOUND error handling in backend/src/api/v1/query.py (raise when all chunks < 0.3 similarity per FR-008, return ErrorDetail with error_code, message, request_id)
- [ ] T030 [US1] Add 422 INSUFFICIENT_GROUNDING error handling in backend/src/api/v1/query.py (raise when confidence_score < 0.3 after LLM generation and LLM did NOT explicitly refuse per FR-009, return ErrorDetail)
- [ ] T031 [US1] Add unit test for confidence scoring in backend/tests/unit/test_confidence_scoring.py (test mean calculation, grounding_status thresholds, edge cases: all chunks same score, single chunk)
- [ ] T032 [P] [US1] Add unit test for LLM service in backend/tests/unit/test_llm_service.py (test system prompt construction, temperature handling, timeout enforcement, refusal detection regex)
- [ ] T033 [P] [US1] Add unit test for vector search in backend/tests/unit/test_vector_search.py (test Qdrant query construction with filters, top_k, threshold, cosine similarity calculation, metadata extraction)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Student Gets Clear Error Feedback (Priority: P2)

**Goal**: Students receive clear, actionable error messages for invalid requests (authentication failures, validation errors, authorization denials)

**Independent Test**: Send various invalid requests and verify appropriate error codes (401, 400, 403) and helpful messages are returned

### Tests for User Story 2 ⚠️

- [ ] T034 [P] [US2] Contract test for error responses in backend/tests/contract/test_error_responses.py (validate all 20 error codes return ErrorDetail schema with error_code, message, field, request_id per data-model.md)
- [ ] T035 [P] [US2] Integration test for authentication errors in backend/tests/integration/test_authentication.py (test MISSING_TOKEN 401 when no Authorization header, INVALID_TOKEN 401 for bad signature, TOKEN_EXPIRED 401 for expired JWT per FR-011)
- [ ] T036 [P] [US2] Integration test for validation errors in backend/tests/integration/test_validation.py (test QUERY_TEXT_EMPTY 400 for whitespace query, INVALID_CHAPTER_ID 400 for malformed chapter_id, INVALID_USER_ID 400 for non-UUID)
- [ ] T037 [P] [US2] Integration test for authorization errors in backend/tests/integration/test_authorization.py (test CHAPTER_ACCESS_DENIED 403 when chapter not in user's accessible_chapters per FR-012)

### Implementation for User Story 2

- [ ] T038 [P] [US2] Create ErrorCode enum in backend/src/models/errors.py (20 error codes per data-model.md: INVALID_INPUT, QUERY_TEXT_EMPTY, INVALID_CHAPTER_ID, MISSING_TOKEN, INVALID_TOKEN, TOKEN_EXPIRED, CHAPTER_ACCESS_DENIED, CONTEXT_NOT_FOUND, INSUFFICIENT_GROUNDING, RATE_LIMIT_EXCEEDED, VECTOR_DB_ERROR, SERVICE_UNAVAILABLE, etc.)
- [ ] T039 [P] [US2] Create ErrorDetail model in backend/src/models/errors.py (error_code: ErrorCode, message: str, optional field, optional details dict, optional request_id per FR-010)
- [ ] T040 [US2] Implement Better-Auth JWT validation in backend/src/services/auth.py (extract Bearer token from Authorization header, decode with python-jose HS256, verify signature with BETTER_AUTH_SECRET, check exp claim, verify iss="better-auth", extract sub as user_id per research.md Decision 5)
- [ ] T041 [US2] Implement subscription access check in backend/src/services/subscription.py (query Neon subscriptions table by user_id, check chapter_id in accessible_chapters array with GIN index, check expiration_date per FR-012)
- [ ] T042 [US2] Implement input sanitization in backend/src/utils/sanitization.py (strip HTML/script tags from query_text, reject SQL injection patterns per FR-013)
- [ ] T043 [US2] Add authentication middleware to FastAPI in backend/src/api/main.py (apply auth.validate_jwt to all /api/v1/* routes, raise 401 MISSING_TOKEN/INVALID_TOKEN/TOKEN_EXPIRED exceptions)
- [ ] T044 [US2] Add authorization check to POST /api/v1/query in backend/src/api/v1/query.py (call subscription.check_chapter_access before vector search, raise 403 CHAPTER_ACCESS_DENIED if denied)
- [ ] T045 [US2] Add request validation error handling in backend/src/api/v1/query.py (catch Pydantic ValidationError, return 400 INVALID_INPUT with field name)
- [ ] T046 [US2] Add sanitization to query_text field validator in backend/src/models/query.py (call utils.sanitization before other validation)
- [ ] T047 [P] [US2] Add unit test for JWT validation in backend/tests/unit/test_auth_service.py (test signature verification HS256, expiration validation, issuer validation, user_id extraction)
- [ ] T048 [P] [US2] Add unit test for input sanitization in backend/tests/unit/test_input_sanitization.py (test HTML tag stripping, SQL injection detection, whitespace trimming)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Student Reviews Answer Sources (Priority: P3)

**Goal**: Students can review source chunks used to generate answers, including similarity scores, page numbers, and section titles for transparency and deeper research

**Independent Test**: Submit a query and verify response includes sources array with chunk_id, content excerpts, similarity_score, optional metadata (page numbers, section titles), ordered by similarity descending

### Tests for User Story 3 ⚠️

- [ ] T049 [P] [US3] Integration test for source ordering in backend/tests/integration/test_source_transparency.py (verify sources array ordered by similarity_score descending per FR-019)
- [ ] T050 [P] [US3] Integration test for source metadata in backend/tests/integration/test_source_transparency.py (verify each source includes chunk_id, content excerpt max 500 chars, similarity_score 0.0-1.0, optional page_number/section_title)
- [ ] T051 [P] [US3] Integration test for confidence score calculation in backend/tests/integration/test_source_transparency.py (verify confidence_score equals mean of all source similarity_scores per FR-006)

### Implementation for User Story 3

- [ ] T052 [P] [US3] Add metadata extraction to chapter ingestion script in backend/scripts/ingest_chapters.py (parse markdown headers for section_title, infer page_number from content structure per research.md Decision 2)
- [ ] T053 [US3] Enhance SourceChunk population in backend/src/api/v1/query.py (include all metadata fields from Qdrant payload: chunk_id, content truncated to 500 chars, similarity_score, page_number, section_title)
- [ ] T054 [US3] Add source ordering logic in backend/src/api/v1/query.py (sort sources by similarity_score descending before returning QueryResponse per FR-019)
- [ ] T055 [US3] Add confidence_score calculation in backend/src/services/query_service.py (compute mean of source similarity scores per FR-006, include in QueryResponse)
- [ ] T056 [P] [US3] Add frontend RAGChatbot component in frontend/src/components/RagChatbot.tsx (display answer, collapsible sources section with similarity scores, clickable page numbers, per quickstart.md frontend integration example)
- [ ] T057 [P] [US3] Add TypeScript query API client in frontend/src/services/queryApi.ts (POST /api/v1/query with Authorization header, type-safe QueryRequest/QueryResponse interfaces, error handling)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Rate Limiting & Observability (Cross-Cutting)

**Purpose**: Rate limiting enforcement and production observability across all user stories

- [ ] T058 [P] Implement Redis-based rate limiter in backend/src/services/rate_limiter.py (sliding window algorithm with ZADD/ZREMRANGEBYSCORE, 10 req/min per user_id, return retry_after=60 when exceeded per research.md Decision 4)
- [ ] T059 Add rate limit middleware to POST /api/v1/query in backend/src/api/v1/query.py (call rate_limiter.check before processing, raise 429 RATE_LIMIT_EXCEEDED with Retry-After: 60 header per FR-014)
- [ ] T060 [P] Add query audit logging to POST /api/v1/query in backend/src/api/v1/query.py (insert into query_audit_log table with query_id, user_id_hash SHA256, chapter_id, status_code, latency_ms, confidence_score, grounding_status per data-model.md QueryAuditLog)
- [ ] T061 [P] Add Prometheus metrics instrumentation to POST /api/v1/query in backend/src/api/v1/query.py (record query_latency_seconds, increment grounding_quality_rate by status, increment query_errors_total by error_code per FR-017)
- [ ] T062 [P] Integration test for rate limiting in backend/tests/integration/test_rate_limiting.py (send 10 requests succeed, 11th returns 429 RATE_LIMIT_EXCEEDED with Retry-After: 60 header, reset after 60s per FR-014)
- [ ] T063 [P] Unit test for rate limiter in backend/tests/unit/test_rate_limiter.py (test sliding window logic, ZADD/ZCARD operations, expire timing, edge cases: exactly 10 requests, Redis unavailable fallback)

---

## Phase 7: Content Ingestion Pipeline

**Purpose**: Ingest textbook chapters into Qdrant for RAG retrieval

- [ ] T064 [P] Create chapter ingestion script in backend/scripts/ingest_chapters.py (read markdown files from data/chapters/, chunk with tiktoken cl100k_base 512 tokens + 64 overlap, generate chunk_ids, extract metadata per research.md Decision 2)
- [ ] T065 [P] Add OpenAI embedding generation to backend/scripts/ingest_chapters.py (batch 100 chunks per API call, use text-embedding-3-small, exponential backoff for rate limits per research.md Decision 1)
- [ ] T066 [P] Add Qdrant upload to backend/scripts/ingest_chapters.py (upsert PointStruct with chunk_id hash, 1536-dim embedding, payload with chapter_id/content/metadata)
- [ ] T067 [P] Create ingestion validation script in backend/scripts/validate_ingestion.py (query Qdrant collection for total chunks, test semantic search with sample query "What is a ROS 2 node?", verify top results have similarity > 0.7)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T068 [P] Add timeout handling for vector DB in backend/src/services/vector_search.py (asyncio.wait_for with timeout=5s, raise 500 VECTOR_DB_ERROR on timeout per FR-015)
- [ ] T069 [P] Add timeout handling for LLM in backend/src/services/llm.py (OpenAI client timeout=25s, raise 500 LLM_SERVICE_ERROR on timeout per FR-015)
- [ ] T070 [P] Add 503 SERVICE_UNAVAILABLE handling in backend/src/api/v1/query.py (catch OpenAI API errors, Qdrant connection errors, return ErrorDetail with retry recommendation)
- [ ] T071 [P] Create .env file from .env.example and add to .gitignore (ensure secrets not committed per constitution Rule V)
- [ ] T072 [P] Run mypy --strict on backend/src/ and fix all type errors (achieve 100% type hints per constitution Rule I)
- [ ] T073 Run pytest with coverage report (pytest backend/tests/ --cov=backend/src --cov-report=html, ensure ≥90% coverage per constitution Rule II)
- [ ] T074 [P] Run Black formatter and Flake8 linter (black backend/src/ backend/tests/, flake8 backend/src/, fix all violations)
- [ ] T075 [P] Validate quickstart.md instructions (follow steps 1-8, verify local development environment works)
- [ ] T076 [P] Create Dockerfile for production deployment in backend/Dockerfile (Python 3.11 slim, Poetry install, uvicorn command, expose 8000)
- [ ] T077 [P] Update frontend integration example in quickstart.md (verify RAGChatbot.tsx and queryApi.ts match current API contract)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Rate Limiting & Observability (Phase 6)**: Depends on US1 completion (POST /api/v1/query endpoint exists)
- **Content Ingestion (Phase 7)**: Can proceed in parallel with user stories after Foundational complete
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independently testable but enhances US1 with error handling
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independently testable but enhances US1 with source transparency

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 Setup**: T002-T007 all marked [P] can run in parallel
- **Phase 2 Foundational**: T009-T013, T015 all marked [P] can run in parallel
- **Phase 3 US1 Tests**: T016-T020 all marked [P] can run in parallel (write tests first!)
- **Phase 3 US1 Models**: T021-T024 all marked [P] can run in parallel
- **Phase 3 US1 Unit Tests**: T031-T033 all marked [P] can run in parallel
- **Phase 4 US2 Tests**: T034-T037 all marked [P] can run in parallel
- **Phase 4 US2 Models**: T038-T039 all marked [P] can run in parallel
- **Phase 4 US2 Unit Tests**: T047-T048 all marked [P] can run in parallel
- **Phase 5 US3 Tests**: T049-T051 all marked [P] can run in parallel
- **Phase 5 US3 Frontend**: T056-T057 can run in parallel with backend tasks
- **Phase 6 Cross-Cutting**: T058, T060-T063 all marked [P] can run in parallel
- **Phase 7 Ingestion**: T064-T067 all marked [P] can run in parallel
- **Phase 8 Polish**: T068-T072, T074-T077 all marked [P] can run in parallel
- **User Stories**: Once Foundational complete, US1, US2, US3 can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T016: "Contract test for POST /api/v1/query in backend/tests/contract/test_query_api_contract.py"
Task T017: "Integration test for happy path (fully grounded) in backend/tests/integration/test_query_flow.py"
Task T018: "Integration test for partially grounded answer in backend/tests/integration/test_query_flow.py"
Task T019: "Integration test for speculative answer in backend/tests/integration/test_query_flow.py"
Task T020: "Integration test for LLM refusal handling in backend/tests/integration/test_query_flow.py"

# Launch all models for User Story 1 together:
Task T021: "Create QueryRequest model in backend/src/models/query.py"
Task T022: "Create SourceChunk model in backend/src/models/query.py"
Task T023: "Create QueryResponse model in backend/src/models/query.py"
Task T024: "Create VectorSearchResult model in backend/src/models/vector.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup → ✅ T001-T007
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories) → ✅ T008-T015
3. Complete Phase 3: User Story 1 → ✅ T016-T033
4. Complete Phase 7: Content Ingestion → ✅ T064-T067 (need data to test US1)
5. **STOP and VALIDATE**: Test User Story 1 independently with curl/pytest
6. Deploy/demo if ready

**MVP Scope**: Authenticated students can ask questions about chapters and receive grounded answers with source citations. This is the minimum viable product.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready ✅
2. Add User Story 1 + Content Ingestion → Test independently → Deploy/Demo (MVP! 🎯)
3. Add User Story 2 → Test independently → Deploy/Demo (better error handling)
4. Add User Story 3 → Test independently → Deploy/Demo (source transparency)
5. Add Phase 6 (Rate Limiting & Observability) → Production-ready
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together → ✅ T001-T015
2. Once Foundational is done:
   - Developer A: User Story 1 (T016-T033) + Content Ingestion (T064-T067)
   - Developer B: User Story 2 (T034-T048)
   - Developer C: User Story 3 (T049-T057)
3. Stories complete and integrate independently
4. Shared developer: Phase 6 Rate Limiting & Observability (T058-T063)
5. All developers: Phase 8 Polish (T068-T077)

---

## Task Count Summary

- **Phase 1 Setup**: 7 tasks (T001-T007)
- **Phase 2 Foundational**: 8 tasks (T008-T015) ⚠️ BLOCKS all stories
- **Phase 3 User Story 1 (P1)**: 18 tasks (T016-T033) 🎯 MVP
- **Phase 4 User Story 2 (P2)**: 15 tasks (T034-T048)
- **Phase 5 User Story 3 (P3)**: 9 tasks (T049-T057)
- **Phase 6 Rate Limiting & Observability**: 6 tasks (T058-T063)
- **Phase 7 Content Ingestion**: 4 tasks (T064-T067)
- **Phase 8 Polish**: 10 tasks (T068-T077)

**Total**: 77 tasks

**MVP Tasks** (minimum for demo): 37 tasks (Phase 1 + Phase 2 + Phase 3 + Phase 7 ingestion)

**Parallel Opportunities**: 42 tasks marked [P] can run in parallel (54% of all tasks)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label (US1, US2, US3) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests FAIL before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Constitution Compliance**: All tasks enforce 100% type hints (mypy), 90% test coverage (pytest-cov), standardized errors (ErrorCode enum), secure secrets (.env + .gitignore)
- **Alignment with Requirements**: All 19 functional requirements (FR-001 to FR-019) and 8 success criteria (SC-001 to SC-008) are covered across tasks
- **Test Traceability**: Contract tests (T016, T034), integration tests (T017-T020, T035-T037, T049-T051, T062), unit tests (T031-T033, T047-T048, T063) map to acceptance scenarios in spec.md
