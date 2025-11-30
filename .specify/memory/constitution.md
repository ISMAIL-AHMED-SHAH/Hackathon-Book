<!--
Sync Impact Report:
- Version: 0.0.0 → 1.0.0
- Modified principles: N/A (initial ratification)
- Added sections: 5 principle sections (Code Quality & Standards, Testing Requirements, Error Handling & API Contracts, Educational Content Standards, Security & Authentication)
- Removed sections: None
- Templates requiring updates:
  ✅ plan-template.md: Updated constitution check alignment
  ✅ spec-template.md: Aligned with requirements standards
  ✅ tasks-template.md: Task categorization reflects principles
- Follow-up TODOs: None
-->

# Physical AI Textbook Platform Constitution

## Core Principles

### I. Code Quality & Standards

All Python code (FastAPI backend, RAG pipeline logic) MUST use 100% type hints validated by Mypy or equivalent static type checker. All code MUST pass a single-line formatter (Black) and a standard linter (Flake8) with zero errors before commit.

**Rationale**: Type safety prevents runtime errors in production, especially critical for RAG pipelines processing educational content. Consistent formatting ensures maintainability across the educational content generation system and API codebase.

### II. Testing Requirements

All API endpoints and core logic functions MUST maintain a minimum of 90% test coverage. Every Acceptance Criterion defined in a feature specification MUST be traceable to at least one test case that validates that criterion.

**Rationale**: High test coverage ensures reliability of the textbook platform and RAG chatbot. Specification-anchored tests guarantee that educational features deliver on their promises and learning outcomes are measurable.

### III. Error Handling & API Contracts

All backend API errors MUST return a standardized JSON object with the structure `{"error_code": "...", "message": "..."}`. HTTP status codes MUST be used semantically: 2xx for success, 4xx for client errors, 5xx for server errors. Specifically, `401 Unauthorized` for missing/invalid authentication tokens and `403 Forbidden` for valid authentication but insufficient permissions.

**Rationale**: Standardized error handling enables the frontend (Docusaurus) and RAG chatbot to provide clear, actionable feedback to students. Semantic HTTP status codes ensure correct error recovery and debugging in the learning platform.

### IV. Educational Content Standards (Docusaurus)

Each textbook chapter (markdown file) MUST introduce a maximum of 5 new technical concepts to manage cognitive load. All content MUST be written for a B1 proficiency level to ensure accessibility. All chapters MUST include at least one concrete, runnable code example demonstrating the concepts taught.

**Rationale**: Cognitive load limits prevent overwhelming students learning Physical AI and Robotics. B1 proficiency ensures global accessibility. Runnable examples enable hands-on learning, critical for mastering ROS 2, Gazebo, and NVIDIA Isaac platforms.

### V. Security & Authentication

All `POST` and `PUT` endpoints MUST be authenticated using the Better-Auth service via a valid Bearer Token in the `Authorization` header. User credentials and API keys MUST NEVER be hardcoded; they MUST be stored in environment variables and managed via `.env` files excluded from version control.

**Rationale**: Authentication protects user data and personalization features. Better-Auth integration enables signup/signin flows that collect user background for content personalization. Secure credential management prevents exposure of database connection strings and API keys for OpenAI/Qdrant services.

## Development Workflow

All feature work MUST follow the Spec-Driven Development (SDD) workflow: Constitution → Specify → Clarify → Plan → Tasks → Implement. Each phase MUST produce the required artifacts (spec.md, plan.md, tasks.md) before implementation begins.

**Pull Request Requirements**: All PRs MUST include links to the corresponding specification and demonstrate that acceptance criteria are met. Code reviews MUST verify compliance with all five core principles before approval.

**Test-Driven Development**: For critical features (RAG pipeline, authentication, content generation), tests MUST be written first, approved by stakeholders, fail initially, then implementation MUST make them pass (Red-Green-Refactor cycle).

## Governance

This constitution supersedes all other practices and guidelines. Amendments require:
1. Documentation of the proposed change with rationale
2. Approval from project maintainers
3. Migration plan for existing code that violates the new rules

All PRs and code reviews MUST verify compliance with this constitution. Any introduction of complexity (additional abstractions, new dependencies, architectural patterns) MUST be justified against the principles above.

**Version**: 1.0.0 | **Ratified**: 2025-11-28 | **Last Amended**: 2025-11-28
