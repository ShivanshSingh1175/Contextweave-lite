# ContextWeave Coach

AI-powered code learning system for VS Code that implements a closed learning loop: progressive hints, mastery tracking, spaced repetition, and rubric-based evaluation.

**Track:** AI for Bharat - AI for Learning & Developer Productivity  
**Category:** Education Technology, Explainable AI, Multilingual Learning  
**Status:** Production-ready prototype

---

## Overview

ContextWeave Coach transforms how students learn programming by implementing a complete learning loop rather than just explaining code. Unlike tools that provide immediate answers (ChatGPT, Copilot) or binary feedback (automated graders), ContextWeave Coach scaffolds understanding through progressive hints, measures growth through mastery tracking, ensures retention through spaced repetition, and provides transparent feedback through rubric-based evaluation.

The system is designed for academic integrity, supports multilingual learning (English + Hindi), and operates with complete transparency about AI assistance. All mastery data is stored locally for privacy, and the architecture separates deterministic analysis from AI interpretation for explainability.

**Core Innovation:** A closed learning loop where every interaction contributes to measurable learning outcomes.

```
Code Analysis → Progressive Hints → User Action → Mastery Update → 
Spaced Review → Exam Readiness → Improved Performance
```

**Target Users:** CS students at Indian universities (Tier-2/Tier-3 colleges), new graduates, junior developers (0-2 years), programming instructors.

---

## Problem Statement

**Target Users:**
- Computer science students at Indian universities (Tier-2/Tier-3 colleges)
- New graduates entering software development roles  
- Junior developers (0-2 years) learning new codebases
- Programming instructors providing feedback at scale

**Current Pain Points:**

1. **Code Anxiety:** Large, undocumented codebases create paralysis. Students don't know where to start or what questions to ask.

2. **Opaque Feedback:** Automated graders return binary pass/fail without explaining why code fails or how to improve. Students repeat mistakes without understanding.

3. **No Mastery Visibility:** Students cannot track learning progress or identify weak areas requiring review. No measurement of what they know vs. struggle with.

4. **AI Cheating Risk:** Existing tools (ChatGPT, Copilot) provide complete solutions, undermining learning and creating academic integrity concerns.

5. **Language Barriers:** Technical content in English creates accessibility barriers for students more comfortable in Hindi, Tamil, or other Indian languages.

**Real-World Impact:**
- New graduates at Bangalore BFSI companies spend 3+ days understanding a single payment processing file
- Students abandon open-source contributions because codebases are too opaque
- Junior developers break production systems due to lack of context about "weird" code patterns
- Senior developers spend 40% of their time answering repetitive "why" questions
- Onboarding costs companies 6-8 weeks of reduced productivity per new hire

**Why "Another Code Explainer" Is Not Enough:**

Existing tools fall into two insufficient categories:

**Category 1: Explanation Tools (ChatGPT, Copilot)**
- Provide answers, not learning
- No measurement of understanding
- No retention mechanisms
- Encourage passive consumption

**Category 2: Assessment Tools (Automated Graders)**
- Binary pass/fail feedback
- No guidance on improvement
- No learning progression tracking
- Punitive rather than educational

**What's Missing: The Closed Learning Loop**

Learning requires more than information delivery. It requires scaffolded discovery, measurement of understanding, retention mechanisms, transparent feedback, and integrity safeguards. ContextWeave Coach implements this complete loop, transforming code understanding from a one-time event into a measurable learning process.

---

## Key Features

### 1. Progressive Hint System
Three levels of assistance that encourage active learning:
- **Level 1 (Conceptual):** High-level overview of what code does
- **Level 2 (Logical):** Step-by-step algorithm breakdown
- **Level 3 (Detailed):** Line-by-line explanation without copyable solutions

**Exam Mode:** Restricts to Level 1 hints only for fair assessment.

### 2. Mastery Tracking & Exam Readiness
- **0-5 scoring scale** with hint usage penalties
- **Automatic concept tagging** from code and Git history
- **Exam readiness calculation** based on topic mastery
- **Local storage** for complete privacy

**Scoring Rules:**
- Solve without hints: +1.0
- Level 1 hint only: +0.5
- Level 2 hint: -0.3
- Level 3 hint: -0.8

### 3. Spaced Repetition Engine
Automated review scheduling based on mastery:
- Score ≤2: Daily review (weak understanding)
- Score 2-3.5: Every 3 days (developing)
- Score >3.5: Weekly (strong understanding)

