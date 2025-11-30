---
name: docusaurus-integration-patterns
description: Integration patterns for embedding interactive React components and features into Docusaurus documentation sites. Use when adding custom UI elements, chat widgets, personalization buttons, or interactive code editors to Docusaurus content.
---

# Skill: Docusaurus Integration Patterns

**Version**: 1.0.0
**Created**: 2025-11-28
**Category**: Frontend Integration
**Decision Points**: 3

## Description

This skill provides proven patterns for integrating custom React components and interactive features into Docusaurus sites. It covers component architecture, MDX usage, styling isolation, state management, and deployment best practices.

## When to Use This Skill

**Apply this skill when:**
- Adding custom React components to Docusaurus pages (chat widgets, personalization buttons, interactive demos)
- Embedding third-party services (authentication, analytics, payment)
- Building interactive educational features (code playgrounds, quizzes, simulations)
- Implementing global features (navigation enhancements, search, theming)
- Troubleshooting component rendering or styling issues in Docusaurus

**Skip this skill when:**
- Writing pure markdown content (no custom components needed)
- Using only built-in Docusaurus features (sidebar, navbar, admonitions)
- Working with standard HTML/CSS (no React integration required)

## Persona

You are a frontend developer integrating React components into Docusaurus who thinks about component architecture the way a library author thinks about API design:

- **Isolation**: Components don't leak styles or state globally
- **Reusability**: Components work across multiple pages/contexts
- **Performance**: Components don't block page load or cause hydration issues
- **Accessibility**: Components work with keyboard navigation and screen readers

Your goal: Add rich interactive features to documentation without breaking Docusaurus conventions or degrading performance.

## Analytical Questions

Before integrating components, analyze:

### 1. **Component Scope & Placement**
- Is this component page-specific or site-wide?
- Should it render on every page (global) or specific pages (local)?
- Does it need to work in MDX content or only in custom pages?

### 2. **State Management Needs**
- Does the component need to share state across pages? (user auth, preferences)
- Is state ephemeral (chat widget session) or persistent (user profile)?
- What's the state hydration strategy? (client-only, SSR-compatible, localStorage)

### 3. **Styling Strategy**
- Should styles be scoped (CSS modules) or global (theme variables)?
- Does the component need to adapt to Docusaurus themes (light/dark mode)?
- Are there style conflicts with Docusaurus defaults?

## Decision Principles

Apply these patterns when integrating with Docusaurus:

### 1. **Component Location Pattern**

```
docusaurus-site/
├── src/
│   ├── components/          # ← Reusable React components
│   │   ├── ChatWidget/
│   │   │   ├── index.tsx
│   │   │   └── styles.module.css
│   │   ├── PersonalizeButton/
│   │   │   ├── index.tsx
│   │   │   └── styles.module.css
│   │   └── UserProfile/
│   │       ├── index.tsx
│   │       └── styles.module.css
│   │
│   ├── pages/               # ← Custom pages (not in docs/)
│   │   └── dashboard.tsx
│   │
│   ├── theme/               # ← Override Docusaurus components (swizzled)
│   │   └── Root.tsx         # ← Global wrapper (auth, state)
│   │
│   └── css/
│       └── custom.css       # ← Global styles
│
├── docs/                    # ← Markdown/MDX content
│   └── chapter-1.mdx        # ← Can import from src/components
│
└── docusaurus.config.js     # ← Site configuration
```

**Principle**:
- `src/components/` for reusable React components
- `src/theme/` for global wrappers and overrides
- `docs/` for content (can import components)
- `src/pages/` for custom non-documentation pages

### 2. **MDX Component Import Pattern**

```mdx
---
title: Chapter 1: Introduction
sidebar_position: 1
---

import ChatWidget from '@site/src/components/ChatWidget';
import PersonalizeButton from '@site/src/components/PersonalizeButton';

# Chapter 1: Introduction to Physical AI

<PersonalizeButton chapterId="chapter-1" />

## What is Physical AI?

Physical AI combines artificial intelligence with physical systems...

[Content continues...]

<ChatWidget
  context="chapter-1"
  suggestions={["What is Physical AI?", "Explain embodied AI"]}
/>
```

**Pattern Breakdown**:
```tsx
// src/components/PersonalizeButton/index.tsx
import React from 'react';
import styles from './styles.module.css';

interface PersonalizeButtonProps {
  chapterId: string;
}

export default function PersonalizeButton({ chapterId }: PersonalizeButtonProps) {
  const handleClick = () => {
    // Implementation
  };

  return (
    <button className={styles.personalizeButton} onClick={handleClick}>
      ✨ Personalize this chapter
    </button>
  );
}
```

```css
/* src/components/PersonalizeButton/styles.module.css */
.personalizeButton {
  background: var(--ifm-color-primary);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  margin-bottom: 1rem;
}

.personalizeButton:hover {
  background: var(--ifm-color-primary-dark);
}

/* Adapt to Docusaurus dark mode */
[data-theme='dark'] .personalizeButton {
  background: var(--ifm-color-primary-light);
}
```

**Principle**: Use `@site/` alias for imports, CSS modules for styling, Docusaurus CSS variables for theming.

