# Reusable Intelligence & Components

This document catalogs all reusable components, patterns, and intelligence from the Physical AI Textbook project that can be extracted for future use.

## 📦 Table of Contents

1. [Frontend Components](#frontend-components)
2. [Backend Components](#backend-components)
3. [Docusaurus Patterns](#docusaurus-patterns)
4. [Development Workflow](#development-workflow)
5. [Educational Content Templates](#educational-content-templates)
6. [Deployment Patterns](#deployment-patterns)

---

## 🎨 Frontend Components

### 1. ChatbotWidget Component

**Location**: `frontend/src/components/ChatbotWidget/`

**Purpose**: Persistent floating chatbot widget with RAG integration

**Reusability Score**: ⭐⭐⭐⭐⭐ (Highly reusable)

**Features**:
- Fixed bottom-right positioning
- Open/close state management
- API integration with error handling
- Conversation history
- Loading states
- Mobile responsive

**How to Reuse**:
1. Copy `ChatbotWidget/` directory to your project
2. Update API endpoint in `useApiClient` hook
3. Inject via Root component swizzle
4. Customize styling in `styles.module.css`

**Customization Points**:
```typescript
// Change API endpoint
const { fetchData } = useApiClient();

// Modify query structure
interface ChatbotQuery {
  query_text: string;
  chapter_id: string | null;
  user_id: string;
  selected_text?: string;  // Optional context
}

// Customize widget position/styling
.container {
  position: fixed;
  bottom: 20px;  /* Customize */
  right: 20px;   /* Customize */
}
```

**Dependencies**:
- React 18+
- `useApiClient` hook
- `useChapterId` hook (optional)

---

### 2. Custom React Hooks

#### 2.1 `useApiClient` Hook

**Location**: `frontend/src/hooks/useApiClient.ts`

**Purpose**: Standardized API client with timeout, error handling, and configuration

**Reusability Score**: ⭐⭐⭐⭐⭐

**Features**:
- Environment-based API URL configuration
- Request timeout with AbortController
- Automatic error parsing
- TypeScript type safety

**How to Reuse**:
```typescript
import { useApiClient } from '@site/src/hooks/useApiClient';

function MyComponent() {
  const { apiUrl, fetchData } = useApiClient();

  const fetchSomething = async () => {
    try {
      const data = await fetchData('/endpoint', {
        method: 'POST',
        body: JSON.stringify({ foo: 'bar' }),
      });
      return data;
    } catch (error) {
      console.error('Request failed:', error);
    }
  };
}
```

**Configuration**:
```typescript
// In docusaurus.config.ts
customFields: {
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  apiTimeout: process.env.REACT_APP_API_TIMEOUT || '10000',
}
```

---

#### 2.2 `useChapterId` Hook

**Location**: `frontend/src/hooks/useChapterId.ts`

**Purpose**: Context-aware routing - detects current chapter from URL

**Reusability Score**: ⭐⭐⭐⭐

**Features**:
- Reactive pathname detection
- Plugin data integration
- Normalized path handling (removes trailing slashes, hash fragments)

**How to Reuse**:
```typescript
import { useChapterId } from '@site/src/hooks/useChapterId';

function MyComponent() {
  const chapterId = useChapterId();
  // Returns: "ch-ros2-nodes" or null
}
```

**Requires**: Chapter mapper plugin (see below)

---

#### 2.3 `useTextSelection` Hook

**Location**: `frontend/src/hooks/useTextSelection.ts`

**Purpose**: Detect and capture text selection with bounding box coordinates

**Reusability Score**: ⭐⭐⭐⭐⭐ (Universal)

**Features**:
- Browser Selection API integration
- Supports mouse and keyboard selection
- Returns text + DOMRect for tooltip positioning
- Auto-cleanup on unmount

**How to Reuse**:
```typescript
import { useTextSelection } from '@site/src/hooks/useTextSelection';

function MyComponent() {
  const selection = useTextSelection();

  if (selection) {
    console.log('Selected text:', selection.text);
    console.log('Bounding box:', selection.range);
  }
}
```

**Use Cases**:
- Text highlighting tools
- Annotation systems
- Context-aware search
- Quote extraction

---

### 3. Docusaurus Plugin: Chapter Mapper

**Location**: `frontend/plugins/chapter-mapper-plugin.js`

**Purpose**: Generate static chapter ID mapping at build time

**Reusability Score**: ⭐⭐⭐⭐

**Features**:
- Build-time data generation
- No runtime overhead
- Extensible mapping structure
- Integrates with Docusaurus plugin API

**How to Reuse**:
```javascript
// plugins/your-mapper-plugin.js
module.exports = function yourMapperPlugin(context, options) {
  return {
    name: 'your-mapper-plugin',
    contentLoaded({ actions }) {
      const yourMapping = {
        '/path1': 'id1',
        '/path2': 'id2',
      };
      actions.createData('your-map.json', JSON.stringify(yourMapping));
    },
  };
};
```

**Register in config**:
```typescript
// docusaurus.config.ts
plugins: [
  './plugins/your-mapper-plugin.js',
],
```

**Access in components**:
```typescript
import { usePluginData } from '@docusaurus/useGlobalData';

const data = usePluginData('your-mapper-plugin')?.['your-map.json'];
```

---

### 4. Root Component Swizzle Pattern

**Location**: `frontend/src/theme/Root.tsx`

**Purpose**: Inject global components that persist across navigation

**Reusability Score**: ⭐⭐⭐⭐⭐

**Features**:
- Never unmounts during navigation
- Perfect for persistent widgets
- Global state container

**How to Reuse**:
```typescript
// src/theme/Root.tsx
import React from 'react';
import YourGlobalComponent from '@site/src/components/YourGlobalComponent';

export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <YourGlobalComponent />
    </>
  );
}
```

**Use Cases**:
- Chat widgets
- Notification systems
- Global search
- Analytics trackers
- Help tooltips

---

## 🔧 Backend Components

### 1. RAG Query Pipeline

**Location**: `backend/src/api/v1/query.py`

**Purpose**: Complete RAG (Retrieval-Augmented Generation) implementation

**Reusability Score**: ⭐⭐⭐⭐⭐

**Features**:
- Vector similarity search (Qdrant)
- LLM integration (OpenAI GPT-4)
- Context grounding validation
- Source citation tracking
- Confidence scoring

**Components to Extract**:

#### 1.1 Vector Search Service
```python
# backend/src/services/vector_search.py
class VectorSearchService:
    def search(self, query: str, chapter_id: str = None, limit: int = 3):
        """Reusable vector search with optional filtering"""
        pass
```

#### 1.2 LLM Service
```python
# backend/src/services/llm.py
class LLMService:
    def generate_answer(self, query: str, context: List[str]):
        """Reusable LLM answer generation"""
        pass
```

#### 1.3 Error Handler
```python
# backend/src/utils/error_handler.py
class StandardErrorResponse:
    """Reusable standardized error responses"""
    error_code: str
    message: str
```

**How to Reuse**:
1. Copy `backend/src/services/` directory
2. Update vector DB connection settings
3. Configure LLM provider (OpenAI, Anthropic, etc.)
4. Customize error codes for your domain

---

### 2. Prometheus Metrics Integration

**Location**: `backend/src/core/metrics.py`

**Purpose**: Production-ready observability

**Reusability Score**: ⭐⭐⭐⭐⭐

**Metrics Tracked**:
- Request duration (histogram)
- Request count (counter)
- Active requests (gauge)
- Error rates (counter)

**How to Reuse**:
```python
from prometheus_client import Counter, Histogram

query_counter = Counter(
    'app_queries_total',
    'Total number of queries',
    ['endpoint', 'status']
)

query_duration = Histogram(
    'app_query_duration_seconds',
    'Query processing time',
    ['endpoint']
)
```

---

## 📚 Docusaurus Patterns

### 1. Educational Content Structure

**Pattern**: Hierarchical modules with auto-generated navigation

**Structure**:
```
docs/
├── intro.md
├── module-1-topic/
│   ├── _category_.json
│   ├── chapter1.md
│   └── chapter2.md
├── module-2-topic/
│   ├── _category_.json
│   └── chapter1.md
```

**`_category_.json` Template**:
```json
{
  "label": "Module 1: Topic Name",
  "position": 1,
  "link": {
    "type": "generated-index",
    "description": "Module description here."
  }
}
```

**Reusability**: Use for any course, documentation, or knowledge base

---

### 2. Chapter Template

**Location**: Any chapter file (e.g., `frontend/docs/module-1-ros2/nodes.md`)

**Pattern**: Consistent structure for educational content

**Template**:
```markdown
---
sidebar_position: 1
---

# Chapter Title

Brief introduction (1-2 sentences).

## Key Concepts

1. **Concept 1**: Explanation
2. **Concept 2**: Explanation
3. **Concept 3**: Explanation

## Code Example

\`\`\`python
# Runnable code snippet
import library

def example():
    pass
\`\`\`

## Use Cases

| Scenario | Solution | When to Use |
|----------|----------|-------------|
| ... | ... | ... |

## Try It Yourself

Ask the chatbot:
- "Question 1?"
- "Question 2?"
```

**Reusability**: Template for any technical documentation

---

### 3. GitHub Actions Deployment Workflow

**Location**: `.github/workflows/deploy.yml`

**Purpose**: Automated CI/CD for Docusaurus → GitHub Pages

**Reusability Score**: ⭐⭐⭐⭐⭐

**Features**:
- Build caching (npm)
- Environment variable injection
- Artifact upload
- Concurrent deployment control

**How to Reuse**:
1. Copy `.github/workflows/deploy.yml` to your repo
2. Update `working-directory` if needed
3. Update environment variables
4. Configure repository secrets for API keys

**Customization**:
```yaml
- name: Build website
  env:
    REACT_APP_API_URL: ${{ secrets.API_URL }}  # Use secrets for sensitive data
    REACT_APP_CUSTOM_VAR: your-value
  run: npm run build
```

---

## 🔄 Development Workflow Patterns

### 1. Spec-Driven Development (SDD)

**Pattern**: This entire project structure

**Components**:
- `specs/` directory with spec.md, plan.md, tasks.md
- `history/prompts/` for PHR (Prompt History Records)
- `.specify/` for templates and scripts

**Reusability**: Framework for any software project

**How to Reuse**:
1. Copy `.specify/` directory structure
2. Use `/sp.specify`, `/sp.plan`, `/sp.tasks`, `/sp.implement` workflow
3. Maintain PHRs for AI-assisted development

---

### 2. Task Breakdown Pattern

**Location**: `specs/001-docusaurus-textbook/tasks.md`

**Pattern**: Phase-based task organization

**Structure**:
```markdown
## Phase 1: Setup
- [ ] Task 1
- [ ] Task 2

## Phase 2: Core Development
- [ ] Task 3
- [X] Task 4 (completed)

**Checkpoint**: Phase validation criteria
```

**Markers**:
- `[P]` = Can run in parallel
- `[US1]` = Belongs to User Story 1
- `[X]` = Completed

**Reusability**: Template for any complex project

---

## 📝 Educational Content Templates

### 1. Textbook Chapter Template

**Characteristics**:
- B1 English proficiency level
- ≤5 key concepts per chapter
- ≥1 runnable code example
- Interactive chatbot prompts
- Comparison tables
- Use cases

**Quality Gates**:
```markdown
✅ Simple sentence structures
✅ Common vocabulary (avoid jargon)
✅ Clear code comments
✅ Real-world examples
✅ Visual aids (tables, diagrams)
```

---

### 2. Capstone Project Template

**Location**: `frontend/docs/module-4-vla/capstone.md`

**Pattern**: Comprehensive integration project

**Structure**:
1. Project Overview
2. System Architecture (diagram)
3. Learning Objectives (checklist)
4. Phase-by-phase implementation
5. Code examples for each component
6. Success criteria
7. Bonus challenges
8. Resources

**Reusability**: Template for any course-ending project

---

## 🚀 Deployment Patterns

### 1. Environment Configuration Pattern

**Pattern**: Multi-environment configuration with dotenv

**Structure**:
```
.env.development      # Local development
.env.production       # Production build
.gitignore            # Exclude .env files
```

**Docusaurus Integration**:
```typescript
// docusaurus.config.ts
import * as dotenv from 'dotenv';

const envFile = process.env.NODE_ENV === 'production'
  ? '.env.production'
  : '.env.development';
dotenv.config({ path: envFile });

const config = {
  customFields: {
    apiUrl: process.env.REACT_APP_API_URL,
  },
};
```

**Reusability**: Universal pattern for any web app

---

### 2. GitHub Pages Deployment Checklist

**Pattern**: Pre-deployment validation

**Checklist**:
```markdown
- [ ] `url` matches GitHub username
- [ ] `baseUrl` matches repository name (case-sensitive!)
- [ ] `organizationName` set correctly
- [ ] `projectName` set correctly
- [ ] `trailingSlash: false` configured
- [ ] Build succeeds locally (`npm run build`)
- [ ] .gitignore excludes build artifacts
- [ ] GitHub Pages source set to "GitHub Actions"
```

---

## 🎁 Extractable Packages

### Recommended NPM Packages to Publish

1. **@your-org/docusaurus-chatbot-widget**
   - ChatbotWidget component
   - useApiClient hook
   - Styles

2. **@your-org/docusaurus-chapter-mapper**
   - Chapter mapper plugin
   - useChapterId hook

3. **@your-org/react-text-selection**
   - useTextSelection hook
   - SelectionTooltip component (if implemented)

4. **@your-org/rag-query-pipeline**
   - Vector search service
   - LLM integration
   - Error handling

---

## 📊 Reusability Matrix

| Component | Reusability | Effort to Extract | Universal Use | Domain-Specific |
|-----------|-------------|-------------------|---------------|-----------------|
| ChatbotWidget | ⭐⭐⭐⭐⭐ | Low | ✅ | Any docs site |
| useApiClient | ⭐⭐⭐⭐⭐ | Minimal | ✅ | Any React app |
| useTextSelection | ⭐⭐⭐⭐⭐ | Minimal | ✅ | Universal |
| useChapterId | ⭐⭐⭐⭐ | Low | ❌ | Docusaurus only |
| Chapter Mapper Plugin | ⭐⭐⭐⭐ | Low | ❌ | Docusaurus only |
| Root Component Pattern | ⭐⭐⭐⭐⭐ | Minimal | ❌ | Docusaurus only |
| RAG Pipeline | ⭐⭐⭐⭐⭐ | Medium | ✅ | Any chatbot |
| GitHub Actions Workflow | ⭐⭐⭐⭐⭐ | Minimal | ✅ | Any static site |
| Educational Content Template | ⭐⭐⭐⭐ | Low | ✅ | Any course |
| SDD Workflow | ⭐⭐⭐⭐⭐ | Medium | ✅ | Any software project |

---

## 🔮 Future Enhancements

### High-Value Additions

1. **Offline Mode**: Cache chapters in IndexedDB
2. **Voice Input**: Integrate with useTextSelection for voice queries
3. **Multi-Language**: i18n support for international students
4. **PDF Export**: Generate PDF from chapters
5. **Progress Tracking**: User progress persistence
6. **Annotations**: Allow users to highlight and annotate
7. **Collaborative Features**: Share notes with classmates

---

## 📦 Quick Start: Extract for New Project

### Example: Create a New Documentation Site

```bash
# 1. Copy reusable components
cp -r frontend/src/components/ChatbotWidget your-project/src/components/
cp -r frontend/src/hooks your-project/src/
cp -r frontend/src/theme/Root.tsx your-project/src/theme/
cp -r frontend/plugins your-project/

# 2. Copy configuration
cp frontend/.env.development your-project/
cp .github/workflows/deploy.yml your-project/.github/workflows/

# 3. Update API endpoints
# Edit your-project/src/hooks/useApiClient.ts

# 4. Customize styles
# Edit your-project/src/components/ChatbotWidget/styles.module.css
```

---

## 🎯 Conclusion

This project contains **highly reusable intelligence** across:
- ✅ Frontend components (chatbot, hooks, plugins)
- ✅ Backend services (RAG, vector search, LLM)
- ✅ Development workflows (SDD, task management)
- ✅ Deployment patterns (GitHub Actions, environment config)
- ✅ Educational templates (chapters, capstone projects)

**Estimated Reusability**: 80% of code can be extracted for other projects with minimal modification.

**Highest Value Components**:
1. ChatbotWidget + useApiClient (universal chatbot solution)
2. useTextSelection (universal text interaction)
3. RAG Pipeline (any AI-powered search)
4. GitHub Actions workflow (any static site deployment)
5. SDD workflow (any software project)

---

**Next Steps**: Consider publishing reusable components as open-source NPM packages or internal libraries.