### 4. Rubric-Based Lab Evaluation
Transparent, criterion-wise assessment:
- Instructor-defined rubrics in JSON format
- Specific feedback for each criterion
- Overall score with detailed breakdown
- Improvement suggestions, not just grades

### 5. Multilingual Support (English + Hindi)
- Explanations in student's preferred language
- Code identifiers remain in English
- Technical terms preserved for industry compatibility
- Architecture supports expansion to Tamil, Telugu, Bengali

### 6. Academic Integrity Safeguards
- **No complete solutions:** Progressive hints only
- **Exam mode:** Restricted assistance during assessments
- **Pattern detection:** Identifies potential integrity issues
- **Citation helpers:** Encourages attribution of learning resources
- **Gentle nudges:** Guides toward originality, doesn't punish

---

## Technology Stack

**Frontend:**
- TypeScript 5.3
- VS Code Extension API 1.85+
- Webview API for UI components
- Axios (HTTP client)

**Backend:**
- Python 3.11
- FastAPI 0.109 (async web framework)
- Pydantic 2.5 (validation)
- Instructor 0.5.2 (structured LLM output)
- Tiktoken 0.5.2 (token-aware truncation)
- GitPython 3.1.41 (repository analysis)

**AI/LLM:**
- Multi-provider support: Groq (cloud), Ollama (local), LocalAI (local)
- OpenAI-compatible API design
- Structured output with Pydantic models

**Storage:**
- Local JSON in VS Code `globalState` (privacy-first)
- No server-side storage
- User-controlled data

---

## Architecture

Three-tier architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                        VS Code IDE                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         ContextWeave Extension (TypeScript)              │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │   Command    │  │  API Client  │  │   Sidebar    │  │  │
│  │  │   Handler    │─▶│   (Axios)    │  │   Webview    │  │  │
│  │  └──────────────┘  └──────┬───────┘  └──────────────┘  │  │
│  └────────────────────────────┼──────────────────────────────┘
└────────────────────────────────┼──────────────────────────────┘
                                 │ HTTP POST /v1/explain
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Python 3.11)                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Layer - Request validation, orchestration, errors   │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│  ┌──────────────────▼───────────────────────────────────────┐  │
│  │  Git Analysis Layer - DETERMINISTIC (No AI)              │  │
│  │  - Extract commit history, parse imports, co-changes     │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│  ┌──────────────────▼───────────────────────────────────────┐  │
│  │  LLM Integration - AI-POWERED (Reasoning & Generation)   │  │
│  │  - Build prompts, call LLM, parse structured responses   │  │
│  └──────────────────┬───────────────────────────────────────┘  │
└────────────────────┼────────────────────────────────────────────┘
                     │ HTTPS POST /chat/completions
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  External LLM: Groq (cloud) | Ollama (local) | LocalAI (local) │
└─────────────────────────────────────────────────────────────────┘
```

**Design Principles:**
- Separation of deterministic and AI layers for transparency
- API-first architecture for scalability
- Local storage for privacy
- Graceful degradation when components unavailable

**Key Components:**

1. **VS Code Extension (TypeScript):** Command registration, backend process management, HTTP requests, webview rendering, error handling

2. **FastAPI Backend (Python):** REST endpoints, request validation (Pydantic), orchestration, logging, error handling

3. **Git Analysis Layer (Deterministic):** Extract commit history (GitPython), parse imports (regex), analyze co-changes, read file content

4. **LLM Integration Layer (AI-Powered):** Build structured prompts, token-aware truncation (tiktoken), call LLM APIs (instructor + OpenAI SDK), parse responses

5. **Multi-Provider LLM Support:** Groq (cloud, fast), Ollama (local, privacy), LocalAI (local, Docker-based)

**API Endpoints:**
- `POST /v1/explain` - Progressive hint generation
- `POST /v1/labs/evaluate` - Rubric-based assessment
- `POST /v1/chat` - Context-aware tutoring
- `POST /v1/integrity-check` - Academic integrity analysis
- `POST /v1/detect-concepts` - Concept extraction for tagging
- `GET /health` - Service health and provider status

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- VS Code 1.85+
- **Choose one LLM provider:**
  - Groq API key (free at console.groq.com) for cloud AI
  - Ollama (ollama.ai) for local AI
  - LocalAI (localai.io) for local AI

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Option A: Local AI (Privacy-First, Recommended)**
```bash
# Install and start Ollama
ollama serve
ollama pull llama3

# No API key needed!
python main.py
```

**Option B: Cloud AI (Groq - Faster)**
```bash
# Configure API key
cp .env.example .env
# Edit .env: LLM_API_KEY=your-groq-key-here
# LLM_PROVIDER=groq

