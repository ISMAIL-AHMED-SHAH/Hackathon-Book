---
id: 003
title: Docusaurus Textbook Task Generation
stage: tasks
date: 2025-11-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-docusaurus-textbook
branch: 001-docusaurus-textbook
user: user
command: /sp.tasks
labels: ["tasks", "implementation", "user-stories", "mvp", "docusaurus"]
links:
  spec: specs/001-docusaurus-textbook/spec.md
  plan: specs/001-docusaurus-textbook/plan.md
  tasks: specs/001-docusaurus-textbook/tasks.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-docusaurus-textbook/tasks.md
tests:
 - Manual testing checklist embedded in tasks (no automated tests per constitution)
---

## Prompt

```text
User requested task generation after planning phase completed.

Command invoked: `/sp.tasks`
User input: (empty - proceeded automatically)

Context:
- Specification completed with 5 user stories (3 P1, 2 P2)
- Implementation plan completed with architecture decisions
- Design documents available: research.md, data-model.md, contracts/, quickstart.md
- Hackathon deadline: ~18 hours remaining
- Target: 100/100 base hackathon points
```

## Response

Created comprehensive task list for Docusaurus Physical AI Textbook Platform organized by user story priorities.

**Task Generation Deliverables:**

**Tasks.md Structure**:
- Created `specs/001-docusaurus-textbook/tasks.md` with 85 tasks organized into 8 phases
- All tasks follow strict checklist format: `- [ ] [ID] [P?] [Story] Description with file path`
- Tasks organized by user story to enable independent implementation and testing
- 35 tasks (41%) marked [P] for parallel execution
- Clear dependencies and execution order documented

**Phase Breakdown**:

1. **Phase 1: Setup** (7 tasks)
   - Initialize Docusaurus project with TypeScript
   - Install dependencies (@floating-ui/react, dotenv)
   - Configure environment files and TypeScript
   - Create type definitions for all entities

2. **Phase 2: Foundational** (7 tasks) - **BLOCKS all user stories**
   - Create chapter mapper plugin with all 10 chapter IDs
   - Create custom hooks (useChapterId, useApiClient, useTextSelection)
   - Configure Docusaurus for GitHub Pages
   - Setup syntax highlighting for Python/Bash/YAML

3. **Phase 3: User Story 1 - Read Interactive Textbook** (18 tasks) - **P1 🎯 MVP**
   - Write intro landing page
   - Create 4 module directories with metadata
   - Write 10 chapters (nodes, topics, services, urdf, gazebo-basics, sensors, isaac-sim, isaac-ros, voice-commands, capstone)
   - All chapters: 3-5 concepts, B1 English, ≥1 code example
   - Configure sidebars and navigation
   - Local testing
   - **Independent test**: Navigate site, browse TOC, read chapters

4. **Phase 4: User Story 2 - RAG Chatbot** (11 tasks) - **P1**
   - Create ChatbotWidget component with state management
   - Implement API integration (POST /v1/query)
   - Add response rendering (answer + source citations)
   - Handle loading states and errors (400/404/429/500/503)
   - Swizzle Root component to inject widget
   - Testing (query submission, error handling, chapter context)
   - **Independent test**: Ask question, receive answer with citations

5. **Phase 5: User Story 3 - Selected Text Search** (10 tasks) - **P2**
   - Create SelectionTooltip component with Floating UI
   - Implement text selection detection
   - Add "Ask about this" action
   - Integrate with ChatbotWidget
   - Handle viewport edge cases
   - Mobile testing
   - **Independent test**: Highlight text, click tooltip, query submitted

6. **Phase 6: User Story 4 - GitHub Pages Deployment** (14 tasks) - **P1**
   - Create GitHub Actions workflow (.github/workflows/deploy.yml)
   - Configure build and deploy jobs
   - Update docusaurus.config.ts for GitHub Pages (baseUrl, url, etc.)
   - Test local build
   - Push to GitHub and enable Pages
   - Monitor deployment
   - Test deployed site
   - **Independent test**: Visit GitHub Pages URL, site loads correctly

7. **Phase 7: User Story 5 - Chapter Navigation** (5 tasks) - **P2**
   - Verify Docusaurus doc pagination enabled (default feature)
   - Test Next/Previous links on all chapters
   - Verify first/last chapter edge cases
   - Test sequential flow
   - **Independent test**: Click Next/Previous, navigate sequentially

8. **Phase 8: Polish & Cross-Cutting Concerns** (13 tasks)
   - Dark mode support
   - Mobile responsiveness optimization
   - Logo and favicon
   - Cross-browser testing (Chrome, Firefox, Safari, Edge)
   - Lighthouse accessibility audit (target: ≥90)
   - Performance testing (page load <3s, chatbot <10s)
   - Educational standards verification (≤5 concepts, B1 English)
   - Code cleanup
   - Documentation updates
   - Final validation via quickstart.md

**User Story Mapping**:

All tasks labeled with [Story] markers (US1, US2, US3, US4, US5) for traceability:
- **US1** (Read Textbook): 18 tasks - Textbook content creation
- **US2** (Chatbot): 11 tasks - RAG integration
- **US3** (Selected Text): 10 tasks - Text selection UX
- **US4** (Deployment): 14 tasks - GitHub Pages
- **US5** (Navigation): 5 tasks - Next/Previous links
- **Setup/Foundational/Polish**: 27 tasks - Infrastructure

**Dependencies Documented**:

- Setup → Foundational (sequential)
- Foundational → **BLOCKS** all user stories
- US1, US2, US4: Independent after Foundational
- US3: Depends on US2 (requires ChatbotWidget)
- US5: Depends on US1 (requires chapters)
- Polish: Depends on all user stories

