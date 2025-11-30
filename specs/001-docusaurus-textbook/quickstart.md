# Quickstart Guide: Docusaurus Physical AI Textbook

**Feature**: `001-docusaurus-textbook`
**Date**: 2025-11-30
**Target Audience**: Developers implementing the frontend

## Overview

This guide provides step-by-step instructions to set up the Docusaurus textbook frontend with embedded RAG chatbot integration. Estimated setup time: **30 minutes**.

---

## Prerequisites

Before starting, ensure you have:

- [x] **Node.js 18+** installed (`node --version`)
- [x] **npm 9+** installed (`npm --version`)
- [x] **Git** installed for version control
- [x] **Backend RAG API running** at `http://localhost:8000` (see `PROGRESS.md`)
- [x] **GitHub account** for Pages deployment
- [x] **Text editor** (VS Code recommended)

**Verify backend is running:**
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy",...}
```

---

## Step 1: Initialize Docusaurus Project

### 1.1 Create Frontend Directory

```bash
cd /path/to/hackathon-book
npx create-docusaurus@latest frontend classic --typescript
cd frontend
```

**What this does:**
- Creates `frontend/` directory with Docusaurus v3 boilerplate
- Uses "classic" preset (docs + blog)
- Enables TypeScript for type safety

### 1.2 Verify Installation

```bash
npm run start
```

**Expected output:**
```
[INFO] Starting the development server...
[SUCCESS] Docusaurus website is running at: http://localhost:3000/
```

Press **Ctrl+C** to stop the server after verification.

---

## Step 2: Install Additional Dependencies

```bash
npm install @floating-ui/react
npm install --save-dev dotenv
```

**Dependencies:**
- `@floating-ui/react`: Tooltip positioning for text selection
- `dotenv`: Environment variable management

---

## Step 3: Configure Docusaurus

### 3.1 Update `docusaurus.config.ts`

Replace the generated config with:

```typescript
import { themes as prismThemes } from 'prism-react-renderer';
import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import dotenv from 'dotenv';

// Load environment variables
const envFile = process.env.NODE_ENV === 'production'
  ? '.env.production'
  : '.env.development';
dotenv.config({ path: envFile });

const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'A comprehensive guide to building intelligent physical systems',
  favicon: 'img/favicon.ico',

  // GitHub Pages deployment config
  url: 'https://your-username.github.io',
  baseUrl: '/hackathon-book/',
  organizationName: 'your-username',
  projectName: 'hackathon-book',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  // Custom fields for API configuration
  customFields: {
    apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    apiTimeout: process.env.REACT_APP_API_TIMEOUT || '10000',
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/your-username/hackathon-book/tree/main/frontend/',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/social-card.png',
    navbar: {
      title: 'Physical AI Textbook',
      logo: {
        alt: 'Textbook Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Textbook',
        },
        {
          href: 'https://github.com/your-username/hackathon-book',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI Textbook Project.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'yaml'],
    },
    colorMode: {
      defaultMode: 'light',
      respectPrefersColorScheme: true,
    },
  } satisfies Preset.ThemeConfig,

  plugins: [
    ['./plugins/chapter-mapper-plugin.js', {}],
  ],
};

export default config;
```

**Update these fields:**
- `url`: Your GitHub Pages URL
- `baseUrl`: Your repository name (e.g., `/hackathon-book/`)
- `organizationName`: Your GitHub username
- `projectName`: Your repository name

### 3.2 Create Environment Files

**`.env.development`:**
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=10000
```

**`.env.production`:**
```bash
REACT_APP_API_URL=https://api.example.com
REACT_APP_API_TIMEOUT=30000
```

**Add to `.gitignore`:**
```
.env.production
.env.development.local
.env.production.local
```

---

## Step 4: Create Chapter Mapper Plugin

```bash
mkdir plugins
```

**`plugins/chapter-mapper-plugin.js`:**

```javascript
module.exports = function chapterMapperPlugin(context, options) {
  return {
    name: 'chapter-mapper-plugin',

    contentLoaded({ actions }) {
      const chapterMap = {
        '/docs/intro': null,
        '/docs/module-1-ros2/nodes': 'ch-ros2-nodes',
        '/docs/module-1-ros2/topics': 'ch-ros2-topics',
        '/docs/module-1-ros2/services': 'ch-ros2-services',
        '/docs/module-1-ros2/urdf': 'ch-ros2-urdf',
        '/docs/module-2-gazebo/simulation-basics': 'ch-gazebo-basics',
        '/docs/module-2-gazebo/sensors': 'ch-gazebo-sensors',
        '/docs/module-3-isaac/isaac-sim': 'ch-isaac-sim',
        '/docs/module-3-isaac/isaac-ros': 'ch-isaac-ros',
        '/docs/module-4-vla/voice-commands': 'ch-vla-voice',
        '/docs/module-4-vla/capstone': 'ch-vla-capstone',
      };

      actions.createData('chapter-map.json', JSON.stringify(chapterMap, null, 2));
    },
  };
};
```

