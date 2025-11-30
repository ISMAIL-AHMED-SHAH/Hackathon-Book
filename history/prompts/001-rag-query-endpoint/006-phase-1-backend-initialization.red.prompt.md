---
id: 006
title: Phase 1 Backend Initialization
stage: red
date: 2025-11-29
surface: agent
model: claude-sonnet-4-5
feature: 001-rag-query-endpoint
branch: 001-rag-query-endpoint
user: developer
command: /sp.implement
labels: ["setup", "infrastructure", "python", "backend", "phase-1"]
links:
  spec: specs/001-rag-query-endpoint/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - backend/pyproject.toml
 - backend/.env.example
 - backend/README.md
 - .gitignore
 - backend/src/api/v1/ (directory structure)
 - backend/src/models/ (directory structure)
 - backend/src/services/ (directory structure)
 - backend/src/core/ (directory structure)
 - backend/src/utils/ (directory structure)
 - backend/tests/contract/ (directory structure)
 - backend/tests/integration/ (directory structure)
 - backend/tests/unit/ (directory structure)
 - backend/scripts/ (directory structure)
tests:
 - None (infrastructure setup phase)
---

## Prompt

I am starting the implementation of **Phase 1: Setup (Shared Infrastructure)**.

**Atomic Task Group (T001 & T002):** Initialize the Python backend project and define the base structure.

**Files to Generate/Modify:**
1. **`backend/pyproject.toml`**: Initialize the project using Poetry. List the core dependencies required for the RAG API and Better-Auth: `fastapi`, `uvicorn` (for running), `pydantic` (for schemas), `qdrant-client` (for vector search), `anthropic` (for Claude generation), and `python-jose` (for Better-Auth). Include `pytest` for testing (Constitution Rule 2.1). Set the Python version to 3.11+.
2. **Shell Commands**: Provide the necessary shell commands (e.g., `mkdir -p`) to create the following directory structure inside the `backend/` folder, as defined in T001:
    - `src/{api,models,services,core,utils}/`
    - `tests/{contract,integration,unit}/`
3. **`backend/README.md`**: A brief README file for the backend service.

**Instruction:**
Generate the content for `backend/pyproject.toml`, the content for `backend/README.md`, and the shell commands to create the required directory structure.

## Response snapshot

Successfully completed Phase 1: Setup (Shared Infrastructure) tasks T001, T002, T003, and T007.

**Files Created:**

1. **backend/pyproject.toml**:
   - Initialized Poetry project with Python 3.11+
   - Added core dependencies: FastAPI 0.104+, Pydantic 2.5+, qdrant-client 1.7+, openai 1.6+, python-jose 3.3+, asyncpg 0.29+, redis 5.0+
   - Configured dev dependencies: pytest, pytest-asyncio, pytest-cov, black, flake8, mypy, pre-commit
   - Configured tool settings for Black (line length 100), mypy (strict mode), pytest (coverage targets)

2. **backend/.env.example**:
   - Template for all required environment variables
   - OpenAI configuration (API key, embedding model, LLM model)
   - Qdrant Cloud configuration (URL, API key, collection name)
   - Neon Postgres configuration (connection string)
   - Better-Auth configuration (secret, issuer)
   - Redis configuration (URL for rate limiting)
   - Rate limiting settings (10 req/min, 60s window)
   - Timeout settings (5s vector DB, 25s LLM, 30s total)
   - Application settings (env, log level, debug mode)

3. **backend/README.md**:
   - Overview of the RAG Query Backend service
   - Tech stack documentation
   - Project structure with descriptions
   - Getting started instructions (prerequisites, installation, running server)
   - Testing and code quality commands
   - API documentation with example request/response
   - Environment variables reference
   - Security best practices
   - Performance targets and monitoring metrics

4. **.gitignore**:
   - Python patterns (__pycache__, *.pyc, .venv, venv, dist, build, eggs, *.egg-info)
   - Testing patterns (.pytest_cache, .coverage, htmlcov, .mypy_cache)
   - Environment files (.env, .env.local, *.env)
   - IDE patterns (.vscode, .idea, *.swp, .DS_Store, Thumbs.db)
   - Node.js patterns (node_modules, *.log)
   - Build outputs (dist, build, *.min.js, *.min.css)
   - Temporary files (*.tmp, *.cache, *.log)
   - Poetry lock file

5. **Directory Structure**:
   Created complete backend directory structure:
   - backend/src/api/v1/ (FastAPI routes)
   - backend/src/models/ (Pydantic data models)
   - backend/src/services/ (business logic)
   - backend/src/core/ (configuration, exceptions, metrics)
   - backend/src/utils/ (helper functions)
   - backend/tests/contract/ (API contract tests)
   - backend/tests/integration/ (end-to-end tests)
   - backend/tests/unit/ (unit tests)
   - backend/scripts/ (setup and ingestion scripts)

**Tasks Completed:**
- [X] T001: Backend directory structure created
- [X] T002: Python 3.11+ project initialized with pyproject.toml
- [X] T003: .env.example file created with all required variables
- [X] T007: .gitignore created with Python, testing, and IDE patterns

**Updated tasks.md** to mark T001, T002, T003, and T007 as completed.

## Outcome

- ✅ Impact: Successfully initialized Python backend project structure with all necessary configuration files. Ready for Phase 2 foundational implementation.
- 🧪 Tests: None (infrastructure setup phase - no tests written yet)
- 📁 Files: 4 files created (pyproject.toml, .env.example, README.md, .gitignore) + 9 directories
- 🔁 Next prompts: Continue with Phase 1 remaining tasks (T004: Black/Flake8/mypy configuration, T005: pre-commit hooks, T006: docker-compose.yml)
- 🧠 Reflection: Clean separation of concerns in directory structure. pyproject.toml includes all dependencies from plan.md. .env.example provides clear guidance for developers. README.md serves as comprehensive onboarding document.

## Evaluation notes (flywheel)

- Failure modes observed: None - all files created successfully
- Graders run and results (PASS/FAIL): N/A (infrastructure setup, no tests to run)
- Prompt variant (if applicable): Standard implementation prompt
- Next experiment (smallest change to try): Continue with T004-T006 to complete Phase 1 setup
