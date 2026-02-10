# ContextWeave Lite - System Design Document

**Version:** 1.0  
**Date:** February 2026  
**Track:** AI for Bharat - AI for Learning & Developer Productivity  
**Status:** Production Ready

---

## High-Level Architecture

### System Overview

ContextWeave Lite is a three-tier system consisting of a VS Code extension frontend, a FastAPI backend, and an external LLM service. The architecture separates deterministic data collection from AI-powered reasoning to ensure transparency, testability, and graceful degradation.

**Core Components:**
- VS Code Extension (TypeScript) - User interface and command handling
- FastAPI Backend (Python) - API orchestration and business logic
- Git Analysis Layer (Python) - Deterministic data extraction
- LLM Integration Layer (Python) - AI-powered interpretation
- External LLM Service (Groq) - Natural language processing

**Design Principles:**
- Separation of concerns (deterministic vs AI layers)
- API-first architecture (stateless, scalable)
- Graceful degradation (works without Git or LLM)
- Zero-configuration user experience

---

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        VS Code IDE                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         ContextWeave Extension (TypeScript)              │  │
│  │                                                          │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │   Command    │  │  API Client  │  │   Sidebar    │  │  │
│  │  │   Handler    │─▶│   (Axios)    │  │   Webview    │  │  │
│  │  └──────────────┘  └──────┬───────┘  └──────────────┘  │  │
│  │                           │                              │  │
│  │  ┌──────────────────────┐│                              │  │
│  │  │  Backend Manager     ││                              │  │
│  │  │  (Auto-spawn Python) ││                              │  │
│  │  └──────────────────────┘│                              │  │
│  └────────────────────────────┼──────────────────────────────┘
└────────────────────────────────┼──────────────────────────────┘
                                 │
                                 │ HTTP POST /context/file
                                 │ JSON: {repo_path, file_path, ...}
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Python 3.11)                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Layer (main.py)                   │  │
│  │  - Request validation (Pydantic)                         │  │
│  │  - Orchestration logic                                   │  │
│  │  - Error handling                                        │  │
│  │  - Response formatting                                   │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                     │                                           │
│  ┌──────────────────▼───────────────────────────────────────┐  │
│  │          Git Analysis Layer (git_utils.py)               │  │
│  │          DETERMINISTIC - No AI Interpretation            │  │
│  │                                                          │  │
│  │  - Extract commit history (GitPython)                   │  │
│  │  - Parse import statements (Regex)                      │  │
│  │  - Analyze co-change patterns (Git log)                 │  │
│  │  - Read file content                                    │  │
│  │  - Calculate diff statistics                            │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                     │                                           │
│  ┌──────────────────▼───────────────────────────────────────┐  │
│  │        LLM Integration Layer (llm_client.py)             │  │
│  │        AI-POWERED - Reasoning & Generation               │  │
│  │                                                          │  │
│  │  - Build structured prompts                             │  │
│  │  - Token-aware truncation (tiktoken)                    │  │
│  │  - Call LLM API (instructor + OpenAI SDK)               │  │
│  │  - Parse structured responses (Pydantic)                │  │
│  │  - Handle errors & fallbacks                            │  │
│  └──────────────────┬───────────────────────────────────────┘  │
└────────────────────┼────────────────────────────────────────────┘
                     │
                     │ HTTPS POST /chat/completions
                     │ JSON: {model, messages, response_model}
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External LLM Service                         │
│                    Groq Cloud API                               │
│                    Model: llama-3.1-8b-instant                  │
│                    Context: 8,192 tokens                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. VS Code Extension (Frontend)

**Name:** ContextWeave Extension

**Responsibilities:**
- Register VS Code commands and UI elements
- Detect active file and workspace paths
- Manage backend process lifecycle
- Make HTTP requests to backend API
- Render analysis results in sidebar webview
- Handle user interactions (click file links)
- Display error messages with recovery suggestions

**Technologies:**
- TypeScript 5.3.0
- VS Code Extension API 1.85+
- Axios 1.6.2 (HTTP client)
- Node.js child_process (backend management)