---

## Step 5: Create Custom Hooks

### 5.1 `src/hooks/useChapterId.ts`

```typescript
import { useLocation } from '@docusaurus/router';
import { usePluginData } from '@docusaurus/useGlobalData';

export function useChapterId(): string | null {
  const { pathname } = useLocation();
  const chapterMap = usePluginData('chapter-mapper-plugin')?.['chapter-map.json'] as Record<string, string | null>;

  const normalizedPath = pathname.replace(/\/$/, '').split('#')[0];
  return chapterMap?.[normalizedPath] || null;
}
```

### 5.2 `src/hooks/useApiClient.ts`

```typescript
import { useDocusaurusContext } from '@docusaurus/useDocusaurusContext';

export function useApiClient() {
  const { siteConfig } = useDocusaurusContext();
  const { apiUrl, apiTimeout } = siteConfig.customFields as {
    apiUrl: string;
    apiTimeout: string;
  };

  const fetchData = async (endpoint: string, options: RequestInit = {}) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), parseInt(apiTimeout));

    try {
      const response = await fetch(`${apiUrl}${endpoint}`, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}`);
      }

      return await response.json();
    } finally {
      clearTimeout(timeoutId);
    }
  };

  return { apiUrl, fetchData };
}
```

### 5.3 `src/hooks/useTextSelection.ts`

```typescript
import { useEffect, useState } from 'react';

export interface TextSelection {
  text: string;
  range: DOMRect | null;
}

