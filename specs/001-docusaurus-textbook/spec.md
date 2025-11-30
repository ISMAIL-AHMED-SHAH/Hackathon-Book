# Feature Specification: Docusaurus Physical AI Textbook Platform

**Feature Branch**: `001-docusaurus-textbook`
**Created**: 2025-11-30
**Status**: Draft
**Input**: User description: "Create Docusaurus-based Physical AI textbook with embedded RAG chatbot, selected text search, and GitHub Pages deployment"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read Interactive Textbook Content (Priority: P1)

Students learning Physical AI & Humanoid Robotics need to access structured educational content organized by modules (ROS 2, Gazebo, NVIDIA Isaac, VLA) in a web-based textbook format that works on any device.

**Why this priority**: This is the foundation of the learning experience. Without readable, well-organized content, no other features matter.

**Independent Test**: Can be fully tested by navigating to the deployed site, browsing the table of contents, and reading at least one complete chapter. Delivers standalone educational value even without chatbot features.

**Acceptance Scenarios**:

1. **Given** a student visits the textbook homepage, **When** they view the navigation sidebar, **Then** they see all modules organized hierarchically (Module 1: ROS 2, Module 2: Gazebo, Module 3: NVIDIA Isaac, Module 4: VLA)
2. **Given** a student clicks on a chapter link, **When** the chapter loads, **Then** they see formatted content with headings, code blocks, and explanatory text
3. **Given** a student is reading on a mobile device, **When** they access the textbook, **Then** the layout adapts responsively and remains readable
4. **Given** a student wants to find specific content, **When** they use the built-in search, **Then** they see relevant results from across all chapters

---

### User Story 2 - Ask Questions via RAG Chatbot (Priority: P1)

Students encounter concepts they don't understand while reading and need immediate clarification by asking natural language questions that are answered using the textbook's content as the knowledge base.

**Why this priority**: This is the core innovation that differentiates this textbook from static alternatives. It directly addresses the hackathon requirement for RAG integration and provides immediate learning support.

**Independent Test**: Can be tested by opening the chatbot widget, typing "What are ROS 2 nodes?", and receiving an answer with source citations from the textbook content.

**Acceptance Scenarios**:

1. **Given** a student is reading any chapter, **When** they open the chatbot widget, **Then** they see an input field and a prompt to ask questions
2. **Given** the chatbot is open and the student types a question, **When** they submit the query, **Then** they receive an answer generated from relevant textbook sections within 10 seconds
3. **Given** the chatbot returns an answer, **When** the student views the response, **Then** they see source citations indicating which chapters/sections the answer came from
4. **Given** the chatbot receives a question unrelated to the textbook content, **When** it processes the query, **Then** it responds with "I cannot find relevant information in the textbook to answer this question"
5. **Given** the student is on Chapter 3 (Gazebo), **When** they ask a question via the chatbot, **Then** the system prioritizes context from Chapter 3 while still considering other chapters

---

### User Story 3 - Query Selected Text (Priority: P2)

Students highlight specific technical terms or code snippets they don't understand and want contextual explanations without manually retyping the text into the chatbot.

**Why this priority**: This significantly improves user experience by reducing friction in the learning process. It's a required hackathon feature (10 points) but can be built after the basic chatbot works.

**Independent Test**: Can be tested by highlighting text in a chapter, right-clicking or using a context menu action, and receiving a chatbot response specifically about the highlighted content.

**Acceptance Scenarios**:

1. **Given** a student highlights text on a textbook page, **When** they trigger the "Ask about this" action, **Then** the chatbot opens with the selected text pre-populated as context
2. **Given** the chatbot receives a query with selected text, **When** it generates a response, **Then** the answer focuses specifically on explaining or elaborating on the selected text
3. **Given** a student selects a code snippet, **When** they query it, **Then** the chatbot explains what the code does in plain language

---

### User Story 4 - Access Published Textbook Online (Priority: P1)

Instructors, students, and hackathon judges need to access the textbook via a public URL without installing anything locally.

**Why this priority**: This is a core hackathon requirement (20 points for GitHub Pages deployment). The textbook must be publicly accessible to have value.

**Independent Test**: Can be tested by visiting the GitHub Pages URL in a browser and confirming the site loads correctly with all content accessible.

**Acceptance Scenarios**:

1. **Given** anyone with the URL, **When** they visit the GitHub Pages site, **Then** the textbook homepage loads within 3 seconds
2. **Given** the site is deployed, **When** new content is pushed to the main branch, **Then** the site automatically rebuilds and deploys updated content within 10 minutes
3. **Given** a user on a slow internet connection, **When** they access the site, **Then** pages load progressively and remain usable