**Key Files:**
- extension.ts - Main entry point, command registration
- apiClient.ts - HTTP client for backend communication
- sidebarProvider.ts - Webview UI rendering
- backendManager.ts - Python backend process management

**State Management:**
- Stateless (no persistent data)
- Backend process handle stored in memory
- Sidebar webview content regenerated on each analysis

---

### 2. FastAPI Backend (API Layer)

**Name:** ContextWeave API

**Responsibilities:**
- Expose HTTP REST endpoints
- Validate incoming requests (Pydantic schemas)
- Orchestrate Git analysis and LLM calls
- Format responses according to schema
- Log operations for debugging
- Handle errors gracefully

**Technologies:**
- Python 3.11
- FastAPI 0.109.0
- Uvicorn 0.27.0 (ASGI server)
- Pydantic 2.5.3 (validation)
- python-dotenv 1.2.1 (configuration)

**Key Endpoints:**
- GET / - Health check (returns service status)
- GET /health - Detailed health (includes LLM configuration status)
- POST /context/file - Main analysis endpoint

**Configuration:**
- Environment variables loaded from .env file
- CORS enabled for VS Code extension access
- Logging configured to INFO level

---

### 3. Git Analysis Layer (Deterministic)

**Name:** Git Utils Module

**Responsibilities:**
- Extract commit history for specific files
- Parse import statements (Python, JavaScript, Java)
- Identify co-changed files (temporal analysis)
- Read file content from disk
- Calculate diff statistics

**Technologies:**
- GitPython 3.1.41
- Python regex (import parsing)
- Python os/pathlib (file operations)

**Key Functions:**
- get_commit_history() - Extract last N commits for file
- extract_imports() - Parse import statements by language
- find_co_changed_files() - Analyze commit co-occurrence
- get_related_files() - Combine imports and co-changes
- read_file_content() - Read file with truncation

**Design Rationale:**
Pure data extraction with no interpretation ensures:
- Fast, predictable performance
- Easy to test with mock Git repositories
- Can be used independently of LLM
- Provides structured data for AI layer

---

### 4. LLM Integration Layer (AI-Powered)

**Name:** LLM Client Module

**Responsibilities:**
- Build structured prompts from Git data
- Truncate content based on token limits
- Call external LLM API with retry logic
- Parse and validate JSON responses
- Provide mock responses when LLM unavailable

**Technologies:**
- OpenAI SDK 1.12.0
- Instructor 0.5.2 (structured output)
- Tiktoken 0.5.2 (token counting)
- httpx 0.26.0 (async HTTP)

**Key Functions:**
- analyze_file_with_llm() - Main entry point
- build_messages() - Construct chat messages
- truncate_content_tokens() - Token-aware truncation
- create_mock_response() - Fallback when LLM unavailable

**Prompt Engineering:**
- System prompt defines role and output format
- User prompt includes file content, commits, related files
- Explicit instructions for JSON structure
- Emphasis on simple language for junior developers
- Request for uncertainty acknowledgment

---

## Data Flow

### End-to-End Flow: File Analysis

**Step 1: User Initiates Analysis**
```
User Action: Right-click file → "ContextWeave: Explain this file"
Extension: Detect file path, workspace path, selected code
Extension: Show loading state in sidebar
```

**Step 2: Extension Calls Backend**
```
HTTP POST http://localhost:8000/context/file
Headers: Content-Type: application/json
Body: {
  "repo_path": "C:\\Users\\...\\project",
  "file_path": "C:\\Users\\...\\project\\src\\main.py",
  "selected_code": null,
  "commit_limit": 50
}
```

**Step 3: Backend Validates Request**
```
API Layer (main.py):
- Validate file_path exists
- Validate repo_path exists (optional, graceful degradation)
- Parse request with Pydantic schema
```

**Step 4: Git Analysis (Deterministic)**
```
Git Utils (git_utils.py):
- Open Git repository with GitPython
- Query last 50 commits touching file
- Extract: hash, author, date, message, lines_changed
- Parse import statements (language-specific regex)
- Analyze co-changed files (last 100 commits)
- Read file content (max 10,000 lines)

Output: {
  commits: [{hash, author, date, message, lines_changed}, ...],
  imports: ["module1.py", "module2.py", ...],
  co_changed: [{path, frequency}, ...],
  file_content: "..."
}
```