export function useTextSelection() {
  const [selection, setSelection] = useState<TextSelection | null>(null);

  useEffect(() => {
    const handleSelection = () => {
      const sel = window.getSelection();
      if (!sel || sel.rangeCount === 0) {
        setSelection(null);
        return;
      }

      const text = sel.toString().trim();
      if (text.length > 0) {
        const range = sel.getRangeAt(0).getBoundingClientRect();
        setSelection({ text, range });
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

  return selection;
}
```

---

## Step 6: Create Chatbot Widget Component

### 6.1 `src/components/ChatbotWidget/index.tsx`

```typescript
import React, { useState } from 'react';
import { useApiClient } from '@site/src/hooks/useApiClient';
import { useChapterId } from '@site/src/hooks/useChapterId';
import styles from './styles.module.css';

interface ChatbotQuery {
  query_text: string;
  chapter_id: string | null;
  user_id: string;
  selected_text?: string;
}

interface ChatbotResponse {
  answer: string;
  sources: Array<{
    chapter_id: string;
    section_title: string;
    similarity_score: number;
  }>;
  confidence_score: number;
  grounding_status: string;
}

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<ChatbotResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { fetchData } = useApiClient();
  const chapterId = useChapterId();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);

    const queryData: ChatbotQuery = {
      query_text: query,
      chapter_id: chapterId,
      user_id: 'guest-user',
    };

    try {
      const data = await fetchData('/v1/query', {
        method: 'POST',
        body: JSON.stringify(queryData),
      });
      setResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={styles.toggleButton}
        aria-label="Toggle chatbot"
      >
        💬
      </button>

      {isOpen && (
        <div className={styles.chatPanel}>
          <div className={styles.header}>
            <h3>Ask a Question</h3>
            <button onClick={() => setIsOpen(false)}>×</button>
          </div>

          <div className={styles.content}>
            {response && (
              <div className={styles.response}>
                <p><strong>Answer:</strong> {response.answer}</p>
                <div className={styles.sources}>
                  <strong>Sources:</strong>
                  <ul>
                    {response.sources.map((source, idx) => (
                      <li key={idx}>
                        {source.section_title} (similarity: {source.similarity_score.toFixed(2)})
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {error && <div className={styles.error}>{error}</div>}
          </div>

          <form onSubmit={handleSubmit} className={styles.form}>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question..."
              disabled={isLoading}
              className={styles.input}
            />
            <button type="submit" disabled={isLoading} className={styles.submitButton}>
              {isLoading ? 'Loading...' : 'Ask'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
```

### 6.2 `src/components/ChatbotWidget/styles.module.css`

```css
.container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 999;
}

.toggleButton {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #0066cc;
  border: none;
  cursor: pointer;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: transform 0.2s;
}

.toggleButton:hover {
  transform: scale(1.1);
}

.chatPanel {
  position: absolute;
  bottom: 70px;
  right: 0;
  width: 350px;
  max-height: 500px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 5px 40px rgba(0, 0, 0, 0.16);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  background: #0066cc;
  color: white;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h3 {
  margin: 0;
  font-size: 16px;
}

.header button {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  max-height: 350px;
}

.response {
  margin-bottom: 16px;
}

.sources {
  margin-top: 12px;
  font-size: 14px;
}

.sources ul {
  margin: 8px 0;
  padding-left: 20px;
}

.error {
  color: #d32f2f;
  padding: 12px;
  background: #ffebee;
  border-radius: 4px;
}

.form {
  padding: 12px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 8px;
}

.input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.submitButton {
  padding: 8px 16px;
  background: #0066cc;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.submitButton:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

---

## Step 7: Swizzle Root Component

```bash
mkdir -p src/theme
```

**`src/theme/Root.tsx`:**

```typescript
import React from 'react';
import ChatbotWidget from '@site/src/components/ChatbotWidget';

export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <ChatbotWidget />
    </>
  );
}
```

---

## Step 8: Create Textbook Content

### 8.1 Update `docs/intro.md`

```markdown
---
sidebar_position: 1
---

# Welcome to Physical AI & Humanoid Robotics

Learn to build intelligent physical systems that understand and interact with the real world.

## Course Modules

1. **ROS 2 Fundamentals** - The robotic nervous system
2. **Gazebo Simulation** - Digital twin environments
3. **NVIDIA Isaac** - AI-powered perception
4. **Vision-Language-Action** - LLM-to-Robot integration

Ask questions using the chatbot widget in the bottom-right corner!
```

### 8.2 Create Chapter Structure

```bash
mkdir -p docs/module-1-ros2
mkdir -p docs/module-2-gazebo
mkdir -p docs/module-3-isaac
mkdir -p docs/module-4-vla
```

**Example chapter (`docs/module-1-ros2/nodes.md`):**

```markdown
---
sidebar_position: 1
---

# ROS 2 Nodes

ROS 2 nodes are the fundamental building blocks of robotic systems. Each node is an independent process that performs a specific task.

## Key Concepts

1. **Process Isolation**: Each node runs as a separate process
2. **Communication**: Nodes communicate via topics, services, and actions
3. **Modularity**: Nodes can be developed and tested independently

## Example Code

\`\`\`python
import rclpy
from rclpy.node import Node

class MinimalNode(Node):
    def __init__(self):
        super().__init__('minimal_node')
        self.get_logger().info('Node started!')

def main():
    rclpy.init()
    node = MinimalNode()
    rclpy.spin(node)
    rclpy.shutdown()
\`\`\`

Try asking the chatbot: "What is the purpose of rclpy.spin()?"
```

---

## Step 9: Test Locally

```bash
npm run start
```

**Verification checklist:**
- [ ] Site loads at `http://localhost:3000`
- [ ] Navigation sidebar shows modules
- [ ] Chatbot widget appears in bottom-right
- [ ] Clicking chatbot opens chat panel
- [ ] Submitting a question calls backend API
- [ ] Response displays answer and sources

---

## Step 10: Deploy to GitHub Pages

### 10.1 Create GitHub Actions Workflow

```bash
mkdir -p .github/workflows
```

**`.github/workflows/deploy.yml`:**

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: ./frontend
        run: npm install --frozen-lockfile

      - name: Build website
        working-directory: ./frontend
        env:
          REACT_APP_API_URL: https://api.example.com
        run: npm run build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: frontend/build

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/deploy-pages@v4
        id: deployment
```

### 10.2 Enable GitHub Pages

1. Go to GitHub.com → Repository → Settings → Pages
2. Source: Select **"GitHub Actions"**
3. Push code to trigger deployment
4. Wait ~2 minutes for deployment to complete
5. Visit site at `https://your-username.github.io/hackathon-book/`

---

## Troubleshooting

### Issue: Chatbot returns "Service unavailable"

**Solution**: Verify backend is running:
```bash
curl http://localhost:8000/health
```

### Issue: 404 errors on GitHub Pages

**Solution**: Check `baseUrl` in `docusaurus.config.ts` matches repository name.

### Issue: Environment variables not working

**Solution**: Ensure `dotenv` is installed and `.env` files are in `frontend/` directory.

### Issue: TypeScript errors

**Solution**: Run type check:
```bash
npm run typecheck
```

---

## Next Steps

1. Write remaining 4+ chapters for all modules
2. Implement selected text search tooltip
3. Add more styling and branding
4. Test on mobile devices
5. Submit to hackathon!

---

## Resources

- [Docusaurus Documentation](https://docusaurus.io/docs)
- [React Hooks Reference](https://react.dev/reference/react)
- [Floating UI Docs](https://floating-ui.com/docs/react)
- Backend API: See `backend/src/api/main.py` for endpoint details
