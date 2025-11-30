# Tasks: Docusaurus Physical AI Textbook Platform

**Input**: Design documents from `specs/001-docusaurus-textbook/`
**Prerequisites**: plan.md (architecture), spec.md (user stories), research.md (technical decisions), data-model.md (entities), contracts/ (API spec), quickstart.md (implementation guide)

**Tests**: Manual testing only (no automated test tasks per constitution Gate 2.1 - deferred for hackathon MVP)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/`, `frontend/docs/`, `frontend/plugins/`
- **Configuration**: `frontend/docusaurus.config.ts`, `frontend/.env.development`
- **Deployment**: `.github/workflows/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Docusaurus configuration

- [X] T001 Initialize Docusaurus project with TypeScript in frontend/ directory using `npx create-docusaurus@latest frontend classic --typescript`
- [X] T002 [P] Install dependencies: `@floating-ui/react` and `dotenv` in frontend/package.json
- [X] T003 [P] Configure docusaurus.config.ts with GitHub Pages deployment settings (url, baseUrl, organizationName, projectName)
- [X] T004 [P] Create environment files: frontend/.env.development (API_URL=http://localhost:8000) and frontend/.env.production
- [X] T005 [P] Update frontend/.gitignore to exclude .env.production and .env.development.local
- [X] T006 [P] Create frontend/tsconfig.json with strict TypeScript settings
- [X] T007 [P] Create TypeScript type definitions in frontend/src/types/index.ts (ChatbotQuery, ChatbotResponse, SourceCitation, TextSelection, etc.)

**Checkpoint**: Docusaurus project initialized, dependencies installed, configuration files created

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Create chapter mapper plugin in frontend/plugins/chapter-mapper-plugin.js with chapter ID mapping for all 10 chapters
- [X] T009 Register chapter-mapper-plugin in frontend/docusaurus.config.ts plugins array
- [X] T010 [P] Create useChapterId hook in frontend/src/hooks/useChapterId.ts using @docusaurus/router and plugin data
- [X] T011 [P] Create useApiClient hook in frontend/src/hooks/useApiClient.ts with fetch wrapper, timeout handling, and error responses
- [X] T012 [P] Create useTextSelection hook in frontend/src/hooks/useTextSelection.ts using Selection API with mouseup and selectionchange listeners
- [X] T013 [P] Update frontend/docusaurus.config.ts customFields to load API URL and timeout from environment variables using dotenv
- [X] T014 [P] Configure Prism theme in frontend/docusaurus.config.ts to support Python, Bash, YAML syntax highlighting

**Checkpoint**: Foundation ready - custom hooks created, plugin registered, configuration complete. User story implementation can now begin.

---

## Phase 3: User Story 1 - Read Interactive Textbook Content (Priority: P1) 🎯 MVP

**Goal**: Students can access structured educational content organized by modules in a web-based textbook format

**Independent Test**: Navigate to deployed site, browse table of contents, read at least one complete chapter with formatted content, code blocks, and responsive layout

### Implementation for User Story 1

- [X] T015 [P] [US1] Create frontend/docs/intro.md landing page with course overview and module descriptions
- [X] T016 [P] [US1] Create module directory frontend/docs/module-1-ros2/ with _category_.json metadata (title: "Module 1: ROS 2 Fundamentals", position: 1)
- [X] T017 [P] [US1] Write chapter frontend/docs/module-1-ros2/nodes.md (ROS 2 Nodes - 3-5 concepts, B1 English, ≥1 code example, sidebar_position: 1)
- [X] T018 [P] [US1] Write chapter frontend/docs/module-1-ros2/topics.md (ROS 2 Topics & Pub/Sub - 3-5 concepts, B1 English, ≥1 code example, sidebar_position: 2)
- [X] T019 [P] [US1] Write chapter frontend/docs/module-1-ros2/services.md (ROS 2 Services & Actions - 3-5 concepts, B1 English, ≥1 code example, sidebar_position: 3)
- [X] T020 [P] [US1] Write chapter frontend/docs/module-1-ros2/urdf.md (Robot Description with URDF - 3-5 concepts, B1 English, ≥1 code example, sidebar_position: 4)
- [X] T021 [P] [US1] Create module directory frontend/docs/module-2-gazebo/ with _category_.json metadata (title: "Module 2: Gazebo Simulation", position: 2)
- [X] T022 [P] [US1] Write chapter frontend/docs/module-2-gazebo/simulation-basics.md (Gazebo Basics - 3-5 concepts, B1 English, ≥1 code example, sidebar_position: 1)
- [X] T023 [P] [US1] Write chapter frontend/docs/module-2-gazebo/sensors.md (Simulating Sensors - 3-5 concepts, B1 English, ≥1 code example, sidebar_position: 2)
- [X] T024 [P] [US1] Create module directory frontend/docs/module-3-isaac/ with _category_.json metadata (title: "Module 3: NVIDIA Isaac", position: 3)
- [X] T025 [P] [US1] Write chapter frontend/docs/module-3-isaac/isaac-sim.md (Isaac Sim Overview - 3-5 concepts, B1 English, ≥1 code example, sidebar_position: 1)
- [X] T026 [P] [US1] Write chapter frontend/docs/module-3-isaac/isaac-ros.md (Isaac ROS Integration - 3-5 concepts, B1 English, ≥1 code example, sidebar_position: 2)
- [X] T027 [P] [US1] Create module directory frontend/docs/module-4-vla/ with _category_.json metadata (title: "Module 4: Vision-Language-Action", position: 4)
- [X] T028 [P] [US1] Write chapter frontend/docs/module-4-vla/voice-commands.md (Voice Commands with Whisper - 3-5 concepts, B1 English, ≥1 code example, sidebar_position: 1)
- [X] T029 [P] [US1] Write chapter frontend/docs/module-4-vla/capstone.md (Capstone Project - 3-5 concepts, B1 English, ≥1 code example, sidebar_position: 2)
- [X] T030 [US1] Configure frontend/sidebars.ts to organize all 10 chapters hierarchically by module
- [X] T031 [US1] Update frontend/docusaurus.config.ts navbar to add "Textbook" link pointing to docs sidebar
- [X] T032 [US1] Test locally with `npm run build` - verify navigation sidebar shows all modules/chapters, content renders correctly, code blocks have syntax highlighting, responsive on mobile

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Textbook has 10 chapters across 4 modules, all readable with navigation.

---

## Phase 4: User Story 2 - Ask Questions via RAG Chatbot (Priority: P1)

**Goal**: Students can ask natural language questions and receive AI-generated answers with source citations from textbook content

**Independent Test**: Open chatbot widget, type "What are ROS 2 nodes?", receive answer with source citations within 10 seconds

### Implementation for User Story 2

- [X] T033 [P] [US2] Create ChatbotWidget component in frontend/src/components/ChatbotWidget/index.tsx with open/close state, query input, response display
- [X] T034 [P] [US2] Create ChatbotWidget styles in frontend/src/components/ChatbotWidget/styles.module.css (fixed bottom-right, 350px wide, responsive on mobile)
- [X] T035 [US2] Implement chatbot query submission in ChatbotWidget using useApiClient hook to POST /v1/query with query_text, chapter_id (from useChapterId), user_id: "guest-user"
- [X] T036 [US2] Implement response rendering in ChatbotWidget to display answer text, source citations (chapter title, section title, similarity score), and confidence score
- [X] T037 [US2] Add loading indicator to ChatbotWidget while waiting for API response (isLoading state, spinner animation)
- [X] T038 [US2] Add error handling to ChatbotWidget for HTTP status codes: 400 (validation error), 404 (CONTEXT_NOT_FOUND), 429 (rate limit), 500/503 (server error)
- [X] T039 [US2] Add empty query validation to ChatbotWidget (disable submit button if query is empty, show prompt message)
- [X] T040 [US2] Create Root component swizzle in frontend/src/theme/Root.tsx to inject ChatbotWidget on every page
- [ ] T041 [US2] Test chatbot integration locally: open widget, submit query "What are ROS 2 nodes?", verify response with source citations displays correctly
- [ ] T042 [US2] Test chatbot error handling: stop backend API, verify "Service temporarily unavailable" message appears
- [ ] T043 [US2] Test chatbot chapter context: navigate to different chapters, verify chapter_id changes in requests (use browser DevTools Network tab)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Textbook is readable AND chatbot answers questions with source citations.

---

## Phase 5: User Story 3 - Query Selected Text (Priority: P2)

**Goal**: Students can highlight text and trigger contextual chatbot queries without manually retyping

**Independent Test**: Highlight text in a chapter, see tooltip appear, click "Ask about this", chatbot opens with selected text pre-populated

### Implementation for User Story 3

- [ ] T044 [P] [US3] Create SelectionTooltip component in frontend/src/components/SelectionTooltip/index.tsx using useTextSelection hook and Floating UI
- [ ] T045 [P] [US3] Create SelectionTooltip styles in frontend/src/components/SelectionTooltip/styles.module.css with floating positioning, "Ask about this" button
- [ ] T046 [US3] Implement tooltip positioning in SelectionTooltip using @floating-ui/react with offset, flip, and shift middleware to handle viewport edges
- [ ] T047 [US3] Add SelectionTooltip to Root component in frontend/src/theme/Root.tsx (inject alongside ChatbotWidget)
- [ ] T048 [US3] Implement "Ask about this" action in SelectionTooltip to open ChatbotWidget with selected_text pre-populated in query
- [ ] T049 [US3] Update ChatbotWidget to accept selected_text prop and display it as context above query input (e.g., "Selected: <text>")
- [ ] T050 [US3] Update ChatbotWidget query submission to include selected_text in POST /v1/query body when available
- [ ] T051 [US3] Test text selection locally: highlight text, verify tooltip appears near selection, click "Ask about this", verify chatbot opens with selected text shown
- [ ] T052 [US3] Test selection tooltip positioning: highlight text near viewport edges (top, bottom, left, right), verify tooltip stays visible and doesn't overflow
- [ ] T053 [US3] Test selection on mobile: long-press to select text on mobile device, verify tooltip appears and is usable

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Textbook readable, chatbot answers questions, selected text search works.

---

## Phase 6: User Story 4 - Access Published Textbook Online (Priority: P1)

**Goal**: Anyone can access the textbook via a public GitHub Pages URL without installing anything

**Independent Test**: Visit GitHub Pages URL in browser, confirm site loads within 3 seconds, all content accessible

### Implementation for User Story 4

- [X] T054 [P] [US4] Create GitHub Actions workflow file .github/workflows/deploy.yml with build and deploy jobs for GitHub Pages
- [X] T055 [P] [US4] Configure workflow to run on push to main branch and manual workflow_dispatch
- [X] T056 [P] [US4] Add build step to workflow: install dependencies, run `npm run build` with REACT_APP_API_URL environment variable for production
- [X] T057 [P] [US4] Add deploy step to workflow: upload build artifact to GitHub Pages using actions/upload-pages-artifact and actions/deploy-pages
- [X] T058 [P] [US4] Configure workflow permissions: contents: read, pages: write, id-token: write
- [X] T059 [US4] Update frontend/docusaurus.config.ts baseUrl to match GitHub repository name (e.g., /hackathon-book/)
- [X] T060 [US4] Update frontend/docusaurus.config.ts url to GitHub Pages URL (e.g., https://username.github.io)
- [X] T061 [US4] Set trailingSlash: false in frontend/docusaurus.config.ts to avoid GitHub Pages 404 issues
- [X] T062 [US4] Test local build: run `npm run build` in frontend/, verify build/ directory created without errors
- [ ] T063 [US4] Push code to GitHub repository on main branch (USER ACTION REQUIRED)
- [ ] T064 [US4] Enable GitHub Pages in repository settings: Settings → Pages → Source: "GitHub Actions" (USER ACTION REQUIRED)
- [ ] T065 [US4] Monitor GitHub Actions workflow: verify build completes successfully, deploy step uploads artifact (USER ACTION REQUIRED)
- [ ] T066 [US4] Test deployed site: visit GitHub Pages URL, verify homepage loads, navigation works, chapters readable, chatbot functions (USER ACTION REQUIRED)
- [ ] T067 [US4] Test deployment on slow connection: use browser DevTools to throttle to "Slow 3G", verify pages load progressively (USER ACTION REQUIRED)

**Checkpoint**: At this point, all P1 user stories (1, 2, 4) are complete. Textbook is publicly accessible via GitHub Pages with working chatbot.

---

## Phase 7: User Story 5 - Navigate Between Chapters (Priority: P2)

**Goal**: Students can navigate sequentially between chapters using Next/Previous links

**Independent Test**: Click "Next Chapter" and "Previous Chapter" buttons at bottom of pages, verify sequential navigation

### Implementation for User Story 5

- [X] T068 [US5] Verify Docusaurus classic preset includes doc pagination (Next/Previous links) - this is enabled by default
- [X] T069 [US5] Test chapter navigation locally: navigate to any chapter, scroll to bottom, verify "Next Chapter" and "Previous Chapter" links appear
- [X] T070 [US5] Test navigation on first chapter: navigate to first chapter (Module 1: ROS 2 Nodes), verify no "Previous Chapter" link appears
- [X] T071 [US5] Test navigation on last chapter: navigate to last chapter (Module 4: Capstone), verify no "Next Chapter" link appears
- [X] T072 [US5] Test sequential flow: start at first chapter, click "Next" repeatedly, verify chapters load in correct module/sidebar order

**Checkpoint**: All user stories (1, 2, 3, 4, 5) are now independently functional. Full textbook experience complete.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final quality checks

- [X] T073 [P] Add dark mode support: verify frontend/docusaurus.config.ts colorMode config includes defaultMode and respectPrefersColorScheme
- [X] T074 [P] Optimize ChatbotWidget mobile responsiveness: test on iOS Safari and Android Chrome, adjust styles if needed for small screens
- [ ] T075 [P] Add custom CSS in frontend/src/css/custom.css for global styling (if needed for branding)
- [ ] T076 [P] Add logo and favicon in frontend/static/img/ directory
- [X] T077 [P] Update frontend/docusaurus.config.ts title, tagline, and footer to reflect Physical AI Textbook branding
- [ ] T078 [P] Test cross-browser compatibility: verify site works on Chrome, Firefox, Safari, Edge (latest versions)
- [ ] T079 [P] Run Lighthouse accessibility audit on deployed site: aim for score ≥90 (per Success Criterion SC-006)
- [X] T080 [P] Verify all chapters follow educational standards: ≤5 concepts per chapter, B1 English proficiency, ≥1 code example
- [ ] T081 [P] Test chatbot performance: submit 5 different queries, verify average response time <10 seconds (per Success Criterion SC-002)
- [ ] T082 [P] Test page load performance: use browser DevTools Performance tab, verify homepage loads <3 seconds (per Success Criterion SC-004)
- [X] T083 Code cleanup: remove any console.log statements, unused imports, commented-out code
- [X] T084 Documentation: update README.md in repository root with project overview, setup instructions, deployment guide
- [ ] T085 Final verification: run through quickstart.md validation checklist to ensure all features work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase (hooks and plugins must exist)
- **User Story 2 (Phase 4)**: Depends on Foundational phase (hooks must exist) - Independent of US1 but enhanced by having chapters to cite
- **User Story 3 (Phase 5)**: Depends on Foundational phase AND User Story 2 (requires ChatbotWidget to exist)
- **User Story 4 (Phase 6)**: Depends on Foundational phase - Independent of other stories (deployment can happen anytime)
- **User Story 5 (Phase 7)**: Depends on User Story 1 (requires chapters to navigate between)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories - **MVP candidate**
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent of US1 but references chapters
- **User Story 3 (P2)**: Depends on User Story 2 (requires ChatbotWidget component)
- **User Story 4 (P1)**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 5 (P2)**: Depends on User Story 1 (requires chapters to exist)

### Within Each User Story

- **US1**: All chapter writing tasks (T015-T029) can run in parallel, then sidebar configuration (T030-T031), then local testing (T032)
- **US2**: Component creation (T033-T034) parallel, then implementation tasks sequential, then testing (T041-T043)
- **US3**: Component creation (T044-T045) parallel, then implementation tasks sequential, then testing (T051-T053)
- **US4**: Workflow file creation (T054-T058) parallel, config updates (T059-T061) parallel, then deployment sequence (T062-T067)
- **US5**: Verification and testing tasks sequential (T068-T072)

### Parallel Opportunities

- **Phase 1 Setup**: All tasks (T001-T007) can run in parallel except T001 must complete first
- **Phase 2 Foundational**: T010-T014 marked [P] can run in parallel after T008-T009 complete
- **US1 Chapters**: T015-T029 (all chapter writing) can run in parallel - 15 tasks simultaneously
- **US2 Components**: T033-T034 can run in parallel
- **US3 Components**: T044-T045 can run in parallel
- **US4 Workflow**: T054-T058 can run in parallel, T059-T061 can run in parallel
- **Polish**: T073-T082 marked [P] can run in parallel

---

## Parallel Example: User Story 1 (Chapter Writing)

```bash
# Launch all chapter writing tasks for US1 together (15 tasks in parallel):
Task: "Create frontend/docs/intro.md landing page"
Task: "Create frontend/docs/module-1-ros2/ with _category_.json"
Task: "Write frontend/docs/module-1-ros2/nodes.md"
Task: "Write frontend/docs/module-1-ros2/topics.md"
Task: "Write frontend/docs/module-1-ros2/services.md"
Task: "Write frontend/docs/module-1-ros2/urdf.md"
Task: "Create frontend/docs/module-2-gazebo/ with _category_.json"
Task: "Write frontend/docs/module-2-gazebo/simulation-basics.md"
Task: "Write frontend/docs/module-2-gazebo/sensors.md"
Task: "Create frontend/docs/module-3-isaac/ with _category_.json"
Task: "Write frontend/docs/module-3-isaac/isaac-sim.md"
Task: "Write frontend/docs/module-3-isaac/isaac-ros.md"
Task: "Create frontend/docs/module-4-vla/ with _category_.json"
Task: "Write frontend/docs/module-4-vla/voice-commands.md"
Task: "Write frontend/docs/module-4-vla/capstone.md"
```

---

## Parallel Example: User Story 2 (Chatbot Components)

```bash
# Launch ChatbotWidget component and styles in parallel:
Task: "Create ChatbotWidget component in frontend/src/components/ChatbotWidget/index.tsx"
Task: "Create ChatbotWidget styles in frontend/src/components/ChatbotWidget/styles.module.css"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 + 4 - P1 only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T014) - **CRITICAL**
3. Complete Phase 3: User Story 1 (T015-T032) - Textbook content
4. Complete Phase 4: User Story 2 (T033-T043) - Chatbot widget
5. Complete Phase 6: User Story 4 (T054-T067) - GitHub Pages deployment
6. **STOP and VALIDATE**: Test independently - textbook readable online with working chatbot
7. Deploy/demo MVP (70 hackathon points: 30 for textbook + 25 for chatbot + 5 for deployment + backend 30 = 90 total, need US3 for 100)

### Incremental Delivery (Add P2 stories for full 100 points)

1. MVP deployed (US1 + US2 + US4) → **90 points**
2. Add User Story 3 (T044-T053) → Selected text search → **100 points** ✅
3. Add User Story 5 (T068-T072) → Chapter navigation (already included in Docusaurus)
4. Complete Phase 8: Polish (T073-T085) → Final quality improvements

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T014)
2. Once Foundational is done:
   - **Developer A**: User Story 1 - Chapter writing (T015-T032)
   - **Developer B**: User Story 2 - Chatbot widget (T033-T043)
   - **Developer C**: User Story 4 - GitHub Pages deployment (T054-T067)
3. Stories complete and integrate independently
4. Add User Story 3 for final 100 points

### Recommended Execution Order (Solo Developer)

**Priority**: Complete P1 user stories first to reach 90 points, then add US3 for 100 points

1. **Day 1 (6-8 hours)**:
   - T001-T014: Setup + Foundational (~2 hours)
   - T015-T032: User Story 1 - Write all 10 chapters (~5-6 hours using AI assistance)

2. **Day 2 (4-6 hours)**:
   - T033-T043: User Story 2 - Build chatbot widget (~3 hours)
   - T054-T067: User Story 4 - Deploy to GitHub Pages (~2 hours)
   - **Checkpoint**: MVP deployed with 90 points

3. **Day 3 (2-3 hours)**:
   - T044-T053: User Story 3 - Add selected text search (~2 hours)
   - T073-T085: Polish phase - Final quality checks (~1 hour)
   - **Checkpoint**: Full 100 points achieved

**Total time**: 12-17 hours (achievable within 18-hour deadline!)

---

## Notes

- [P] tasks = different files, no dependencies, can run simultaneously
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **No automated tests** per constitution (manual testing only for hackathon MVP)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Chapter writing** is the critical path (5-10 hours) - use AI assistance (ChatGPT) to draft content
- **Chatbot integration** requires backend API running at localhost:8000
- **Deployment** requires GitHub repository with Pages enabled

---

## Task Count Summary

- **Phase 1 (Setup)**: 7 tasks
- **Phase 2 (Foundational)**: 7 tasks
- **Phase 3 (US1 - Textbook Content)**: 18 tasks
- **Phase 4 (US2 - Chatbot)**: 11 tasks
- **Phase 5 (US3 - Selected Text)**: 10 tasks
- **Phase 6 (US4 - Deployment)**: 14 tasks
- **Phase 7 (US5 - Navigation)**: 5 tasks
- **Phase 8 (Polish)**: 13 tasks
- **TOTAL**: 85 tasks

**Parallel opportunities**: 35 tasks marked [P] can run in parallel (41% of total)

**MVP scope** (US1 + US2 + US4): 50 tasks → 90 hackathon points
**Full scope** (all user stories): 85 tasks → 100 hackathon points + polish

---

## Success Metrics Alignment

This task list delivers on all success criteria from spec.md:

- **SC-001**: US1 T032 - Verify chapters load within 2 seconds
- **SC-002**: US2 T041 - Verify chatbot responds within 10 seconds
- **SC-003**: US3 T051 - Verify text selection triggers query with one action
- **SC-004**: US4 T066 - Verify GitHub Pages loads within 3 seconds
- **SC-005**: US2 T041 - Test chatbot answer quality (confidence > 0.3)
- **SC-006**: Polish T079 - Run Lighthouse audit for 90+ accessibility score
- **SC-007**: Polish T085 - Validate end-to-end learning task completion
- **SC-008**: Polish T078 - Test cross-browser compatibility
- **SC-009**: US1 T015-T029 - Ensure all code examples are syntactically correct
- **SC-010**: Polish T074 - Test chatbot widget on mobile devices

All functional requirements (FR-001 to FR-020) are covered by tasks across the user stories.

**Ready for implementation!** Run `/sp.implement` to begin systematic execution of these tasks.