---

### User Story 5 - Navigate Between Chapters (Priority: P2)

Students working through the course material sequentially need to easily move forward and backward between chapters without returning to the table of contents.

**Why this priority**: Improves learning flow and reduces navigation friction. Standard Docusaurus functionality but important for UX.

**Independent Test**: Can be tested by clicking "Next" and "Previous" buttons at the bottom of chapter pages to navigate sequentially.

**Acceptance Scenarios**:

1. **Given** a student finishes reading a chapter, **When** they scroll to the bottom, **Then** they see "Next Chapter" and "Previous Chapter" navigation links
2. **Given** a student clicks "Next Chapter", **When** the next page loads, **Then** they see the subsequent chapter in the learning sequence
3. **Given** a student is on the first chapter, **When** they view the page, **Then** there is no "Previous Chapter" link

---

### Edge Cases

- What happens when the chatbot receives an empty query? System should prompt user to enter a question.
- How does the system handle malformed or very long queries (>1000 characters)? System should truncate and warn user.
- What happens when the backend RAG API is unavailable? Chatbot should display "Service temporarily unavailable. Please try again later."
- What happens when a student selects text that spans multiple paragraphs or code blocks? System should capture the full selection and pass it to the chatbot.
- What happens when two students query the chatbot simultaneously? System should handle concurrent requests independently without interference.
- What happens when a chapter has no corresponding content in the vector database? Chatbot should gracefully indicate it doesn't have context for that chapter yet.
- How does the system handle special characters in queries (quotes, brackets, code syntax)? System should sanitize input to prevent injection attacks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a web-based textbook with at least 5 chapters covering Physical AI & Humanoid Robotics topics (ROS 2, Gazebo, NVIDIA Isaac, Vision-Language-Action)
- **FR-002**: System MUST organize content hierarchically with modules, chapters, and sections visible in a navigation sidebar
- **FR-003**: System MUST render Markdown content including headings, paragraphs, code blocks (with syntax highlighting), lists, and images
- **FR-004**: System MUST embed a chatbot widget accessible from every textbook page
- **FR-005**: Chatbot MUST send user queries to the backend RAG API at `http://localhost:8000/v1/query` (configurable for production)
- **FR-006**: Chatbot MUST display answers, source citations, and confidence scores returned from the RAG API
- **FR-007**: System MUST detect when a user selects text on a page and provide a mechanism to query that selected text via the chatbot
- **FR-008**: System MUST pass selected text to the backend API as the `selected_text` parameter in query requests
- **FR-009**: System MUST automatically detect the current chapter ID from the page URL and include it in chatbot queries
- **FR-010**: System MUST be deployable to GitHub Pages with a single build command
- **FR-011**: System MUST be responsive and usable on desktop, tablet, and mobile devices
- **FR-012**: System MUST include a built-in search function to find keywords across all chapters
- **FR-013**: Each chapter MUST include at least one runnable code example demonstrating the concepts taught
- **FR-014**: Each chapter MUST limit new technical concepts to a maximum of 5 to manage cognitive load
- **FR-015**: Content MUST be written at a B1 English proficiency level for global accessibility
- **FR-016**: System MUST handle chatbot errors gracefully with user-friendly messages (not stack traces)
- **FR-017**: System MUST display loading indicators while chatbot queries are being processed
- **FR-018**: System MUST allow users to copy code snippets with a single click
- **FR-019**: System MUST generate a static site (HTML/CSS/JS) with no server-side rendering requirements for hosting
- **FR-020**: System MUST support dark mode and light mode themes

### Key Entities

- **Chapter**: A self-contained educational unit covering a specific topic (e.g., "ROS 2 Nodes and Topics"). Contains markdown content, code examples, and is associated with a chapter ID for RAG queries.
- **Module**: A grouping of related chapters (e.g., "Module 1: ROS 2 Fundamentals"). Contains multiple chapters and provides thematic organization.
- **Chatbot Query**: A user-submitted question with optional selected text context. Includes query text, chapter ID, user ID, and selected text. Sent to backend RAG API.
- **Chatbot Response**: An answer generated by the RAG system. Includes answer text, source citations (chapter/section references), confidence score, and grounding status.
- **Source Citation**: A reference to a specific textbook section used to generate an answer. Includes chapter title, section title, page number (if applicable), and similarity score.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Students can navigate to any of the 5+ chapters and read complete, formatted content within 2 seconds of clicking
- **SC-002**: Students can submit a chatbot query and receive an answer with source citations within 10 seconds
- **SC-003**: Students can select text on any page and trigger a contextual chatbot query with one action (click or keyboard shortcut)
- **SC-004**: The textbook site is publicly accessible via GitHub Pages and loads the homepage within 3 seconds for users with average internet connections
- **SC-005**: The chatbot successfully answers at least 80% of questions that have relevant content in the textbook (measured by confidence score > 0.3)
- **SC-006**: The site passes Lighthouse accessibility audit with a score of 90+ for accessibility
- **SC-007**: Students can complete a learning task (read a chapter, ask 2 clarifying questions, find a related topic via search) without encountering errors in 95% of sessions
- **SC-008**: The deployed site works correctly on Chrome, Firefox, Safari, and Edge browsers (latest versions)
- **SC-009**: Code examples in chapters are syntactically correct and runnable in their intended environments
- **SC-010**: The chatbot widget is visible and accessible on mobile devices without obscuring textbook content