**Step 5: LLM Integration (AI-Powered)**
```
LLM Client (llm_client.py):
- Truncate file_content to 6,000 tokens (tiktoken)
- Build structured prompt:
  * System: "You are a senior developer assistant..."
  * User: "FILE: ...\nCONTENT: ...\nCOMMITS: ...\nRELATED: ..."
- Call Groq API with instructor:
  * Model: llama-3.1-8b-instant
  * Response model: ContextResponse (Pydantic)
  * Temperature: 0.3 (low creativity)
  * Max retries: 2
- Parse JSON response into ContextResponse object

Output: ContextResponse {
  summary: "This file...",
  decisions: [{title, description, commits}, ...],
  related_files: [{path, reason}, ...],
  weird_code_explanation: "..." or null,
  metadata: {commits_analyzed, llm_model, ...}
}
```

**Step 6: Backend Returns Response**
```
HTTP 200 OK
Content-Type: application/json
Body: {
  "summary": "This file is the main entry point...",
  "decisions": [...],
  "related_files": [...],
  "weird_code_explanation": null,
  "metadata": {...}
}
```

**Step 7: Extension Renders Results**
```
Sidebar Provider (sidebarProvider.ts):
- Generate HTML with VS Code theme colors
- Section 1: "What this file does" (summary)
- Section 2: "Key design decisions" (decisions with commit badges)
- Section 3: "You should also read" (related files with links)
- Section 4: "Selected Code Explanation" (if applicable)
- Footer: Metadata (commits analyzed, model used)
- Make commit hashes and file paths clickable
```

---

## AI/ML Design

### LLM Architecture

**Model Selection:**
- Primary: Groq llama-3.1-8b-instant
- Rationale: Fast inference (< 2s), good code understanding, free tier
- Alternatives: OpenAI GPT-3.5-turbo, GPT-4, AWS Bedrock Claude

**Input Processing:**
```
Raw Inputs:
- File content (up to 10,000 lines)
- Commit history (up to 50 commits)
- Import statements (up to 10 files)
- Co-changed files (up to 10 files)
- Selected code (optional, up to 100 lines)

Token-Aware Truncation:
- Use tiktoken to count tokens accurately
- Truncate file content to 6,000 tokens max
- Preserve syntax (decode at token boundaries)
- Add truncation notice if needed

Prompt Construction:
- System prompt: Define role and output format
- User prompt: Structured sections (FILE, CONTENT, COMMITS, RELATED)
- Total prompt size: ~7,000 tokens (within 8,192 limit)
```

**Processing:**
```
LLM Tasks:
1. Semantic Understanding:
   - Analyze code structure and purpose
   - Identify main responsibilities
   - Understand design patterns

2. Natural Language Reasoning:
   - Interpret commit messages (often cryptic)
   - Infer design decisions across multiple commits
   - Synthesize patterns (e.g., "gradual refactoring")

3. Relationship Inference:
   - Understand why files are related
   - Explain conceptual connections
   - Prioritize by learning value

4. Natural Language Generation:
   - Generate clear, concise summaries
   - Adapt language for junior developers
   - Admit uncertainty when evidence is weak
```

**Output:**
```
Structured JSON (enforced by instructor):
{
  "summary": string (2-3 sentences),
  "decisions": [
    {
      "title": string (3-5 words),
      "description": string (one sentence),
      "commits": [string] (commit hashes)
    }
  ],
  "related_files": [
    {
      "path": string (relative path),
      "reason": string (one sentence)
    }
  ],
  "weird_code_explanation": string or null,
  "metadata": object
}

Validation:
- Pydantic models ensure type safety
- Instructor retries if JSON invalid
- Fallback to mock response on repeated failures
```

**Assumptions:**
- LLM has general programming knowledge
- LLM can interpret natural language commit messages
- LLM can infer intent from code structure
- LLM output may be imperfect (hence source attribution)

---

### Why AI is Essential

**Tasks Requiring AI:**

