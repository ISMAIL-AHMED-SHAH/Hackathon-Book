# Research: Docusaurus Physical AI Textbook Platform

**Feature**: `001-docusaurus-textbook`
**Date**: 2025-11-30
**Phase**: 0 (Pre-implementation research)

## Overview

This document consolidates research findings for implementing a Docusaurus-based textbook with embedded RAG chatbot, selected text search, and GitHub Pages deployment.

---

## 1. Chatbot Widget Integration

### Decision

Use **Root component swizzling** (`src/theme/Root.js`) to inject a persistent floating chatbot widget that appears on every page.

### Rationale

The Root component is rendered at the top of the React tree and **never unmounts during navigation**, ensuring widget state persists automatically. This eliminates manual lifecycle management compared to alternatives.

### Implementation Pattern

```javascript
// src/theme/Root.js
import React from 'react';
import ChatbotWidget from '@site/src/components/ChatbotWidget';

export default function Root({children}) {
  return (
    <>
      {children}
      <ChatbotWidget />
    </>
  );
}
```

Widget component structure:
- Fixed positioning (bottom-right corner)
- Toggle button to open/close chat panel
- CSS modules for styling
- React state for open/closed status

### Alternatives Considered

| Approach | Why Rejected |
|----------|--------------|
| Footer swizzling | Footer unmounts on navigation, losing state |
| Client modules | Cannot use React hooks or state |
| Custom plugin with injectHtmlTags | Cannot inject React components |

### Sources