## Assumptions *(include if you made assumptions)*

- Backend RAG API is already functional and running at `http://localhost:8000/v1/query` (as confirmed in PROGRESS.md)
- Content will be written in Markdown format following Docusaurus conventions
- GitHub repository already exists and has GitHub Pages enabled in settings
- Students have basic familiarity with web browsers and don't require accessibility features beyond standard screen reader support
- OpenAI API and Qdrant Cloud services have sufficient quota for expected query volume during hackathon demo
- The textbook will initially be in English only (Urdu translation is a bonus feature outside this spec)
- User authentication is not required for the base feature (Better-Auth signup/signin is a bonus feature outside this spec)
- The chatbot will have a default user ID for anonymous users (e.g., "guest-user") until authentication is implemented
- Chapter IDs follow the naming convention `ch-{module}-{topic}` (e.g., "ch-ros2-fundamentals")
- The backend API is CORS-enabled to accept requests from the frontend domain

## Out of Scope *(include if explicit exclusions needed)*

- User authentication and signup/signin (bonus feature, separate specification)
- Content personalization based on user background (bonus feature, separate specification)
- Urdu translation functionality (bonus feature, separate specification)
- Offline mode or progressive web app (PWA) features
- Real-time collaboration or multi-user editing of content
- Video embedding or interactive simulations within chapters
- Discussion forums or comment sections on chapters
- Analytics tracking or user behavior monitoring
- Content versioning or draft/publish workflows
- Admin panel for non-technical content editing
- AI-generated content creation tools
- Voice input for chatbot queries
- Integration with learning management systems (LMS)

## Dependencies *(include if external systems/teams involved)*

- **Backend RAG API**: Developed and deployed separately. Required endpoints: `POST /v1/query`, `GET /health`
- **Qdrant Cloud**: Vector database service must be accessible and contain embedded textbook content
- **OpenAI API**: Required for generating chatbot responses via the backend service
- **GitHub Pages**: Static site hosting service, requires repository with Pages enabled
- **Node.js & npm**: Required for building the Docusaurus site (version 18+ recommended)
- **Docusaurus v3**: Static site generator framework, provides theming and React components
- **Backend content loading**: Test data or full textbook content must be embedded in Qdrant before chatbot can function

## Notes *(optional - for additional context)*

**Content Structure Overview**:
Based on `project-req.md`, the textbook should cover:
- Module 1: ROS 2 Fundamentals (nodes, topics, services, URDF)
- Module 2: Gazebo & Unity Simulation (physics, sensors, rendering)
- Module 3: NVIDIA Isaac (Isaac Sim, Isaac ROS, Nav2)
- Module 4: Vision-Language-Action (Whisper voice commands, LLM-to-ROS integration, capstone project)

**Chatbot Integration Pattern**:
The chatbot widget should be implemented as a Docusaurus theme component (`src/theme/ChatBot/index.tsx`) and injected into the root layout so it appears on every page.

**Chapter ID Detection Strategy**:
Extract chapter ID from the page URL pathname. For example, `/docs/module-1-ros2/nodes` → chapter ID: `ch-ros2-nodes`. Map URLs to chapter IDs using a configuration file.

**Selected Text Query UX**:
Implement using browser Selection API. When text is selected, show a floating tooltip/button with "Ask about this" action. Clicking opens chatbot with selected text pre-populated.

**Deployment Workflow**:
Docusaurus provides a built-in `npm run deploy` command for GitHub Pages. This builds the static site and pushes to the `gh-pages` branch automatically.

**Hackathon Scoring Alignment**:
- Base textbook (5 chapters): 30 points
- Embedded chatbot widget: 25 points
- Selected text search: 10 points
- GitHub Pages deployment: 5 points
- **Total**: 70 points (backend already earned 30 points)