**Parallel Execution Examples**:

- **US1 chapter writing**: 15 tasks can run in parallel (T015-T029)
- **Setup tasks**: 7 tasks mostly parallel
- **Foundational hooks**: 5 tasks parallel (T010-T014)
- **Polish checks**: 10 tasks parallel (T073-T082)

**Implementation Strategies Provided**:

1. **MVP First** (US1 + US2 + US4 = 90 points):
   - Day 1: Setup + Foundational + US1 (write chapters) → 6-8 hours
   - Day 2: US2 (chatbot) + US4 (deployment) → 4-6 hours
   - **Result**: Deployed textbook with chatbot = 90 hackathon points

2. **Incremental to 100 points**:
   - Add US3 (selected text) → +10 points = **100 points** ✅
   - Add US5 (navigation) → Enhanced UX
   - Polish phase → Final quality

3. **Parallel Team Strategy**:
   - Developer A: US1 (chapter writing)
   - Developer B: US2 (chatbot widget)
   - Developer C: US4 (deployment)
   - Converge: US3 integration

**Recommended Execution Order (Solo)**:

1. T001-T014: Setup + Foundational (~2 hours)
2. T015-T032: US1 - Write 10 chapters (~5-6 hours with AI assistance)
3. T033-T043: US2 - Build chatbot (~3 hours)
4. T054-T067: US4 - Deploy to GitHub Pages (~2 hours)
5. **Checkpoint**: MVP deployed (90 points)
6. T044-T053: US3 - Add selected text search (~2 hours)
7. T073-T085: Polish (~1 hour)
8. **Final**: 100 points achieved

**Total time**: 12-17 hours (achievable within 18-hour deadline!)

**Task Count Summary**:

- Total tasks: **85**
- Parallel tasks: **35** (41%)
- MVP scope (US1+US2+US4): **50 tasks** → 90 points
- Full scope (all stories): **85 tasks** → 100 points

**Success Criteria Mapped**:

Every success criterion from spec.md mapped to specific tasks:
- SC-001 (page load <2s): US1 T032
- SC-002 (chatbot <10s): US2 T041
- SC-003 (selected text): US3 T051
- SC-004 (GitHub Pages <3s): US4 T066
- SC-005 (answer quality): US2 T041
- SC-006 (Lighthouse 90+): Polish T079
- SC-007 (error-free sessions): Polish T085
- SC-008 (cross-browser): Polish T078
- SC-009 (code examples): US1 T015-T029
- SC-010 (mobile chatbot): Polish T074

**Functional Requirements Covered**:

All FR-001 to FR-020 covered:
- FR-001 (≥5 chapters): US1 creates 10 chapters ✅
- FR-004 (chatbot widget): US2 ✅
- FR-007 (selected text): US3 ✅
- FR-010 (GitHub Pages): US4 ✅
- FR-011 (responsive): Polish T074 ✅
- FR-012 (search): Docusaurus default ✅
- FR-013 (code examples): US1 all chapters ✅
- FR-014 (≤5 concepts): US1 guideline ✅
- FR-015 (B1 English): US1 guideline ✅
- FR-016 (error handling): US2 T038 ✅
- FR-017 (loading indicator): US2 T037 ✅
- FR-020 (dark mode): Polish T073 ✅

**Testing Approach**:

- No automated tests per constitution Gate 2.1 (deferred for hackathon MVP)
- Manual testing tasks embedded in each user story phase
- Independent test criteria defined for each story
- Validation checkpoints after each phase
- Final end-to-end validation via quickstart.md (T085)

**Critical Path Identified**:

- **Bottleneck**: Chapter content writing (T015-T029) = 5-10 hours
- **Solution**: Use AI assistance (ChatGPT) to draft chapters, then review/edit
- **Mitigation**: Prioritize P1 chapters (ROS 2, Gazebo, Isaac, VLA basics)
- **Quality**: Enforce ≤5 concepts, B1 English, ≥1 code example per chapter

**Hackathon Scoring Alignment**:

- Backend RAG API: 30 points ✅ (already complete)
- Docusaurus textbook (5+ chapters): 30 points → US1 (10 chapters)
- Embedded chatbot widget: 25 points → US2
- Selected text search: 10 points → US3
- GitHub Pages deployment: 5 points → US4
- **Total**: 100/100 base points ✅

**Next Steps**:

1. ✅ Run `/sp.implement` to begin systematic task execution
2. ✅ Start with Phase 1: Setup (T001-T007)
3. ✅ Complete Phase 2: Foundational (T008-T014) before user stories
4. ✅ Execute US1 (textbook) + US2 (chatbot) + US4 (deployment) for MVP
5. ✅ Add US3 (selected text) to reach 100 points
6. ✅ Polish and submit to hackathon

**Status:** ✅ TASKS COMPLETE - Ready for implementation

The task list is comprehensive, well-organized, and executable. Each task has a clear description, file path, and dependencies. The user story organization enables independent implementation and testing. The parallel opportunities maximize efficiency. The MVP strategy provides a clear path to 90 points quickly, with incremental delivery to 100 points.

**Format Validation**: ✅ All 85 tasks follow the required checklist format:
- Checkbox: `- [ ]`
- Task ID: T001-T085 (sequential)
- [P] marker: 35 tasks marked for parallel execution
- [Story] label: 64 tasks labeled with US1-US5
- File paths: All implementation tasks include exact file paths
- Dependencies: Clear execution order documented

Ready to implement the Docusaurus Physical AI Textbook Platform!
