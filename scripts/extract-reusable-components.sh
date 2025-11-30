#!/bin/bash
# Extract Reusable Components Script
# Usage: ./scripts/extract-reusable-components.sh <output-directory>

OUTPUT_DIR=${1:-"../reusable-components"}

echo "🎁 Extracting reusable components to: $OUTPUT_DIR"

# Create output directory structure
mkdir -p "$OUTPUT_DIR"/{frontend,backend,workflows,docs,templates}

# ===== FRONTEND COMPONENTS =====
echo "📦 Extracting frontend components..."

# ChatbotWidget
mkdir -p "$OUTPUT_DIR/frontend/components/ChatbotWidget"
cp -r frontend/src/components/ChatbotWidget/* "$OUTPUT_DIR/frontend/components/ChatbotWidget/"

# Hooks
mkdir -p "$OUTPUT_DIR/frontend/hooks"
cp frontend/src/hooks/useApiClient.ts "$OUTPUT_DIR/frontend/hooks/"
cp frontend/src/hooks/useTextSelection.ts "$OUTPUT_DIR/frontend/hooks/"
cp frontend/src/hooks/useChapterId.ts "$OUTPUT_DIR/frontend/hooks/"

# Types
mkdir -p "$OUTPUT_DIR/frontend/types"
cp frontend/src/types/index.ts "$OUTPUT_DIR/frontend/types/"

# Theme
mkdir -p "$OUTPUT_DIR/frontend/theme"
cp frontend/src/theme/Root.tsx "$OUTPUT_DIR/frontend/theme/"

# Plugins
mkdir -p "$OUTPUT_DIR/frontend/plugins"
cp frontend/plugins/chapter-mapper-plugin.js "$OUTPUT_DIR/frontend/plugins/"

echo "✅ Frontend components extracted"

# ===== BACKEND COMPONENTS =====
echo "📦 Extracting backend components..."

# Services
mkdir -p "$OUTPUT_DIR/backend/services"
cp backend/src/services/vector_search.py "$OUTPUT_DIR/backend/services/" 2>/dev/null || echo "⚠️  vector_search.py not found (create if needed)"
cp backend/src/services/llm.py "$OUTPUT_DIR/backend/services/" 2>/dev/null || echo "⚠️  llm.py not found (create if needed)"

# Utils
mkdir -p "$OUTPUT_DIR/backend/utils"
cp backend/src/utils/error_handler.py "$OUTPUT_DIR/backend/utils/" 2>/dev/null || echo "⚠️  error_handler.py not found"

# Core
mkdir -p "$OUTPUT_DIR/backend/core"
cp backend/src/core/metrics.py "$OUTPUT_DIR/backend/core/" 2>/dev/null || echo "⚠️  metrics.py not found"

echo "✅ Backend components extracted"

# ===== WORKFLOWS =====
echo "📦 Extracting CI/CD workflows..."

mkdir -p "$OUTPUT_DIR/workflows"
cp .github/workflows/deploy.yml "$OUTPUT_DIR/workflows/"

echo "✅ Workflows extracted"

# ===== DOCUMENTATION TEMPLATES =====
echo "📦 Extracting documentation templates..."

# Chapter template
cat > "$OUTPUT_DIR/docs/chapter-template.md" << 'EOF'
---
sidebar_position: 1
---

# Chapter Title

Brief introduction (1-2 sentences explaining the chapter topic).

## Key Concepts

1. **Concept 1**: Clear explanation in simple language
2. **Concept 2**: Real-world example
3. **Concept 3**: Use case scenario

## Code Example

\`\`\`python
# Runnable code snippet with comments
def example_function():
    """Docstring explaining what this does."""
    pass
\`\`\`

## Comparison Table

| Feature | Option A | Option B |
|---------|----------|----------|
| Speed | Fast | Slow |
| Use Case | X | Y |

## Best Practices

1. Practice 1
2. Practice 2
3. Practice 3

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Error 1 | Reason | Fix |

## Try It Yourself

Ask the chatbot:
- "Question related to this chapter?"
- "How do I use this concept?"
EOF

# Module category template
cat > "$OUTPUT_DIR/docs/_category_.json" << 'EOF'
{
  "label": "Module 1: Topic Name",
  "position": 1,
  "link": {
    "type": "generated-index",
    "description": "Module description explaining what students will learn."
  }
}
EOF

# Capstone project template
cat > "$OUTPUT_DIR/docs/capstone-template.md" << 'EOF'
---
sidebar_position: 99
---

# Capstone Project: Project Title

## Project Overview

**Goal**: Brief description of what students will build

**Duration**: Estimated time (e.g., 2-4 weeks)

**Difficulty**: Beginner | Intermediate | Advanced

## System Architecture

```
[Component 1] → [Component 2] → [Component 3]
```

## Learning Objectives

By completing this project, you will:

1. ✅ Objective 1
2. ✅ Objective 2
3. ✅ Objective 3

## Phase 1: Setup

### Tasks
- [ ] Task 1
- [ ] Task 2

### Implementation
\`\`\`bash
# Setup commands
\`\`\`

## Phase 2: Core Implementation

### Tasks
- [ ] Task 3
- [ ] Task 4

### Code Example
\`\`\`python
# Implementation code
\`\`\`

## Success Criteria

Your project is complete when:

1. ✅ Criterion 1
2. ✅ Criterion 2
3. ✅ Criterion 3

## Bonus Challenges

- 🌟 Advanced feature 1
- 🌟 Advanced feature 2

## Resources

- [Link 1](url)
- [Link 2](url)
EOF

echo "✅ Documentation templates created"

# ===== PROJECT TEMPLATES =====
echo "📦 Creating project templates..."

# Environment template
cat > "$OUTPUT_DIR/templates/.env.template" << 'EOF'
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=10000

# Backend Configuration (if applicable)
OPENAI_API_KEY=your-api-key-here
QDRANT_URL=http://localhost:6333
EOF

# Docker Compose template (for full stack)
cat > "$OUTPUT_DIR/templates/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - qdrant

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  qdrant_data:
EOF

echo "✅ Project templates created"

# ===== DOCUMENTATION =====
echo "📦 Copying main documentation..."

cp REUSABLE_COMPONENTS.md "$OUTPUT_DIR/README.md"
cp DEPLOYMENT.md "$OUTPUT_DIR/docs/deployment-guide.md" 2>/dev/null || echo "⚠️  DEPLOYMENT.md not found"

# Create package.json for frontend components
cat > "$OUTPUT_DIR/frontend/package.json" << 'EOF'
{
  "name": "@your-org/docusaurus-ai-components",
  "version": "1.0.0",
  "description": "Reusable AI-powered components for Docusaurus",
  "main": "index.js",
  "exports": {
    "./ChatbotWidget": "./components/ChatbotWidget/index.tsx",
    "./hooks/useApiClient": "./hooks/useApiClient.ts",
    "./hooks/useTextSelection": "./hooks/useTextSelection.ts",
    "./hooks/useChapterId": "./hooks/useChapterId.ts",
    "./plugins/chapterMapper": "./plugins/chapter-mapper-plugin.js"
  },
  "keywords": [
    "docusaurus",
    "chatbot",
    "rag",
    "ai",
    "education"
  ],
  "author": "Your Name",
  "license": "MIT",
  "peerDependencies": {
    "react": "^18.0.0",
    "@docusaurus/core": "^3.0.0"
  }
}
EOF

# Create README for the package
cat > "$OUTPUT_DIR/frontend/README.md" << 'EOF'
# Reusable Docusaurus AI Components

Extracted from Physical AI Textbook project.

## Components

### ChatbotWidget
Persistent floating chatbot with RAG integration.

### Hooks
- `useApiClient`: API client with timeout and error handling
- `useTextSelection`: Browser text selection with bounding box
- `useChapterId`: Context-aware chapter detection

### Plugins
- `chapter-mapper-plugin`: Build-time chapter ID mapping

## Installation

\`\`\`bash
npm install @your-org/docusaurus-ai-components
\`\`\`

## Usage

See individual component READMEs for detailed usage.
EOF

# ===== SUMMARY =====
echo ""
echo "✨ Extraction complete!"
echo ""
echo "📂 Output directory: $OUTPUT_DIR"
echo ""
echo "📦 Extracted components:"
echo "  ✅ Frontend: ChatbotWidget, 3 hooks, Root theme, plugin"
echo "  ✅ Backend: Services, utils, metrics"
echo "  ✅ Workflows: GitHub Actions deploy.yml"
echo "  ✅ Templates: Chapter, module, capstone, .env, docker-compose"
echo "  ✅ Documentation: Deployment guide, README"
echo ""
echo "🚀 Next steps:"
echo "  1. Review extracted components in $OUTPUT_DIR"
echo "  2. Update package.json with your organization name"
echo "  3. Publish to NPM or internal registry"
echo "  4. Create GitHub repository for reusable components"
echo ""
echo "📖 See $OUTPUT_DIR/README.md for full documentation"