1. **Commit Message Interpretation:**
   - Input: "refactored for perf", "made it faster", "fixed blocking issue"
   - AI Task: Understand these mean similar things (performance optimization)
   - Why Not Rules: Infinite variation in natural language

2. **Design Decision Synthesis:**
   - Input: 8 commits gradually changing sync to async
   - AI Task: Synthesize into "Migrated to async for better performance"
   - Why Not Rules: Requires reasoning across multiple commits

3. **Code Semantic Understanding:**
   - Input: 200 lines of Java Spring Boot controller
   - AI Task: "This controller handles user authentication endpoints"
   - Why Not Rules: Requires understanding code semantics, not just syntax

4. **Relationship Explanation:**
   - Input: Files A and B change together 10 times
   - AI Task: "Both handle user authentication logic"
   - Why Not Rules: Requires conceptual understanding

**Deterministic vs AI Boundary:**
```
Deterministic (Rules):
✓ Extract commit history
✓ Parse import statements
✓ Count co-changes
✓ Read file content
✓ Calculate statistics

AI (LLM):
✓ Interpret commit messages
✓ Infer design decisions
✓ Explain code purpose
✓ Generate human-readable text
✓ Adapt language for audience
```

---

## Database Design

### Current Implementation

**Storage:** None (stateless system)

**Rationale:**
- MVP focuses on real-time analysis
- No user accounts or persistent data
- Each request is independent
- Simplifies deployment and scaling

**Data Flow:**
```
Request → Git Analysis → LLM Call → Response
(No database writes)
```

---

### Future Database Design

**When Needed:**
- User accounts and authentication
- Analysis result caching
- Usage analytics
- Team collaboration features

**Proposed Schema:**
```
Users:
- id (primary key)
- email
- api_key_hash
- created_at

AnalysisCache:
- id (primary key)
- file_hash (index)
- repo_hash (index)
- analysis_result (JSON)
- created_at
- expires_at

UsageMetrics:
- id (primary key)
- user_id (foreign key)
- file_analyzed
- timestamp
- latency_ms
- success (boolean)
```

---

## Scalability Considerations

### Current Architecture (MVP)

**Deployment:**
- Single-user, local deployment
- Backend runs on localhost:8000
- No load balancing or caching

**Limitations:**
- One user at a time
- No request queuing
- No result caching
- Backend restarts lose state

**Suitable For:**
- Personal use
- Hackathon demonstrations
- Small team testing (< 5 users)

---

### Scaling Strategy (Future)

**Phase 1: Multi-User (10-100 users)**
```
Architecture:
- Deploy backend to cloud (AWS EC2, Lightsail)
- Add Redis cache (5-minute TTL)
- Implement request queuing
- Add basic authentication

Bottlenecks:
- LLM API rate limits (30 req/min on free tier)
- Single backend instance

Solutions:
- Upgrade to paid LLM tier
- Implement request throttling
- Cache aggressively
```

**Phase 2: Team Scale (100-1000 users)**
```
Architecture:
- Multiple backend instances (load balancer)
- Dedicated Redis cluster
- PostgreSQL for user data
- CDN for static assets

Bottlenecks:
- LLM API costs
- Database queries

Solutions:
- Batch LLM requests
- Database read replicas
- Implement workspace indexing (reduce LLM calls)
```

**Phase 3: Enterprise Scale (1000+ users)**
```
Architecture:
- Kubernetes cluster (auto-scaling)
- Distributed caching (Redis Cluster)
- Database sharding
- Self-hosted LLM option

Bottlenecks:
- LLM inference latency
- Cross-region latency

Solutions:
- Deploy LLM inference servers (AWS SageMaker)
- Multi-region deployment
- Edge caching
```

---

## Security Considerations

### Authentication

**Current:** None (local deployment)

**Future:**
- API key authentication for remote deployments
- OAuth integration (GitHub, Google)
- Role-based access control (admin, user, viewer)

---

### Data Privacy

**Code Privacy:**
- Code sent to external LLM API (Groq)
- No long-term storage of code
- User provides own API key (not shared)
- Warning displayed about proprietary code

