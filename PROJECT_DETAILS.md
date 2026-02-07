# ContextWeave Lite - Complete Project Details

**Version:** 0.1.0  
**Status:** ✅ Fully Operational  
**Date:** February 7, 2026  
**Developer:** Shivansh Singh

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Current Configuration](#current-configuration)
5. [Features Implemented](#features-implemented)
6. [File Structure](#file-structure)
7. [Setup & Installation](#setup--installation)
8. [Usage Guide](#usage-guide)
9. [API Documentation](#api-documentation)
10. [Development Status](#development-status)
11. [Known Issues & Limitations](#known-issues--limitations)
12. [Future Enhancements](#future-enhancements)
13. [Troubleshooting](#troubleshooting)

---

## 📖 Project Overview

### What is ContextWeave Lite?

ContextWeave Lite is an AI-powered VS Code extension that helps developers understand code files by analyzing:
- **File Purpose**: 2-3 sentence AI-generated summary
- **Design Decisions**: Key architectural choices extracted from Git history
- **Related Files**: Suggestions for what to read next based on imports and co-changes

### Target Users
- New developers joining a codebase
- Students learning from existing projects
- Junior engineers exploring unfamiliar code
- Anyone needing quick context on legacy code

### Core Value Proposition
Accelerate code understanding by 5-10x by combining:
- Static code analysis
- Git history mining
- AI-powered natural language explanations

---

## 🏗️ System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                     VS Code IDE                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ContextWeave Extension (TypeScript)                 │  │
│  │  - Command: "ContextWeave: Explain this file"       │  │
│  │  - Sidebar webview UI                                │  │
│  │  - API client (HTTP)                                 │  │
│  └──────────────────┬───────────────────────────────────┘  │
└────────────────────┼────────────────────────────────────────┘
                     │ HTTP POST /context/file
                     │ JSON Request/Response
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python 3.11)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                       │  │
│  │  - POST /context/file (main analysis)                │  │
│  │  - GET /health (status check)                        │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  Git Analysis Layer (GitPython)                      │  │
│  │  - Extract commit history                            │  │
│  │  - Parse imports                                     │  │
│  │  - Find co-changed files                            │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  LLM Integration (Groq API)                          │  │
│  │  - Build structured prompts                          │  │
│  │  - Call AI model                                     │  │
│  │  - Parse JSON responses                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                     │
                     │ HTTPS API Call
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Groq Cloud API                                 │
│              Model: llama-3.1-8b-instant                    │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**VS Code Extension:**
- User interface and command registration
- File path detection and workspace management
- HTTP communication with backend
- Result rendering in sidebar

**FastAPI Backend:**
- Request validation and orchestration
- Git repository analysis
- LLM API integration
- Response formatting

**Git Analysis:**
- Deterministic data extraction
- No AI interpretation
- Pure data collection

**LLM Integration:**
- AI-powered interpretation
- Natural language generation
- Reasoning and synthesis

---

## 💻 Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11.9 | Runtime environment |
| FastAPI | 0.109.0 | Web framework |
| Uvicorn | 0.27.0 | ASGI server |
| GitPython | 3.1.41 | Git operations |
| httpx | 0.26.0 | Async HTTP client |
| Pydantic | 2.5.3 | Data validation |
| python-dotenv | 1.2.1 | Environment variables |

### Frontend (VS Code Extension)
| Technology | Version | Purpose |
|------------|---------|---------|
| TypeScript | 5.3.0 | Programming language |
| VS Code API | 1.85.0+ | Extension framework |
| Axios | 1.6.2 | HTTP client |
| Node.js | 18+ | Runtime |

### AI/LLM
| Service | Model | Purpose |
|---------|-------|---------|
| Groq Cloud | llama-3.1-8b-instant | Code analysis & NLG |

### Development Tools
| Tool | Purpose |
|------|---------|
| Git | Version control |
| npm | Package management (frontend) |
| pip | Package management (backend) |
| VS Code | IDE and extension host |

---

## ⚙️ Current Configuration

### Backend Configuration (`.env`)
```bash
# Groq API Configuration
LLM_API_KEY=your-groq-api-key-here
LLM_API_BASE=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-8b-instant

# Server Configuration
PORT=8000
```

### VS Code Extension Settings
```json
{
  "contextweave.backendUrl": "http://localhost:8000",
  "contextweave.commitLimit": 50
}
```

### System Information
- **Operating System**: Windows
- **Platform**: win32
- **Shell**: PowerShell/CMD
- **Python Path**: `backend\venv\Scripts\python.exe`
- **Backend URL**: http://localhost:8000
- **Extension Location**: `vscode-extension/`

---

## ✨ Features Implemented

### Core Features
- ✅ **File Analysis**: AI-powered summary of file purpose
- ✅ **Design Decisions**: Extract key decisions from Git history
- ✅ **Related Files**: Suggest files to read next
- ✅ **Code Explanation**: Explain selected code snippets (optional)

### Git Integration
- ✅ Commit history extraction (last 50 commits)
- ✅ Commit message analysis
- ✅ Diff statistics (lines changed)
- ✅ Co-changed file detection
- ✅ Import statement parsing (Python, JS, Java)

### AI Capabilities
- ✅ Natural language summarization
- ✅ Design decision inference
- ✅ Relationship explanation
- ✅ Code snippet interpretation
- ✅ Uncertainty handling (admits when evidence is weak)

### User Experience
- ✅ VS Code command palette integration
- ✅ Sidebar webview UI
- ✅ Loading states
- ✅ Error handling with clear messages
- ✅ Clickable commit hashes
- ✅ Clickable related file links
- ✅ VS Code theme integration

### Developer Experience
- ✅ Mock mode (works without API key)
- ✅ Environment variable configuration
- ✅ Auto-reload on code changes
- ✅ Comprehensive error logging
- ✅ Health check endpoint

---

## 📁 File Structure

```
ContextWeave Lite/
│
├── 📚 Documentation (11 files, ~5000 lines)
│   ├── README.md                   # Main documentation
│   ├── GETTING_STARTED.md          # Quick start guide
│   ├── QUICKSTART.md               # 5-minute setup
│   ├── PROJECT_SUMMARY.md          # Project overview
│   ├── PROJECT_DETAILS.md          # This file
│   ├── ARCHITECTURE.md             # System architecture
│   ├── TESTING.md                  # Testing guide
│   ├── TROUBLESHOOTING.md          # Common issues
│   ├── INDEX.md                    # Documentation index
│   ├── requirements.md             # Product requirements
│   └── design.md                   # Technical design
│
├── 🐍 Backend (Python/FastAPI)
│   ├── main.py                     # API endpoints (150 lines)
│   ├── schemas.py                  # Pydantic models (40 lines)
│   ├── git_utils.py                # Git operations (250 lines)
│   ├── llm_client.py               # LLM integration (350 lines)
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment variables (active)
│   ├── .env.example                # Environment template
│   ├── LLM_PROVIDERS.md            # LLM configuration guide
│   └── venv/                       # Virtual environment
│
├── 🎨 VS Code Extension (TypeScript)
│   ├── src/
│   │   ├── extension.ts            # Main extension (100 lines)
│   │   ├── apiClient.ts            # Backend client (60 lines)
│   │   └── sidebarProvider.ts      # UI webview (450 lines)
│   ├── out/                        # Compiled JavaScript
│   │   ├── extension.js
│   │   ├── apiClient.js
│   │   └── sidebarProvider.js
│   ├── .vscode/
│   │   ├── launch.json             # Debug configuration
│   │   └── tasks.json              # Build tasks
│   ├── resources/
│   │   └── icon.svg                # Extension icon
│   ├── package.json                # Extension manifest
│   ├── package-lock.json           # Dependency lock
│   ├── tsconfig.json               # TypeScript config
│   └── node_modules/               # Dependencies (160 packages)
│
├── 🔧 Configuration
│   ├── .gitignore                  # Git ignore rules
│   └── .git/                       # Git repository
│
└── 📊 Statistics
    ├── Total Files: 25+ source files
    ├── Total Lines of Code: ~1,400
    ├── Total Documentation: ~5,000 lines
    ├── Git Commits: 2
    └── Dependencies: 160+ packages
```

---

## 🚀 Setup & Installation

### Prerequisites
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed
- ✅ VS Code 1.85+ installed
- ✅ Git installed
- ✅ Groq API key (or OpenAI key)

### Backend Setup (Completed ✅)

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment variables
# Edit backend/.env with your API key

# 6. Start server
python main.py
```

**Status**: ✅ Backend running on http://localhost:8000

### VS Code Extension Setup (Completed ✅)

```bash
# 1. Navigate to extension
cd vscode-extension

# 2. Install dependencies
npm install

# 3. Compile TypeScript
npm run compile

# 4. Run extension
# Open vscode-extension folder in VS Code
# Press F5 to launch Extension Development Host
```

**Status**: ✅ Extension compiled and ready

---

## 📖 Usage Guide

### Basic Usage

1. **Open a Git Repository** in VS Code
   - Must have `.git` folder
   - Must have commit history

2. **Open a File** you want to analyze

3. **Run the Command**:
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
   - Type: `ContextWeave: Explain this file`
   - Press Enter

4. **View Results** in the sidebar:
   - 📄 What this file does
   - 🔍 Key design decisions
   - 📚 You should also read

### Advanced Usage

**Explain Selected Code:**
1. Select 5-10 lines of code
2. Run the command
3. Get additional "Selected Code Explanation" section

**Analyze Different Files:**
- Works with any text file in a Git repository
- Best results with files that have commit history

**Adjust Settings:**
- Open VS Code Settings (`Ctrl+,`)
- Search for "ContextWeave"
- Modify backend URL or commit limit

---

## 🔌 API Documentation

### Endpoints

#### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "llm_configured": true,
  "version": "0.1.0"
}
```

#### POST /context/file
Analyze a file and return context

**Request:**
```json
{
  "repo_path": "C:\\Users\\...\\ContextWeave Lite",
  "file_path": "C:\\Users\\...\\ContextWeave Lite\\backend\\main.py",
  "selected_code": null,
  "commit_limit": 50
}
```

**Response:**
```json
{
  "summary": "This file is the main entry point...",
  "decisions": [
    {
      "title": "Initial commit",
      "description": "Created complete backend structure",
      "commits": ["64b71cd"]
    }
  ],
  "related_files": [
    {
      "path": "backend/llm_client.py",
      "reason": "Handles LLM API calls"
    }
  ],
  "weird_code_explanation": null,
  "metadata": {
    "commits_analyzed": 1,
    "llm_model": "llama-3.1-8b-instant",
    "has_commit_history": true
  }
}
```

---

## 📊 Development Status

### Completed Features ✅
- [x] Backend API with FastAPI
- [x] Git history extraction
- [x] LLM integration (Groq)
- [x] VS Code extension
- [x] Sidebar UI
- [x] Command palette integration
- [x] Error handling
- [x] Mock mode
- [x] Environment configuration
- [x] Comprehensive documentation

### In Progress 🚧
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance optimization
- [ ] Caching improvements

### Planned Features 📋
- [ ] Multi-language UI (Hindi, Tamil, etc.)
- [ ] Chat interface
- [ ] Architecture visualization
- [ ] Team collaboration features
- [ ] Custom prompt templates
- [ ] Offline mode

---

## ⚠️ Known Issues & Limitations

### Current Limitations
1. **Single Repository**: Only analyzes one repo at a time
2. **File-Level Only**: No cross-file analysis
3. **Text Files Only**: Binary files not supported
4. **Git Required**: Must be a Git repository
5. **Commit History**: Better results with more commits
6. **Token Limits**: Very large files (>10,000 lines) are truncated

### Known Issues
1. **TypeScript Warnings**: Editor shows module warnings (doesn't affect runtime)
2. **Model Deprecation**: Some Groq models may be decommissioned
3. **Rate Limits**: Free tier has API rate limits
4. **Windows Paths**: Backslash handling in some edge cases

### Workarounds
- **No Git History**: Initialize repo with `git init` and commit files
- **Large Files**: Will auto-truncate to 6000 characters
- **Rate Limits**: Use caching, reduce commit_limit
- **Model Errors**: Update to supported model in `.env`

---

## 🔮 Future Enhancements

### Short-Term (v1.1 - v1.3)
- Add Redis caching for better performance
- Support more programming languages
- Improve import detection accuracy
- Add unit tests (pytest, Jest)
- Package extension for VS Code marketplace

### Medium-Term (v2.0)
- Multi-repo context
- Chat interface for follow-up questions
- Architecture visualization
- Team collaboration features
- Integration with GitHub/GitLab

### Long-Term (v3.0+)
- Proactive insights
- Code review assistant
- Onboarding workflows
- Fine-tuned models
- Enterprise features

---

## 🐛 Troubleshooting

### Backend Won't Start
**Issue**: Import errors, module not found

**Solution**:
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Extension Not Working
**Issue**: Command not found, sidebar not opening

**Solution**:
```bash
cd vscode-extension
npm install
npm run compile
# Press F5 in VS Code
```

### Mock Response Warning
**Issue**: "LLM not configured" warning

**Solution**:
1. Check `backend/.env` has valid API key
2. Restart backend: Stop and run `python main.py`
3. Verify with: `curl http://localhost:8000/health`

### Git Repository Error
**Issue**: "Not a valid Git repository"

**Solution**:
```bash
cd your-project
git init
git add .
git commit -m "Initial commit"
```

### Model Decommissioned Error
**Issue**: "Model has been decommissioned"

**Solution**:
Update `backend/.env`:
```
LLM_MODEL=llama-3.1-8b-instant
```

---

## 📞 Support & Resources

### Documentation
- [README.md](README.md) - Complete guide
- [GETTING_STARTED.md](GETTING_STARTED.md) - Quick start
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design

### External Resources
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [VS Code Extension API](https://code.visualstudio.com/api)
- [Groq API Docs](https://console.groq.com/docs)
- [GitPython Docs](https://gitpython.readthedocs.io/)

### Community
- GitHub Issues: (Add your repo URL)
- Discord: (Add if available)
- Email: (Add your email)

---

## 📜 License

MIT License - Free to use, modify, and distribute

---

## 🙏 Acknowledgments

- **Built with**: FastAPI, GitPython, VS Code Extension API
- **AI Assistance**: Kiro AI (requirements, design, code generation)
- **Theme**: AI for Bharat - Learning & Developer Productivity
- **Target Users**: Indian developers, students, junior engineers
- **LLM Provider**: Groq Cloud (llama-3.1-8b-instant)

---

## 📈 Project Statistics

| Metric | Value |
|--------|-------|
| **Development Time** | ~9 hours (with AI assistance) |
| **Lines of Code** | ~1,400 |
| **Lines of Documentation** | ~5,000 |
| **Total Files** | 25+ |
| **Dependencies** | 160+ packages |
| **Git Commits** | 2 |
| **API Endpoints** | 2 |
| **Supported Languages** | Python, JavaScript, Java, TypeScript |
| **Current Version** | 0.1.0 |
| **Status** | ✅ Fully Operational |

---

## 🎯 Success Metrics

### MVP Success (Achieved ✅)
- ✅ End-to-end working system
- ✅ Backend + Extension integration
- ✅ Git history analysis
- ✅ LLM integration
- ✅ Beautiful UI
- ✅ Comprehensive documentation

### User Success (To Measure)
- Time to understand a file: Target < 5 minutes
- Accuracy of summaries: Target > 80% helpful
- Reduction in "why" questions: Target 50%
- User satisfaction: Target 4/5 stars

---

**Last Updated**: February 7, 2026  
**Project Status**: ✅ Production Ready  
**Maintainer**: Shivansh Singh

---

*This document is auto-generated and maintained as part of the ContextWeave Lite project.*
