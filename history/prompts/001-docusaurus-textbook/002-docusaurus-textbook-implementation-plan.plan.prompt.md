---
id: 002
title: Docusaurus Textbook Implementation Plan
stage: plan
date: 2025-11-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-docusaurus-textbook
branch: 001-docusaurus-textbook
user: user
command: /sp.plan
labels: ["planning", "frontend", "docusaurus", "architecture", "chatbot"]
links:
  spec: specs/001-docusaurus-textbook/spec.md
  plan: specs/001-docusaurus-textbook/plan.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-docusaurus-textbook/plan.md
 - specs/001-docusaurus-textbook/research.md
 - specs/001-docusaurus-textbook/data-model.md
 - specs/001-docusaurus-textbook/quickstart.md
 - specs/001-docusaurus-textbook/contracts/chatbot-api.yaml
tests:
 - Manual testing checklist defined in plan.md
---

## Prompt

```text
User requested to proceed with planning phase after specification was completed.

Command invoked: `/sp.plan`
User input: "sure proceed"

Context:
- Specification completed and validated (all checklist items passed)
- Backend RAG API is 100% functional
- Need to design frontend architecture for Docusaurus textbook with chatbot integration
- Hackathon deadline: ~18 hours remaining
```

## Response

Created comprehensive implementation plan for Docusaurus Physical AI Textbook Platform.

**Planning deliverables:**

**Phase 0: Research (Completed)**
- Created `specs/001-docusaurus-textbook/research.md` with detailed findings on 5 technical topics:
  1. Chatbot Widget Integration → Root component swizzling pattern
  2. Chapter ID Detection → Custom plugin + useLocation() hook
  3. Text Selection Detection → Selection API + Floating UI
  4. Environment Configuration → customFields + .env files
  5. GitHub Pages Deployment → GitHub Actions workflow

**Phase 1: Design (Completed)**
- Created `specs/001-docusaurus-textbook/data-model.md` defining:
  - 6 core entities (Chapter, Module, ChatbotQuery, ChatbotResponse, SourceCitation, TextSelection)
  - Client-side state management patterns (chatbot widget state, selection tooltip state, chapter context)
  - API contracts aligning with backend QueryRequest/QueryResponse schemas
  - Content structure (10 chapters across 4 modules)
  - TypeScript type definitions for all entities

- Created `specs/001-docusaurus-textbook/contracts/chatbot-api.yaml`:
  - OpenAPI 3.0 specification for backend RAG API
  - Full request/response schemas with examples
  - Error response definitions (400, 404, 429, 500, 503)
  - Health check endpoint spec

- Created `specs/001-docusaurus-textbook/quickstart.md`:
  - Step-by-step developer setup guide (10 steps)
  - Complete code examples for all components
  - Environment configuration instructions
  - GitHub Pages deployment workflow
  - Troubleshooting guide
  - Estimated setup time: 30 minutes

- Created `specs/001-docusaurus-textbook/plan.md`:
  - Technical context (TypeScript 5.x, Docusaurus v3.x, React 18.x, Floating UI)
  - Constitution check (all gates passed or deferred with justification)
  - Project structure (frontend/ directory with Docusaurus layout)
  - 6 architecture decisions documented with rationale and alternatives
  - Integration points (backend API, chapter ID mapping, content structure)
  - Deployment strategy (development + production)
  - Performance optimization (page load, chatbot response, mobile responsiveness)
  - Risk mitigation (4 identified risks with contingency plans)
  - Testing strategy (manual testing checklist)
  - Timeline estimate (12-15 hours remaining work)

**Architecture Decisions:**

1. **Static Site Generation with Docusaurus**
   - Decision: Docusaurus v3 "classic" preset with TypeScript
   - Rationale: Purpose-built for docs sites; provides navigation, search, dark mode, responsive design out-of-box
   - Alternatives rejected: Next.js (too complex), VitePress (Vue-based), Plain HTML (lacks features)

