# Physical AI & Humanoid Robotics Textbook

**An interactive, AI-powered educational platform for learning ROS 2, Gazebo, NVIDIA Isaac, and Vision-Language-Action models.**

[![Deploy to GitHub Pages](https://github.com/ISMAIL-AHMED-SHAH/Hackathon-Book/actions/workflows/deploy.yml/badge.svg)](https://github.com/ISMAIL-AHMED-SHAH/Hackathon-Book/actions/workflows/deploy.yml)

🌐 **Live Site**: [https://ismail-ahmed-shah.github.io/Hackathon-Book/](https://ismail-ahmed-shah.github.io/Hackathon-Book/)

---

## 📚 Overview

This project is a comprehensive textbook platform built with **Docusaurus** that teaches Physical AI and Humanoid Robotics concepts through:

- **10 Interactive Chapters** across 4 modules
- **AI-Powered RAG Chatbot** for instant Q&A
- **Context-Aware Search** with selected text queries
- **B1 English Proficiency** for accessibility
- **Code Examples** in Python, Bash, XML, and YAML

---

## 🎯 Features

### 📖 Structured Learning Content

- **Module 1: ROS 2 Fundamentals** (4 chapters)
  - Nodes, Topics, Services, URDF
- **Module 2: Gazebo Simulation** (2 chapters)
  - Simulation basics, sensor simulation
- **Module 3: NVIDIA Isaac** (2 chapters)
  - Isaac Sim, Isaac ROS integration
- **Module 4: Vision-Language-Action** (2 chapters)
  - Voice commands with Whisper, Capstone project

### 💬 AI Chatbot (RAG Architecture)

- **Vector Search**: Qdrant for semantic similarity
- **LLM Integration**: OpenAI GPT-4 for answer generation
- **Source Citations**: Chapter references with confidence scores
- **Context-Aware**: Automatically detects current chapter

### ✨ Interactive Features

- **Text Selection Search**: Highlight text → Ask chatbot
- **Dark Mode**: System preference detection
- **Responsive Design**: Mobile-optimized UI
- **Sequential Navigation**: Next/Previous chapter links

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ ([Download](https://nodejs.org/))
- **npm** 9+ (comes with Node.js)
- **Git** ([Download](https://git-scm.com/))

### Installation

```bash
# Clone the repository
git clone https://github.com/ISMAIL-AHMED-SHAH/Hackathon-Book.git
cd Hackathon-Book

# Install frontend dependencies
cd frontend
npm install
```

### Development Server

```bash
# Start local development server
cd frontend
npm run start
```

Open [http://localhost:3000/Hackathon-Book/](http://localhost:3000/Hackathon-Book/) in your browser.

### Build for Production

```bash
# Build static site
cd frontend
npm run build

# Serve locally to test
npm run serve
```

Build output: `frontend/build/`

---

## 📁 Project Structure

```
hackathon-book/
├── frontend/                      # Docusaurus frontend
│   ├── docs/                      # Textbook content (Markdown/MDX)
│   │   ├── intro.md               # Landing page
│   │   ├── module-1-ros2/         # ROS 2 chapters
│   │   ├── module-2-gazebo/       # Gazebo chapters
│   │   ├── module-3-isaac/        # NVIDIA Isaac chapters
│   │   └── module-4-vla/          # VLA chapters + Capstone
│   ├── src/
│   │   ├── components/            # React components
│   │   │   ├── ChatbotWidget/     # Floating chatbot UI
│   │   │   └── SelectionTooltip/  # Text selection tooltip (optional)
│   │   ├── hooks/                 # Custom React hooks
│   │   │   ├── useApiClient.ts    # API fetch wrapper
│   │   │   ├── useChapterId.ts    # Chapter context detection
│   │   │   └── useTextSelection.ts # Browser selection API
│   │   ├── theme/
│   │   │   └── Root.tsx           # Global component injection
│   │   └── types/                 # TypeScript type definitions
│   ├── plugins/
│   │   └── chapter-mapper-plugin.js # Build-time chapter ID mapping
│   ├── docusaurus.config.ts       # Main configuration
│   ├── sidebars.ts                # Navigation sidebar
│   └── package.json               # Dependencies
├── backend/                       # FastAPI backend (optional)
│   ├── src/
│   │   ├── api/                   # API endpoints
│   │   ├── services/              # Vector search, LLM
│   │   └── core/                  # Metrics, config
│   └── requirements.txt
├── .github/workflows/
│   └── deploy.yml                 # GitHub Actions CI/CD
├── DEPLOYMENT.md                  # Deployment guide
├── GITHUB_PAGES_SETUP.md          # Quick setup instructions
├── REUSABLE_COMPONENTS.md         # Reusability documentation
└── README.md                      # This file
```

---

## 🛠️ Technology Stack

### Frontend

- **Framework**: [Docusaurus 3.7.1](https://docusaurus.io/) (React-based static site generator)
- **Language**: TypeScript
- **UI Library**: React 18
- **Styling**: CSS Modules
- **Build Tool**: Webpack (bundled with Docusaurus)

### Backend (Optional)

- **Framework**: FastAPI (Python)
- **Vector DB**: Qdrant
- **LLM**: OpenAI GPT-4
- **Embedding Model**: OpenAI text-embedding-3-small

### CI/CD

- **Deployment**: GitHub Actions → GitHub Pages
- **Hosting**: GitHub Pages (static)

---

## 📖 Usage Guide

### Reading Textbook Content

1. Navigate to the **Textbook** tab in the navbar
2. Browse chapters in the left sidebar
3. Use **Next/Previous** links at the bottom of each chapter
4. Toggle **dark mode** via the theme switcher (top-right)

### Using the AI Chatbot

1. Click the **chatbot button** (bottom-right corner)
2. Type your question (e.g., "What are ROS 2 nodes?")
3. Press **Send** or hit **Enter**
4. View the answer with **source citations** and **confidence scores**
5. The chatbot automatically includes context from your current chapter

### Text Selection Search

1. Highlight any text in the textbook
2. Click **"Ask about this"** in the tooltip
3. Chatbot opens with the selected text as context

---

## 🌐 Deployment

This project is deployed via **GitHub Actions** to **GitHub Pages**.

### Automated Deployment

Every push to `main` or `001-docusaurus-textbook` branches triggers:

1. **Build**: Install dependencies, compile Docusaurus site
2. **Deploy**: Upload artifact to GitHub Pages
3. **Live**: Site updates within 2-3 minutes

### Manual Deployment

See [GITHUB_PAGES_SETUP.md](./GITHUB_PAGES_SETUP.md) for step-by-step instructions.

### Environment Variables

Create `frontend/.env.production` for production builds:

```bash
REACT_APP_API_URL=https://your-backend-api.com
REACT_APP_API_TIMEOUT=30000
```

---

## 🧪 Testing

### Manual Testing Checklist

- [ ] All 10 chapters load without errors
- [ ] Navigation (Next/Previous) works correctly
- [ ] Chatbot opens and responds to queries
- [ ] Source citations display correctly
- [ ] Dark mode toggles properly
- [ ] Mobile responsive layout works
- [ ] Text selection tooltip appears (if enabled)

### Build Verification

```bash
cd frontend
npm run build  # Should complete without errors
```

### Local Preview

```bash
cd frontend
npm run serve  # Test production build locally
```

---

## 🤝 Contributing

This project follows **Spec-Driven Development (SDD)** with structured planning:

1. **Spec**: See `specs/001-docusaurus-textbook/spec.md`
2. **Plan**: See `specs/001-docusaurus-textbook/plan.md`
3. **Tasks**: See `specs/001-docusaurus-textbook/tasks.md`

### Development Workflow

1. Create a feature branch from `main`
2. Make changes following the tasks list
3. Test locally with `npm run start`
4. Commit with descriptive messages
5. Push and create a pull request

---

## 📚 Documentation

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Complete deployment guide
- **[GITHUB_PAGES_SETUP.md](./GITHUB_PAGES_SETUP.md)** - Quick GitHub Pages setup
- **[REUSABLE_COMPONENTS.md](./REUSABLE_COMPONENTS.md)** - Reusable components catalog
- **[RUN_BACKEND.md](./RUN_BACKEND.md)** - Backend setup instructions (if applicable)
- **[TESTING.md](./TESTING.md)** - Testing documentation (if applicable)

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](./LICENSE) for details.

---

## 👥 Authors

- **Ismail Ahmed Shah** - [GitHub](https://github.com/ISMAIL-AHMED-SHAH)

---

## 🙏 Acknowledgments

- **[Docusaurus](https://docusaurus.io/)** - Static site generator
- **[ROS 2](https://docs.ros.org/)** - Robot Operating System
- **[NVIDIA Isaac](https://developer.nvidia.com/isaac-sdk)** - Robotics simulation platform
- **[OpenAI](https://openai.com/)** - GPT-4 and Whisper models

---

## 🐛 Issues & Support

Found a bug or have a feature request? Please open an issue on the [GitHub Issues](https://github.com/ISMAIL-AHMED-SHAH/Hackathon-Book/issues) page.

---

## 📊 Project Status

**Current Version**: 1.0.0 (MVP)

**Completion**: 54/85 tasks (64%)

### Completed Features

- ✅ User Story 1: Read Interactive Textbook (100%)
- ✅ User Story 2: RAG Chatbot Integration (100%)
- ✅ User Story 4: GitHub Pages Deployment (64%)
- ✅ User Story 5: Chapter Navigation (100%)
- ✅ Phase 8: Polish (Partial - dark mode, branding, mobile, educational standards)

### In Progress

- ⏳ Backend API deployment (optional)
- ⏳ Cross-browser testing
- ⏳ Performance optimization

---

**Built with ❤️ for the Physical AI & Robotics community**