**Mitigation:**
- Support self-hosted LLM option (future)
- Implement on-premise deployment
- Add data residency controls

---

### API Key Security

**Current Implementation:**
- Keys stored in .env file
- .env in .gitignore (never committed)
- Keys loaded via python-dotenv
- Health endpoint shows status without exposing key

**Best Practices:**
- Never hardcode keys in source code
- Use environment variables or secret managers
- Rotate keys periodically
- Implement key expiration

---

### Input Validation

**Protection Against:**
- Directory traversal attacks (validate file paths)
- Command injection (sanitize Git operations)
- Prompt injection (sanitize user inputs before LLM)
- Denial of service (rate limiting, timeouts)

**Implementation:**
- Pydantic validation on all inputs
- Path validation (os.path.abspath, os.path.exists)
- Timeout on LLM calls (30 seconds)
- File size limits (10,000 lines)

---

## Limitations

### Technical Limitations

**Single Repository:**
- Analyzes one repository at a time
- No cross-repo context
- Cannot understand monorepo relationships

**File-Level Analysis:**
- No architectural visualization
- Cannot analyze entire modules
- Misses system-level patterns

**Git Dependency:**
- Best results require Git history
- Degrades to imports-only without Git
- No temporal intelligence without commits

**Token Limits:**
- Large files truncated to 6,000 tokens
- May miss important code in truncated sections
- Commit history limited to 50 commits

---

### Operational Limitations

**Python Dependency:**
- Requires Python 3.11+ installed
- Requires pip packages installed
- May fail if environment broken

**Internet Dependency:**
- Requires internet for LLM API
- Fails if API unavailable
- Subject to API rate limits

**Resource Usage:**
- Backend uses ~150 MB RAM
- May be heavy on low-end machines
- First-run latency 2-5 seconds

---

### AI Limitations

**LLM Accuracy:**
- May misinterpret cryptic commit messages
- May hallucinate when evidence is weak
- Quality depends on commit message quality

**Language Support:**
- Best for Python, JavaScript, Java
- Limited support for other languages
- Import parsing may miss edge cases

**Context Window:**
- Cannot analyze very large files completely
- May miss important context in truncated sections
- Limited to 8,192 tokens total

---

## Appendix

### Technology Justification

**Why FastAPI:**
- Modern, fast Python web framework
- Automatic OpenAPI documentation
- Built-in async support (for LLM calls)
- Excellent Pydantic integration

**Why GitPython:**
- Pure Python (no external dependencies)
- High-level API (easy to use)
- Well-maintained and documented
- Handles edge cases gracefully

**Why Groq:**
- Fast inference (< 2 seconds)
- Free tier with generous limits
- OpenAI-compatible API (easy to swap)
- Good code understanding

**Why Instructor:**
- Guarantees valid JSON responses
- Automatic retry on parse failures
- Type-safe with Pydantic
- Reduces error handling code

**Why Tiktoken:**
- Accurate token counting
- Model-specific tokenization
- Maximizes context utilization
- Prevents mid-syntax truncation

---

### Deployment Architecture

**Development:**
```
Developer Machine:
- VS Code with extension
- Python backend (localhost:8000)
- Git repository (local)
- Groq API (cloud)
```

**Production (Future):**
```
User Machine:
- VS Code with extension

Cloud Infrastructure:
- Load Balancer (AWS ALB)
- Backend Cluster (AWS ECS)
- Cache Layer (Redis)
- Database (PostgreSQL)
- LLM Service (Groq or AWS Bedrock)
```

---

### Performance Benchmarks

**Measured Latency (p95):**
- Git analysis: 0.5-2 seconds
- LLM API call: 2-5 seconds
- Network overhead: 0.1-0.5 seconds
- UI rendering: < 0.1 seconds
- Total: 3-8 seconds (well under 15s target)

**Resource Usage:**
- Backend RAM: ~150 MB
- Extension RAM: ~50 MB
- CPU: < 5% (idle), 20-30% (during analysis)
- Network: ~50 KB per request

---

**Document Control:**  
Version: 1.0  
Last Updated: February 2026  
Approved By: Technical Lead  
Status: Final