- [Docusaurus Swizzling Documentation](https://docusaurus.io/docs/swizzling)
- [Biel.ai Chatbot Integration Example](https://docs.biel.ai/installation/docusaurus)

---

## 2. Chapter ID Detection

### Decision

Use **`useLocation()` hook** from `@docusaurus/router` combined with a **custom plugin** that generates a static JSON mapping file (`chapter-map.json`) at build time.

### Rationale

`useLocation()` provides reactive pathname updates. Docusaurus plugin's `contentLoaded()` API generates a static mapping file at build time, avoiding runtime path parsing overhead. This pattern is used by official Docusaurus plugins for SEO and analytics.

### Implementation Pattern

```javascript
// plugins/chapter-mapper-plugin.js
module.exports = function chapterMapperPlugin(context, options) {
  return {
    name: 'chapter-mapper-plugin',
    contentLoaded({ actions }) {
      const chapterMap = {
        '/docs/module-1/nodes': 'ch-ros2-nodes',
        '/docs/module-1/packages': 'ch-ros2-packages',
        '/docs/module-2/simulation': 'ch-gazebo-basics',
      };
      actions.createData('chapter-map.json', JSON.stringify(chapterMap));
    },
  };
};
```

```javascript
// src/hooks/useChapterId.js
import { useLocation } from '@docusaurus/router';
import { usePluginData } from '@docusaurus/useGlobalData';

export function useChapterId() {
  const { pathname } = useLocation();
  const chapterMap = usePluginData('chapter-mapper-plugin')?.['chapter-map.json'];
  const normalizedPath = pathname.replace(/\/$/, '').split('#')[0];
  return chapterMap?.[normalizedPath] || null;
}
```

### Key Considerations

- Normalize pathname (remove trailing slashes, hash fragments)
- Handle `baseUrl` prefix for GitHub Pages project sites
- SSR-aware: `useLocation()` pathname hydrates on client

### Alternatives Considered

| Approach | Why Rejected |
|----------|--------------|
| Hardcoded mapping object | Doesn't scale; manual updates required |
| Runtime file system traversal | Doesn't work in SSR context; slow |
| URL query parameters | Pollutes URLs; not RESTful |

### Sources

- [Docusaurus useLocation Documentation](https://github.com/facebook/docusaurus/discussions/9170)
- [Docusaurus Plugin Lifecycle APIs](https://docusaurus.io/docs/api/plugin-methods/lifecycle-apis)

---

## 3. Selected Text Detection

### Decision

Use **browser Selection API** (`window.getSelection()`) with React hooks listening to `mouseup` and `selectionchange` events. Use **Floating UI** library for tooltip positioning.

### Rationale

Selection API is the standard, well-supported way to detect text selection. `selectionchange` event captures keyboard-based selection (Shift+arrows), not just mouse. Floating UI handles complex tooltip positioning near viewport edges.

### Implementation Pattern

```javascript
// src/hooks/useTextSelection.js
import { useEffect, useState } from 'react';

export function useTextSelection() {
  const [selection, setSelection] = useState(null);
  const [range, setRange] = useState(null);

  useEffect(() => {
    const handleSelection = () => {
      const sel = window.getSelection();
      if (sel.rangeCount === 0) {
        setSelection(null);
        return;
      }
      const text = sel.toString();
      if (text.length > 0) {
        setSelection(text);
        setRange(sel.getRangeAt(0).getBoundingClientRect());
      } else {
        setSelection(null);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('selectionchange', handleSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('selectionchange', handleSelection);
    };
  }, []);

  return { selection, range };
}
```

Floating UI integration:
```bash
npm install @floating-ui/react
```

```javascript
import { useFloating, offset, flip, shift } from '@floating-ui/react';

const { refs, floatingStyles } = useFloating({
  placement: 'top',
  middleware: [offset(10), flip(), shift({ padding: 8 })],
});
```

### Accessibility Considerations

- Add `role="tooltip"` and `aria-label` to tooltip
- Support keyboard selection (use `selectionchange`, not just `mouseup`)
- Provide keyboard shortcut to dismiss (Escape key)
- Ignore selections inside input/textarea elements

### Alternatives Considered

| Approach | Why Rejected |
|----------|--------------|
| useContext + manual ref | More verbose; doesn't handle keyboard selection |
| Native context menu | Limited customization; poor programmatic UX |
| Popper.js | Older; Floating UI has better TypeScript support |

### Sources

- [React Text Selection API - Stack Overflow](https://stackoverflow.com/questions/43184603/select-text-highlight-selection-or-get-selection-value-react)
- [Floating UI Tooltip Documentation](https://floating-ui.com/docs/tooltip)
- [How to Share Selected Text in React](https://spacejelly.dev/posts/how-to-share-selected-text-in-react-with-the-selection-api)

---

## 4. Environment Configuration

### Decision

Use **`customFields`** in `docusaurus.config.js` to inject environment variables at build time, accessed via `useDocusaurusContext()`. Store sensitive config in `.env` files excluded from version control.

### Rationale

`customFields` is the official Docusaurus pattern for configuration. It works at build time and ensures environment values are bundled securely. `.env` files support different URLs per environment (development vs production).

### Implementation Pattern

**Environment files:**
```bash
# .env.development
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=5000
```

```bash
# .env.production
REACT_APP_API_URL=https://api.example.com
REACT_APP_API_TIMEOUT=30000
```

**Docusaurus config:**
```javascript
// docusaurus.config.js
import dotenv from 'dotenv';

const envFile = process.env.NODE_ENV === 'production'
  ? '.env.production'
  : '.env.development';
dotenv.config({ path: envFile });

const config = {
  customFields: {
    apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    apiTimeout: process.env.REACT_APP_API_TIMEOUT || '5000',
  },
};

export default config;
```

**API client hook:**
```javascript
// src/hooks/useApiClient.js
import { useDocusaurusContext } from '@docusaurus/useDocusaurusContext';

export function useApiClient() {
  const { siteConfig } = useDocusaurusContext();
  const { apiUrl, apiTimeout } = siteConfig.customFields;

  const fetchData = async (endpoint, options = {}) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), apiTimeout);

    try {
      const response = await fetch(`${apiUrl}${endpoint}`, {
        ...options,
        signal: controller.signal,
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } finally {
      clearTimeout(timeoutId);
    }
  };

  return { apiUrl, fetchData };
}
```

### Security Considerations

- **Never commit `.env.production`** with real secrets
- Use GitHub Secrets for CI/CD environment variables
- `customFields` values are embedded in client bundle; don't put sensitive tokens there
- For GitHub Pages deployment, set environment variables in workflow YAML

### Dependencies

```bash
npm install --save-dev dotenv
```

### Alternatives Considered

| Approach | Why Rejected |
|----------|--------------|
| REACT_APP_ prefix only | Works but less integrated with Docusaurus config |
| Runtime config JSON file | More complex; requires fetch at startup |
| Hardcoded baseUrl in code | Unmaintainable; breaks when environments change |

### Sources

- [Docusaurus Environment Variables Configuration](https://thedaxshepherd.com/2023/01/26/docusaurus-environment-variables/)
- [Docusaurus useDocusaurusContext](https://docusaurus.io/docs/docusaurus-core)

---

## 5. GitHub Pages Deployment

### Decision

Use **GitHub Actions workflow** with Docusaurus's built-in build script. Configure `baseUrl`, `url`, `organizationName`, and `projectName` in `docusaurus.config.js`. Use "GitHub Actions" as Pages source in repository settings.

### Rationale

GitHub Actions is the modern approach recommended by Docusaurus (replacing legacy "Deploy from branch"). Provides CI/CD integration, better logs, supports custom build steps, and is maintained by GitHub.

### Implementation Pattern

**Docusaurus config:**
```typescript
// docusaurus.config.ts
const config = {
  title: 'Physical AI Textbook',
  url: 'https://username.github.io',
  baseUrl: '/hackathon-book/', // Repository name

  organizationName: 'username', // GitHub username or org
  projectName: 'hackathon-book', // Repository name

  trailingSlash: false, // Explicitly set
};

export default config;
```

**GitHub Actions workflow:**
```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm install --frozen-lockfile

      - name: Build website
        env:
          REACT_APP_API_URL: ${{ secrets.API_URL }}
        run: npm run build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: build

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Configuration Guidelines

**Project site pattern** (username.github.io/repo-name):
```typescript
url: 'https://username.github.io',
baseUrl: '/repo-name/',
organizationName: 'username',
projectName: 'repo-name',
```

**User/Organization site pattern** (username.github.io):
```typescript
url: 'https://username.github.io',
baseUrl: '/',
organizationName: 'username',
projectName: 'username.github.io',
```

### Repository Settings

1. Go to GitHub.com → Repository → Settings → Pages
2. Source: Select **"GitHub Actions"** (NOT "Deploy from a branch")
3. Wait for first workflow to complete
4. Site available at URL shown in Settings

### Common Issues

| Issue | Solution |
|-------|----------|
| 404 on subpaths | Verify `baseUrl` matches repository structure |
| CSS not loading | Ensure `baseUrl` is consistent in config and URLs |
| Workflow not appearing | Go to Actions → Enable "Deploy to GitHub Pages" |

### Alternatives Considered

| Approach | Why Rejected |
|----------|--------------|
| npm run deploy script | Deprecated; requires gh-pages package and SSH setup |
| Manual branch deploy | Outdated; no CI/CD integration |
| Vercel/Netlify | Better DX, but requirement is GitHub Pages |

### Sources

- [Docusaurus GitHub Pages Deployment](https://docusaurus.io/docs/deployment)
- [GitHub Pages Docusaurus with Actions](https://github.com/Repair-Technology/docusaurus-v3)

---

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Static Site Generator** | Docusaurus | v3.x | React-based documentation framework |
| **UI Framework** | React | v18.x | Component-based UI (bundled with Docusaurus) |
| **Styling** | CSS Modules | - | Scoped component styles |
| **Tooltip Positioning** | Floating UI | v0.24+ | Robust floating element positioning |
| **HTTP Client** | Fetch API | - | Native browser API for backend calls |
| **Environment Config** | dotenv | v16+ | Environment variable management |
| **Routing** | @docusaurus/router | bundled | Client-side routing (React Router wrapper) |
| **Deployment** | GitHub Actions | - | CI/CD pipeline for GitHub Pages |
| **Node.js** | Node.js | v18+ | Runtime for build tooling |
| **Package Manager** | npm | v9+ | Dependency management |

---

## Next Steps (Phase 1)

1. ✅ Design data model (entities, state, contracts)
2. ✅ Generate API contracts for chatbot integration
3. ✅ Create quickstart.md for developers
4. ✅ Update agent context with technology choices
