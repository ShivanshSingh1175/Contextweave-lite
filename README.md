# ContextWeave Lite

**AI-powered code context assistant for VS Code**

[![AI for Bharat](https://img.shields.io/badge/AI%20for%20Bharat-Learning%20%26%20Productivity-orange)](https://github.com/yourusername/contextweave-lite)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/typescript-5.3+-blue.svg)](https://www.typescriptlang.org/)

> Helping Indian students and junior developers understand large, poorly documented codebases 5-10x faster.

---

## 🎯 The Problem

**Target Users:** Students from Tier-2/Tier-3 colleges, new graduates at Indian companies (BFSI, govtech, startups), and junior developers maintaining legacy systems.

**The Pain:**
- 📚 Legacy codebases have no documentation
- 🔒 Knowledge locked in 1-2 senior developers' heads
- 📝 Git history is noisy ("fix", "update", "wip")
- ⏱️ New developers take 4-6 weeks to become productive

**Real Impact:** A new grad spends 3 days understanding one file. A student gives up on open-source. A junior dev breaks production because they didn't understand "weird" code.

---

## ✨ The Solution

ContextWeave Lite analyzes any file in a Git repository and provides:

1. **📄 Summary** - What the file does (2-3 sentences)
2. **🔍 Design Decisions** - Key choices from Git history (with commit evidence)
3. **📚 Related Files** - What to read next (imports + co-changes)
4. **🤔 Code Explanation** - Why "weird" code exists (optional)

**Architecture:** VS Code extension (TypeScript) + FastAPI backend (Python) + LLM API (Groq)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+, Node.js 18+, VS Code 1.85+
- Git repository to analyze
- Groq API key (free at [console.groq.com](https://console.groq.com))

### 1. Start Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add: LLM_API_KEY=your-groq-key-here

python main.py
```

Backend runs on `http://localhost:8000`

### 2. Install Extension

```bash
cd vscode-extension
npm install
npm run compile
```

Press **F5** in VS Code to launch Extension Development Host

### 3. Use It!

1. Open a Git repository in VS Code
2. Open any file
3. Press `Ctrl+Shift+P` → "ContextWeave: Explain this file"
4. View results in sidebar!

---

## 🤖 Why AI is Needed (Not Just Rules)

**Deterministic Layer (Rules):**
- ✅ Extract commit history from Git
- ✅ Parse import statements
- ✅ Find co-changed files
- ✅ Collect structured data

**AI Layer (LLM):**
- 🧠 Interpret natural language commit messages
- 🧠 Synthesize patterns across multiple commits
- 🧠 Infer design intent and tradeoffs
- 🧠 Generate human-readable explanations

**Example:** Rules see "async refactor" + "update callers" + "remove sync code" as 3 separate commits. AI synthesizes: *"Migrated from synchronous to asynchronous processing to improve API response time and handle concurrent requests."*

**Without AI:** Just a commit browser. **With AI:** Reasoning and learning acceleration.

---

## 🛡️ Responsible AI

- **Transparency:** All AI output labeled "✨ AI-generated"
- **Source Attribution:** Every decision cites commit hashes (clickable)
- **Uncertainty:** Admits when history is sparse ("Limited commit context available")
- **Privacy:** API keys loaded from `.env`, never hardcoded
- **Warning:** Users notified when sending code to cloud APIs

---

## 🇮🇳 Impact for Bharat

**AI for Learning & Developer Productivity Track**

ContextWeave Lite addresses a critical challenge for Indian developers: massive, undocumented codebases with knowledge concentrated in a few senior engineers.

**Impact:**
- **Students:** Learn from real-world projects 5-10x faster, contribute to open-source confidently
- **New Grads:** Reduce onboarding time from 6 weeks to 3 weeks at Indian companies
- **Junior Devs:** Reduce "why" questions to seniors by 50%, gain confidence to maintain legacy code
- **Teams:** Democratize knowledge, reduce dependency on overloaded senior developers

This directly supports the "AI for Learning & Developer Productivity" theme by using AI to accelerate learning and reduce productivity bottlenecks in Indian tech teams.

---

## 📖 Documentation

- **[requirements.md](requirements.md)** - Product requirements and user stories
- **[design.md](design.md)** - Technical architecture and design decisions
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Deep dive into system components
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Executive summary for judges

---

## 🏗️ Architecture

```
VS Code Extension (TypeScript)
    ↓ HTTP POST /context/file
FastAPI Backend (Python)
    ↓ GitPython (deterministic)
    ↓ LLM API (AI reasoning)
Groq llama-3.1-8b-instant
```

**Separation of Concerns:**
- **Git Layer:** Deterministic data extraction (no AI)
- **LLM Layer:** AI-powered interpretation and reasoning
- **Extension:** User interface and experience

---

## 🔧 Configuration

**Backend (`.env`):**
```bash
LLM_API_KEY=your-groq-api-key
LLM_API_BASE=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-8b-instant
```

**VS Code Settings:**
- `contextweave.backendUrl` - Backend URL (default: `http://localhost:8000`)
- `contextweave.commitLimit` - Max commits to analyze (default: 50)

---

## 🐛 Troubleshooting

**"Backend not reachable"**
- Ensure backend is running: `curl http://localhost:8000/health`
- Check `contextweave.backendUrl` in VS Code settings

**"Not a valid Git repository"**
- File must be in a Git repository with commit history
- Run `git init && git add . && git commit -m "Initial commit"`

**"Mock Response: LLM not configured"**
- Set `LLM_API_KEY` in `backend/.env`
- Restart backend: `python main.py`

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more.

---

## 🚧 Limitations (MVP)

- Single repository at a time
- File-level analysis only (no cross-file architecture)
- Requires online LLM (or mock mode)
- Text files only (no binaries)

---

## 🔮 Future Enhancements

- Multi-language UI (Hindi, Tamil, Telugu)
- Chat interface for follow-up questions
- Architecture visualization
- Team collaboration features

---

## 📜 License

MIT License - Free to use, modify, and distribute

---

## 🙏 Acknowledgments

- **Track:** AI for Bharat – AI for Learning & Developer Productivity
- **Built with:** FastAPI, GitPython, VS Code Extension API, Groq
- **AI Assistance:** Kiro (requirements, design, documentation)

---

**Made with ❤️ for Indian developers learning and building**