### 3. **Global State Management Pattern**

```tsx
// src/theme/Root.tsx (swizzle this to wrap entire site)
import React, { ReactNode } from 'react';
import { UserProfileProvider } from '../contexts/UserProfileContext';
import { AuthProvider } from '../contexts/AuthContext';

interface RootProps {
  children: ReactNode;
}

export default function Root({ children }: RootProps) {
  return (
    <AuthProvider>
      <UserProfileProvider>
        {children}
      </UserProfileProvider>
    </AuthProvider>
  );
}
```

```tsx
// src/contexts/UserProfileContext.tsx
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface UserProfile {
  software_level: 'beginner' | 'intermediate' | 'advanced';
  hardware_access: 'simulation-only' | 'edge-kit' | 'full-lab';
}

interface UserProfileContextType {
  profile: UserProfile | null;
  updateProfile: (profile: UserProfile) => void;
}

const UserProfileContext = createContext<UserProfileContextType | undefined>(undefined);

export function UserProfileProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<UserProfile | null>(null);

  // Load from localStorage on mount (client-side only)
  useEffect(() => {
    const saved = localStorage.getItem('userProfile');
    if (saved) {
      setProfile(JSON.parse(saved));
    }
  }, []);

  const updateProfile = (newProfile: UserProfile) => {
    setProfile(newProfile);
    localStorage.setItem('userProfile', JSON.stringify(newProfile));
  };

  return (
    <UserProfileContext.Provider value={{ profile, updateProfile }}>
      {children}
    </UserProfileContext.Provider>
  );
}

export function useUserProfile() {
  const context = useContext(UserProfileContext);
  if (!context) {
    throw new Error('useUserProfile must be used within UserProfileProvider');
  }
  return context;
}
```

```tsx
// Usage in any component
import { useUserProfile } from '@site/src/contexts/UserProfileContext';

export default function PersonalizeButton({ chapterId }) {
  const { profile, updateProfile } = useUserProfile();

  return (
    <div>
      <p>Current level: {profile?.software_level || 'Not set'}</p>
      <button onClick={() => {/* personalize logic */}}>
        Personalize
      </button>
    </div>
  );
}
```

**Principle**: Use React Context for global state (auth, user preferences). Wrap in `src/theme/Root.tsx` to provide context site-wide.

### 4. **Client-Only Rendering Pattern**

Some components (chat widgets, auth) must render only on client (not during SSR).

```tsx
// src/components/ChatWidget/index.tsx
import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';

interface ChatWidgetProps {
  context: string;
  suggestions?: string[];
}

export default function ChatWidget(props: ChatWidgetProps) {
  return (
    <BrowserOnly fallback={<div>Loading chat...</div>}>
      {() => <ChatWidgetClient {...props} />}
    </BrowserOnly>
  );
}

// Separate client-only component
function ChatWidgetClient({ context, suggestions }: ChatWidgetProps) {
  // This code only runs in browser (can use window, localStorage, etc.)
  const [messages, setMessages] = React.useState([]);

  return (
    <div className="chat-widget">
      {/* Chat UI */}
    </div>
  );
}
```

**Principle**: Wrap client-only code in `<BrowserOnly>` to avoid SSR hydration mismatches.

### 5. **API Integration Pattern**

```tsx
// src/services/api.ts
const API_BASE = process.env.NODE_ENV === 'production'
  ? 'https://api.example.com'
  : 'http://localhost:8000';

export async function sendChatMessage(query: string, userLevel: string) {
  const response = await fetch(`${API_BASE}/api/v1/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}` // From auth context
    },
    body: JSON.stringify({ query, user_level: userLevel })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'API request failed');
  }

  return response.json();
}

function getAuthToken(): string {
  // Get from auth context or localStorage
  return localStorage.getItem('authToken') || '';
}
```

```tsx
// Usage in component
import { sendChatMessage } from '@site/src/services/api';
import { useUserProfile } from '@site/src/contexts/UserProfileContext';

export default function ChatWidgetClient({ context }) {
  const { profile } = useUserProfile();
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const handleSend = async (query: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage(query, profile?.software_level || 'intermediate');
      // Handle response
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {error && <div className="error">{error}</div>}
      {/* Chat UI */}
    </div>
  );
}
```

**Principle**: Centralize API calls in `src/services/`. Handle loading and error states. Use environment variables for API URLs.

### 6. **Styling Best Practices**

```css
/* src/components/ChatWidget/styles.module.css */

/* Use CSS modules for component isolation */
.chatWidget {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  width: 350px;
  max-height: 500px;
  background: var(--ifm-background-color);
  border: 1px solid var(--ifm-color-emphasis-300);
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

/* Use Docusaurus CSS variables for theme consistency */
.chatInput {
  background: var(--ifm-background-surface-color);
  color: var(--ifm-font-color-base);
  border: 1px solid var(--ifm-color-emphasis-300);
}

/* Adapt to dark mode automatically */
[data-theme='dark'] .chatWidget {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .chatWidget {
    width: 90%;
    left: 5%;
    right: 5%;
  }
}
```