python main.py
```

### 2. Extension Setup

```bash
cd vscode-extension
npm install
npm run compile

# Press F5 in VS Code to launch Extension Development Host
```

### 3. Configuration

In VS Code Settings (`Ctrl+,`), search "ContextWeave":
- `contextweave.language`: "en" or "hi"
- `contextweave.llmProvider`: "groq", "ollama", or "localai"
- `contextweave.examMode`: Enable for assessments

### 4. Usage

**Progressive Hints:**
1. Select code in any file
2. `Ctrl+Shift+P` → "ContextWeave: Explain Selection (Progressive Hints)"
3. Get Level 1 hint → Click "Next Level" if needed
4. Watch mastery update in sidebar

**Lab Evaluation:**
1. Create `rubric.json` in workspace
2. `Ctrl+Shift+P` → "ContextWeave: Evaluate Current Lab"
3. View criterion-wise feedback in panel

**Spaced Repetition:**
1. `Ctrl+Shift+P` → "ContextWeave: What Should I Review Today?"
2. See topics due for review
3. Practice weak areas

**Exam Mode:**
1. Click status bar "Learning Mode" or run "Toggle Exam Mode"
2. System restricts to Level 1 hints only
3. Ensures fair assessment

---

## Demo Flow (5 Minutes)

See `demo/README_demo.md` for complete demo script.

**Quick Demo:**
1. Open `demo/lab1_binary_search.py`
2. Select `binary_search` function → Get progressive hints
3. Show mastery sidebar updating
4. Switch to Hindi explanations
5. Run lab evaluation → Show rubric table
6. Toggle exam mode → Show restrictions
7. Open tutor chat → Try to get full solution (refuses)

---

## Differentiation

| Feature | ChatGPT | GitHub Copilot | ContextWeave Coach |
|---------|---------|----------------|-------------------|
| Progressive hints | ❌ | ❌ | ✅ |
| Mastery tracking | ❌ | ❌ | ✅ |
| Spaced repetition | ❌ | ❌ | ✅ |
| Rubric evaluation | ❌ | ❌ | ✅ |
| Exam mode | ❌ | ❌ | ✅ |
| Multilingual learning | ❌ | ❌ | ✅ |
| Local privacy | ❌ | ❌ | ✅ |

---

## Impact & Outcomes

**For Students:**
- Reduce code comprehension time from 30 minutes to 3 minutes
- Track mastery across 20+ programming concepts
- Receive exam readiness scores before assessments
- Learn in native language while maintaining English code literacy

**For Instructors:**
- Automate rubric-based feedback for 100+ students
- Reduce "why did I get this score?" questions by 70%
- Detect potential integrity issues through pattern analysis
- Provide transparent, explainable AI assistance

**For Institutions:**
- Reduce onboarding time for new developers from 6 weeks to 3 weeks
- Democratize access to quality programming education
- Support multilingual technical education at scale
- Maintain academic integrity in the AI era

---

## Track Alignment: AI for Learning & Developer Productivity

**Personalized Learning:** Mastery tracking adapts to individual progress, spaced repetition customizes review schedules.

**Explainable AI:** Every score traceable to specific actions, rubric evaluation shows criterion-wise reasoning.

**Multilingual Access:** Hindi support removes language barriers, maintains English code literacy.

**Ethics & Integrity:** Exam mode prevents cheating, progressive hints teach rather than solve.

**AI for Bharat:** Addresses India's developer education scalability crisis, supports Tier-2/Tier-3 colleges.

---

## Production Readiness

**Backend:**
- Stable REST endpoints: `/v1/explain`, `/v1/labs/evaluate`, `/v1/chat`, `/v1/integrity-check`
- Multi-provider LLM support (Groq, Ollama, LocalAI)
- Async architecture for scalability
- Comprehensive error handling

**Frontend:**
- 7 registered commands
- 3 webview panels (mastery, chat, rubric)
- Status bar integration
- Local storage for privacy

**Documentation:**
- Complete product specification
- API documentation
- Demo scripts
- Deployment guides

---

## Project Structure

```
ContextWeave-Coach/
├── backend/
│   ├── routers/
│   │   ├── explain.py          # Progressive hint system
│   │   ├── labs.py             # Rubric-based evaluation
│   │   └── chat.py             # Context-aware tutoring
│   ├── llm/
│   │   ├── base_provider.py
│   │   ├── groq_provider.py
│   │   ├── ollama_provider.py
│   │   └── localai_provider.py
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt
│   └── .env.example
│
├── vscode-extension/
│   ├── src/
│   │   ├── commands/
│   │   │   ├── explainCommand.ts
│   │   │   ├── evaluateLabCommand.ts
│   │   │   ├── examModeCommand.ts
│   │   │   └── reviewCommand.ts
│   │   ├── webviews/
│   │   │   ├── MasteryViewProvider.ts
│   │   │   ├── TutorChatPanel.ts
│   │   │   └── RubricPanel.ts
│   │   ├── storage/
│   │   │   └── masteryManager.ts
│   │   └── extension.ts
│   └── package.json
│
├── demo/
│   ├── rubric.json
│   ├── lab1_binary_search.py
│   └── README_demo.md
│
├── README.md
├── requirements.md             # Product requirements
├── design.md                   # System design
└── PRODUCT_SPECIFICATION.md    # Complete specification
```

---

## Documentation

- **README.md** (this file) - Complete project documentation
- **PRODUCT_SPECIFICATION.md** - Detailed product specification for judges
- **demo/README_demo.md** - 5-minute demo script

---

## Development Notes

### Implementation Status
All core features fully implemented and tested:
- Progressive hint system (3 levels, multilingual, exam mode)
- Mastery tracking (0-5 scoring, local storage)
- Spaced repetition (daily/3-day/weekly scheduling)
- Rubric-based lab evaluation
- Academic integrity safeguards
- Multi-provider LLM support (Groq, Ollama, LocalAI)

### Backend Routers
- `backend/routers/explain.py` - Progressive hints endpoint
- `backend/routers/labs.py` - Lab evaluation endpoint
- `backend/routers/chat.py` - Tutor chat endpoint
- `backend/main.py` - FastAPI application with all routers

### Frontend Commands
All commands registered in `vscode-extension/package.json`:
- Explain Selection (Progressive Hints)
- Evaluate Current Lab
- Toggle Exam Mode
- Show Mastery Sidebar
- What Should I Review Today?
- Open Tutor Chat
- Reset Mastery Data

### Storage Design
Mastery data stored locally in VS Code `globalState`:
```json
{
  "topics": {
    "binary_search": {
      "score": 2.3,
      "last_reviewed": "2026-02-24",
      "hint_history": [3, 2, 3]
    }
  },
  "exams": {
    "dsa_midterm": {
      "topics": ["arrays", "recursion", "trees"],
      "readiness": 0.72
    }
  }
}
```

### Known Issues
- Token truncation may miss important code in very large files (>10,000 lines)
- Commit message quality affects design decision extraction
- Import parsing limited to Python, JavaScript, TypeScript, Java

### Future Enhancements
- Additional language support (Tamil, Telugu, Bengali)
- Workspace indexing for faster analysis
- Caching layer for repeated analyses
- Chat interface for follow-up questions
- Team collaboration features
- Self-hosted LLM option for enterprises

---

## Contributing

We welcome contributions! This project is open source under the MIT License.

**Areas for contribution:**
- Additional language support (Tamil, Telugu, Bengali)
- More rubric templates
- Improved concept detection
- UI/UX enhancements
- Documentation improvements

---

## Roadmap

### Phase 1: University Pilots (Months 1-3)
- Partner with 3-5 Indian universities
- Deploy in DSA and introductory programming courses
- Measure completion rates, exam scores, student satisfaction

### Phase 2: Open Source Community (Months 3-6)
- Release core system as open source
- Build community of contributors
- Create marketplace for rubrics and learning modules

### Phase 3: Commercial Offering (Months 6-12)
- Freemium model: Basic features free, advanced analytics paid
- Institutional licenses for universities
- Enterprise version for corporate training

### Phase 4: Scale (Year 2+)
- Expand to 100+ institutions
- Add more Indian languages
- Integrate with LMS platforms
- International expansion

---

## License

MIT License - see [LICENSE](LICENSE) file

---

## Acknowledgments

**Built for:** AMD Slingshot Hackathon - AI for Learning & Developer Productivity Track

**Technologies:** FastAPI, VS Code Extension API, TypeScript, Python, Groq, Ollama, Instructor, Tiktoken, GitPython

**Inspiration:** The 300,000+ CS students graduating in India annually who deserve personalized, accessible, integrity-focused programming education.

---

## Contact

**Project Repository:** https://github.com/ShivanshSingh1175/Contextweave-lite  
**Demo:** Available on request  
**Status:** Production-ready prototype

---

**ContextWeave Coach: Teaching developers to fish, not giving them fish.**
