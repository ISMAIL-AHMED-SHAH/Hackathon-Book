# Hackathon Book - Reusable Intelligence Library

This directory contains custom subagents and skills designed specifically for building the Physical AI & Humanoid Robotics educational platform with RAG-powered chatbot.

**Created**: 2025-11-28
**Framework**: Spec-Kit Plus (SDD-RI methodology)
**Pattern**: Persona + Questions + Principles (P+Q+P)

---

## 📁 Directory Structure

```
.claude/
├── agents/          # Subagents (5+ decision points, autonomous)
│   ├── educational-content-creator.md
│   ├── rag-pipeline-architect.md
│   └── api-contract-designer.md
│
├── skills/          # Skills (2-4 decision points, guidance)
│   ├── embedding-quality-validator.md
│   ├── personalization-strategy.md
│   └── docusaurus-integration-patterns.md
│
└── README.md        # This file
```

---

## 🤖 Subagents (Autonomous Execution)

### 1. **educational-content-creator**
**Purpose**: Generate complete educational textbook chapters following pedagogical best practices

**When to use**:
- Creating new chapters for the Physical AI course
- Generating educational content for any technical subject
- Designing learning materials with proper scaffolding

**Decision authority**: 9+ decisions
- Chapter structure and learning objectives
- Code examples and exercises
- Prerequisite management and cognitive load
- Assessment design

**Invocation example**:
```
Create Chapter 4 on "ROS 2 Nodes and Topics" using the educational-content-creator subagent.

Context:
- Prerequisites: Students completed Weeks 1-3
- Target: B1 proficiency (intermediate beginners)
- Duration: 90 minutes
- Include: Publisher/subscriber examples, hands-on exercise
```

**Output**: Complete Docusaurus-ready chapter with frontmatter, learning objectives, code examples, and assessments.

---

### 2. **rag-pipeline-architect**
**Purpose**: Design and implement end-to-end RAG pipelines with quality validation

**When to use**:
- Building the document ingestion pipeline
- Setting up Qdrant vector database
- Implementing retrieval APIs with hybrid search
- Debugging retrieval quality issues

**Decision authority**: 8+ decisions
- Chunking strategy (size, overlap, boundaries)
- Embedding model selection and quality validation
- Retrieval algorithms (semantic, hybrid, reranking)
- Error handling and performance optimization

**Invocation example**:
```
Design the RAG pipeline for the Physical AI textbook using the rag-pipeline-architect subagent.

Context:
- Corpus: 13 chapters (~1.2M tokens)
- Content: Educational text (88%), Python code (12%)
- Target: p95 latency < 500ms
- Infrastructure: Qdrant Cloud, OpenAI embeddings, FastAPI
```

**Output**: Complete ingestion pipeline, retrieval API, quality validation suite, and performance benchmarks.

---

### 3. **api-contract-designer**
**Purpose**: Design REST API contracts with explicit schemas, validation, and error handling

**When to use**:
- Designing FastAPI endpoints for the chatbot
- Creating request/response schemas with Pydantic
- Defining error taxonomies and validation rules
- Generating OpenAPI documentation

**Decision authority**: 6+ decisions
- Endpoint structure and authentication
- Request/response schemas with validation
- Error taxonomy (400, 401, 404, 422, 500)
- Security boundaries and rate limiting

**Invocation example**:
```
Design the chat API endpoint using the api-contract-designer subagent.

Context:
- Endpoint: POST /api/v1/chat
- Authentication: JWT (Better-auth)
- Input: User query, session ID, user level
- Output: AI answer with sources and confidence
- Performance: p95 < 2s, rate limit 10/min per user
```

**Output**: Pydantic schemas, FastAPI routes with validation, OpenAPI docs, and security implementation.

---

## 🎯 Skills (Guidance Frameworks)

### 1. **embedding-quality-validator**
**Purpose**: Systematic framework for validating RAG chunk and embedding quality

**When to use**:
- After chunking documents (before embedding)
- After generating embeddings (before storing in Qdrant)
- Debugging poor retrieval accuracy
- Onboarding new content types

**Decision points**: 4
1. Chunk semantic completeness (boundaries, code blocks)
2. Overlap strategy validation (10-20% range)
3. Embedding quality (intra vs inter-chapter similarity)
4. Retrieval accuracy testing (precision@3 > 0.8)

**Invocation example**:
```
I've generated embeddings for 2,847 chunks. Validate quality using the embedding-quality-validator skill.

Context:
- Chunking: 1024 tokens, 128 overlap
- Model: text-embedding-3-small
- Content: Educational text + Python code
```

**Output**: Quality validation report with pass/fail verdicts and fix recommendations.

---

### 2. **personalization-strategy**
**Purpose**: Design user-adaptive content personalization strategies

**When to use**:
- Implementing "Personalize this chapter" button
- Designing user onboarding questionnaires
- Building adaptive AI tutor responses
- Creating content variants for different user segments

**Decision points**: 4
1. User segmentation (dimensions: software level, hardware access)
2. Content adaptation (depth, examples, prerequisites)
3. Caching strategy (pre-generated vs dynamic)
4. Validation metrics (engagement, comprehension, satisfaction)

**Invocation example**:
```
Design personalization for chapter-level content using the personalization-strategy skill.

Context:
- Signup collects: software_level, hardware_access
- 13 chapters, 5-10 pages each
- Performance budget: <500ms page load
- Implementation: Can pre-generate or use LLM
```

**Output**: Complete personalization strategy with segmentation, adaptation patterns, caching approach, and validation plan.

---