**Docusaurus CSS Variables Reference**:
```css
/* Colors */
--ifm-color-primary
--ifm-color-primary-dark
--ifm-color-primary-light
--ifm-background-color
--ifm-background-surface-color
--ifm-font-color-base

/* Spacing */
--ifm-spacing-horizontal
--ifm-spacing-vertical

/* Typography */
--ifm-font-size-base
--ifm-heading-font-weight
```

**Principle**: Use CSS modules for scoping, Docusaurus variables for theming, test in both light/dark modes.

### 7. **Configuration Pattern**

```js
// docusaurus.config.js
module.exports = {
  title: 'Physical AI Course',
  url: 'https://example.com',
  baseUrl: '/',

  // Custom fields (accessible in React components)
  customFields: {
    apiUrl: process.env.API_URL || 'http://localhost:8000',
    enableChat: process.env.ENABLE_CHAT === 'true',
  },

  // Plugins
  plugins: [
    // Add custom webpack config if needed
    function (context, options) {
      return {
        name: 'custom-webpack-config',
        configureWebpack(config, isServer) {
          return {
            resolve: {
              fallback: {
                // Polyfills for Node.js modules in browser
                crypto: require.resolve('crypto-browserify'),
              },
            },
          };
        },
      };
    },
  ],

  themeConfig: {
    navbar: {
      items: [
        // Custom navbar items
      ],
    },
  },
};
```

```tsx
// Accessing config in components
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

export default function ChatWidget() {
  const { siteConfig } = useDocusaurusContext();
  const { apiUrl, enableChat } = siteConfig.customFields;

  if (!enableChat) {
    return null; // Don't render if chat is disabled
  }

  // Use apiUrl for API calls
  return <div>Chat Widget</div>;
}
```

**Principle**: Use `customFields` for environment-specific config. Access via `useDocusaurusContext()`.

## Usage Example

**Scenario**: Add a floating chat widget to all documentation pages

**Invocation**:
```
I want to add a floating chat widget to the bottom-right of every documentation page.
The widget should:
- Be accessible from any page
- Maintain conversation state across page navigation
- Use the user's profile (from auth context) to personalize responses
- Call our FastAPI backend at /api/v1/chat

Use the docusaurus-integration-patterns skill to guide implementation.
```

**Expected Implementation**:

```tsx
// 1. Create component: src/components/ChatWidget/index.tsx
import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';

export default function ChatWidget() {
  return (
    <BrowserOnly fallback={<div>Loading chat...</div>}>
      {() => <ChatWidgetClient />}
    </BrowserOnly>
  );
}

function ChatWidgetClient() {
  const [isOpen, setIsOpen] = React.useState(false);
  const [messages, setMessages] = React.useState([]);

  return (
    <div className={styles.chatContainer}>
      {!isOpen && (
        <button className={styles.chatButton} onClick={() => setIsOpen(true)}>
          💬 Ask AI Tutor
        </button>
      )}
      {isOpen && (
        <div className={styles.chatWidget}>
          {/* Chat UI implementation */}
        </div>
      )}
    </div>
  );
}

// 2. Add to global Root: src/theme/Root.tsx
import ChatWidget from '../components/ChatWidget';

export default function Root({ children }) {
  return (
    <AuthProvider>
      <UserProfileProvider>
        {children}
        <ChatWidget />  {/* Renders on every page */}
      </UserProfileProvider>
    </AuthProvider>
  );
}

// 3. Style: src/components/ChatWidget/styles.module.css
.chatContainer {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  z-index: 1000;
}

.chatButton {
  background: var(--ifm-color-primary);
  /* ... */
}

.chatWidget {
  width: 350px;
  height: 500px;
  background: var(--ifm-background-color);
  /* ... */
}
```

## Self-Check Validation

After integrating components, verify:

- [ ] **Component renders correctly**: Works in both light and dark themes
- [ ] **No hydration errors**: Check browser console for React SSR mismatches
- [ ] **Styles are isolated**: CSS modules prevent global style leaks
- [ ] **Mobile responsive**: Test on 320px, 768px, 1024px viewports
- [ ] **Accessible**: Can navigate with keyboard (Tab, Enter, Esc)
- [ ] **Performance**: Page load time not significantly impacted (<100ms overhead)

## Common Issues and Fixes

### Issue: "window is not defined" error
**Cause**: Component uses browser APIs during SSR
**Fix**: Wrap in `<BrowserOnly>` component

### Issue: Styles not applying
**Cause**: Forgot `.module.css` extension or incorrect import
**Fix**: Use `import styles from './styles.module.css'` and apply as `className={styles.myClass}`

### Issue: Context not available in component
**Cause**: Component rendered outside provider tree
**Fix**: Wrap entire site in `src/theme/Root.tsx` with context providers

### Issue: Dark mode styles broken
**Cause**: Not using Docusaurus CSS variables
**Fix**: Replace hardcoded colors with `var(--ifm-color-primary)` etc.

---

**Key Principle**: Follow Docusaurus conventions (component location, CSS modules, BrowserOnly) to avoid fighting the framework. When in doubt, check official Docusaurus docs.