2. **Persistent Chatbot Widget**
   - Decision: Root component swizzling (`src/theme/Root.tsx`)
   - Rationale: Root never unmounts during navigation, preserving widget state
   - Alternatives rejected: Footer swizzling (loses state), client modules (no React hooks), manual injection (doesn't scale)

3. **Chapter Context Detection**
   - Decision: Custom plugin generates `chapter-map.json` + useLocation() hook
   - Rationale: Build-time mapping avoids runtime overhead; useLocation() reactive to route changes
   - Alternatives rejected: Hardcoded mappings (doesn't scale), file system traversal (SSR incompatible)

4. **Text Selection Detection**
   - Decision: Selection API with mouseup/selectionchange listeners + Floating UI
   - Rationale: Standard browser feature; captures keyboard selection; handles edge cases (viewport boundaries)
   - Alternatives rejected: Native context menu (limited customization), manual positioning (doesn't handle edge cases)

5. **Environment Configuration**
   - Decision: Docusaurus customFields + .env files at build time
   - Rationale: Official Docusaurus pattern; supports different API URLs per environment
   - Alternatives rejected: REACT_APP_ only (less integrated), runtime config JSON (more complex)

6. **GitHub Pages Deployment**
   - Decision: GitHub Actions workflow with Docusaurus build script
   - Rationale: Modern CI/CD approach; better logs; supports environment variables
   - Alternatives rejected: npm run deploy (deprecated), Vercel/Netlify (not GitHub Pages requirement)

**Technical Stack:**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Static Site Generator | Docusaurus v3.x | React-based documentation framework |
| UI Framework | React 18.x | Component-based UI |
| Styling | CSS Modules | Scoped component styles |
| Tooltip Positioning | Floating UI v0.24+ | Robust floating element positioning |
| HTTP Client | Fetch API | Native browser API for backend calls |
| Environment Config | dotenv v16+ | Environment variable management |
| Routing | @docusaurus/router | Client-side routing |
| Deployment | GitHub Actions | CI/CD pipeline for GitHub Pages |

**Project Structure:**

```
hackathon-book/
├── backend/          # EXISTING (100% complete)
└── frontend/         # NEW (to be implemented)
    ├── docs/         # Markdown chapters (10 chapters across 4 modules)
    ├── src/
    │   ├── components/   # ChatbotWidget, SelectionTooltip
    │   ├── hooks/        # useChapterId, useApiClient, useTextSelection
    │   ├── theme/        # Root.tsx (swizzled)
    │   └── types/        # TypeScript definitions
    ├── plugins/          # chapter-mapper-plugin.js
    ├── docusaurus.config.ts
    └── .env.development / .env.production
```

**Integration Flow:**

1. User types question → ChatbotWidget component
2. useChapterId() detects current chapter from URL
3. useApiClient() sends POST /v1/query to backend
4. Backend processes RAG pipeline (Qdrant + GPT-4)
5. Frontend displays answer + source citations
6. Error handling for 400/404/429/500/503 responses

**Constitution Compliance:**

- ✅ Code Quality: Using TypeScript (type safety equivalent to Python type hints)
- ✅ Testing: Manual testing checklist defined; acceptance scenarios traceable to tests
- ✅ Error Handling: Backend standardized error responses; frontend handles all error codes
- ✅ Educational Content: B1 proficiency, ≤5 concepts/chapter, ≥1 code example/chapter
- ⚠️ Security: Authentication deferred (bonus feature); using guest-user for MVP

**Performance Targets:**

- Page load: <2 seconds
- Chatbot response: <10 seconds (backend ~6-8s + network overhead)
- Tooltip display: <100ms after selection
- Lighthouse accessibility: ≥90

**Risk Mitigation:**

- Risk 1: Backend unavailable → Health check + fallback message
- Risk 2: GitHub Pages build fails → Test locally + Vercel contingency
- Risk 3: Content not ready → Prioritize P1 chapters, use AI assistance
- Risk 4: Mobile selection issues → Test on Safari/Chrome, provide paste alternative

**Timeline Estimate:**

Total: 12-15 hours remaining work (achievable before deadline)

Critical path: Chapter content writing (5-10 hours)

**Hackathon Scoring Alignment:**

- Backend RAG API: 30 points ✅ (complete)
- Docusaurus textbook (5+ chapters): 30 points 🎯
- Embedded chatbot widget: 25 points 🎯
- Selected text search: 10 points 🎯
- GitHub Pages deployment: 5 points 🎯
- **Total**: 100/100 base points

**Next Steps:**

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Run `/sp.implement` to execute tasks systematically
3. Write textbook chapters (prioritize ROS 2, Gazebo, Isaac, VLA)
4. Test chatbot integration locally
5. Deploy to GitHub Pages
6. Submit to hackathon

**Status:** ✅ PLANNING COMPLETE - Ready for task generation

All Phase 0 and Phase 1 deliverables completed:
- ✅ research.md (5 technical decisions with implementation patterns)
- ✅ data-model.md (6 entities, state management, API contracts)
- ✅ contracts/chatbot-api.yaml (OpenAPI spec)
- ✅ quickstart.md (developer guide with code examples)
- ✅ plan.md (comprehensive architecture and deployment strategy)

The implementation plan provides clear guidance for building the Docusaurus frontend with all required features for hackathon success.