### 3. **docusaurus-integration-patterns**
**Purpose**: Proven patterns for integrating React components into Docusaurus

**When to use**:
- Adding chat widgets to documentation pages
- Embedding authentication UI (Better-auth)
- Creating personalization buttons
- Troubleshooting component rendering issues

**Decision points**: 3
1. Component scope (page-specific vs site-wide)
2. State management (React Context, localStorage)
3. Styling strategy (CSS modules, Docusaurus variables)

**Invocation example**:
```
Add a floating chat widget to all docs pages using the docusaurus-integration-patterns skill.

Requirements:
- Render on every page (bottom-right)
- Maintain conversation state across navigation
- Use user profile from auth context
- Call FastAPI backend
```

**Output**: Complete implementation with component code, styling, global state setup, and API integration.

---

## 🎓 How to Use This Intelligence Library

### For Hackathon Development

**Phase 1: Content Generation**
```bash
# Use educational-content-creator subagent
"Generate all 13 chapters for the Physical AI course using educational-content-creator.
Follow the curriculum outline in project-req.md."
```

**Phase 2: RAG Pipeline**
```bash
# Use rag-pipeline-architect subagent
"Build the complete RAG pipeline using rag-pipeline-architect.
Include ingestion, embedding, Qdrant setup, and retrieval API."

# Then validate quality with skill
"Validate embedding quality using embedding-quality-validator skill."
```

**Phase 3: Chat API**
```bash
# Use api-contract-designer subagent
"Design the chat API endpoint using api-contract-designer.
Include authentication, validation, and error handling."
```

**Phase 4: Frontend Integration**
```bash
# Use docusaurus-integration-patterns skill
"Integrate chat widget into Docusaurus using docusaurus-integration-patterns skill."

# Use personalization-strategy skill
"Implement content personalization using personalization-strategy skill."
```

---

## 📊 Intelligence Reuse Strategy

### This Project (Hackathon Book)
- **3 subagents** for complex, multi-decision tasks
- **3 skills** for guided, structured decision-making
- **Total**: 6 reusable intelligence components

### Future Projects
These components are **project-agnostic** and can be reused:

**Educational Content Creator**:
- Any technical course or tutorial series
- API documentation with examples
- Training materials for teams

**RAG Pipeline Architect**:
- Knowledge base chatbots
- Semantic search for any corpus
- Q&A systems for documentation

**API Contract Designer**:
- Any REST API development
- Microservices architecture
- Backend service design

**Embedding Quality Validator**:
- Any RAG/vector search system
- Content recommendation engines
- Semantic similarity applications

**Personalization Strategy**:
- E-learning platforms
- Content recommendation systems
- User-adaptive interfaces

**Docusaurus Integration Patterns**:
- Any Docusaurus-based documentation
- Interactive documentation sites
- Educational platform frontends

---

## 🏆 Hackathon Scoring Impact

With this intelligence library:

- ✅ **Base 100 points**: Functional book + RAG chatbot
- ✅ **+50 points**: Reusable agents and skills (6 components, all P+Q+P pattern)
- ✅ **+50 points**: Better-auth implementation (api-contract-designer helps)
- ✅ **+50 points**: Content personalization (personalization-strategy skill)
- ✅ **+50 points**: Urdu translation (can use educational-content-creator pattern)

**Total potential: 300 points** 🎯

---

## 📖 Best Practices

### When to Use Subagents vs Skills

**Use Subagents (autonomous execution) when**:
- Task has 5+ decision points
- Need autonomous reasoning without human intervention
- Pattern is complex and recurring across projects
- Output is a complete artifact (chapter, pipeline, API)

**Use Skills (guidance framework) when**:
- Task has 2-4 decision points
- Need human judgment with structured guidance
- Pattern is simpler, more of a checklist
- Output is validation or strategy (not implementation)

### P+Q+P Pattern Quality Checks

Every subagent/skill should have:
- ✅ **Persona**: Specific cognitive stance (not generic "expert")
- ✅ **Questions**: Context-specific analysis prompts (not yes/no)
- ✅ **Principles**: Concrete decision criteria (not vague guidance)
- ✅ **Examples**: Real usage scenarios with expected outputs
- ✅ **Validation**: Self-check criteria to verify quality

### Avoid Common Mistakes

❌ **Don't create agents for trivial tasks** (1-2 decisions)
❌ **Don't use vague personas** ("you are an expert")
❌ **Don't ask yes/no questions** (activate analysis, not prediction)
❌ **Don't over-specialize** (make patterns reusable across projects)
❌ **Don't skip validation** (always include self-check criteria)

---

## 🔄 Continuous Improvement

As you use these agents and skills, accumulate intelligence:

1. **Create ADRs** for architectural decisions (in `history/adr/`)
2. **Log PHRs** for prompt patterns that work (in `history/prompts/`)
3. **Refine agents** based on usage (version control in git)
4. **Add new components** when patterns emerge (follow P+Q+P)

**Intelligence compounds**: Project 10 will be 10× faster than Project 1.

---

## 🚀 Next Steps

1. **Read the agents**: Understand the P+Q+P patterns
2. **Try an agent**: Start with educational-content-creator for Chapter 1
3. **Validate quality**: Use embedding-quality-validator after RAG setup
4. **Iterate**: Refine based on what works
5. **Share**: Commit to git, reuse in future projects

**Questions?** Reference the Spec-Kit Plus documentation in `31-spec-kit-plus-hands-on/09-designing-reusable-intelligence.md`

---

**Remember**: Intelligence, not code, is the reusable artifact. These agents and skills will serve you long after this hackathon. 🎓✨
