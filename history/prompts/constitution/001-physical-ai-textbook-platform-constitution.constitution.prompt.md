---
id: 001
title: Physical AI Textbook Platform Constitution
stage: constitution
date: 2025-11-28
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["constitution", "principles", "governance", "initial-ratification"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

```text
# Project Constitution: Physical AI Textbook Platform

## 1. Code Quality & Standards
**Rule 1.1 (Type Safety):** All Python code (FastAPI, RAG logic) MUST use 100% type hints, validated by Mypy or a similar tool.
**Rule 1.2 (Linter):** All code MUST pass a single-line formatter (e.g., Black) and a standard linter (e.g., Flake8) with zero errors.

## 2. Testing Requirements
**Rule 2.1 (Test Coverage):** All API endpoints and core logic functions MUST maintain a minimum of 90% test coverage.
**Rule 2.2 (Specification-Anchored Tests):** Every Acceptance Criterion defined in a Specification MUST be traceable to at least one test case.

## 3. Error Handling & API Contracts
**Rule 3.1 (Standardized Errors):** All backend API errors MUST return a standardized JSON object with `{"error_code": "...", "message": "..."}`.
**Rule 3.2 (HTTP Status Codes):** HTTP status codes MUST be used semantically (e.g., 2xx for success, 4xx for client errors, 5xx for server errors). Specifically, `401 Unauthorized` for missing/invalid auth and `403 Forbidden` for valid auth but insufficient permissions.

## 4. Educational Content Standards (Docusaurus)
**Rule 4.1 (Cognitive Load):** Each textbook chapter (markdown file) MUST introduce a maximum of 5 new technical concepts.
**Rule 4.2 (Proficiency Level):** All content MUST be written for a B1 proficiency level.
**Rule 4.3 (Media):** All chapters MUST include at least one concrete runnable code example.

## 5. Security & Authentication
**Rule 5.1 (Authentication):** All `POST` and `PUT` endpoints MUST be authenticated using the **Better-Auth** service via a valid Bearer Token in the `Authorization` header.
```

## Response snapshot

Created the Physical AI Textbook Platform Constitution v1.0.0 with five core principles:

1. **Code Quality & Standards**: Enforcing 100% type hints (Mypy validation) and zero-error linting (Black + Flake8) for all Python code in FastAPI backend and RAG pipelines.

2. **Testing Requirements**: Mandating 90% test coverage for all API endpoints and core logic, with every acceptance criterion traceable to at least one test case.

3. **Error Handling & API Contracts**: Standardizing all API errors as `{"error_code": "...", "message": "..."}` with semantic HTTP status codes (401 for auth failures, 403 for permission denials).

4. **Educational Content Standards**: Limiting cognitive load to 5 concepts per chapter, targeting B1 proficiency level, and requiring at least one runnable code example per chapter in Docusaurus.

5. **Security & Authentication**: Requiring Better-Auth service authentication for all POST/PUT endpoints via Bearer tokens, with strict environment variable management for credentials.

Added Development Workflow section mandating SDD workflow (Constitution → Specify → Clarify → Plan → Tasks → Implement) and TDD for critical features (RAG pipeline, authentication, content generation).

Added Governance section specifying amendment procedures and compliance verification requirements.

## Outcome

- ✅ Impact: Initial constitution ratified (v1.0.0) establishing governance framework for Physical AI Textbook Platform project
- 🧪 Tests: None (constitution is governance document)
- 📁 Files: Created .specify/memory/constitution.md with complete principles
- 🔁 Next prompts: Feature specifications (/sp.specify) for RAG chatbot, Docusaurus integration, Better-Auth implementation, and educational content generation
- 🧠 Reflection: Constitution successfully bridges educational platform requirements (cognitive load, B1 proficiency) with technical standards (type safety, testing, security). Principles are measurable and enforceable.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (initial constitution)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
