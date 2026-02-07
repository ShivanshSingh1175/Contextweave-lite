# ContextWeave Lite - Architecture Documentation

Technical architecture and design decisions for ContextWeave Lite.

---

## System Overview

ContextWeave Lite is a three-tier system:

1. **VS Code Extension (Frontend)** - TypeScript, user interface
2. **FastAPI Backend (API Layer)** - Python, orchestration and business logic
3. **External LLM API (AI Layer)** - Groq/OpenAI, natural language processing

```
┌─────────────────────────────────────────────────────────────┐
│                     VS Code IDE                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ContextWeave Extension (TypeScript)                 │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│  │  │ Command    │  │ API Client   │  │  Sidebar   │  │  │
│  │  │ Handler    │─▶│ (HTTP)       │  │  Webview   │  │  │
│  │  └────────────┘  └──────┬───────┘  └────────────┘  │  │
│  └─────────────────────────┼──────────────────────────┘  │
└────────────────────────────┼─────────────────────────────┘
                             │
                             │ HTTP POST /context/file
                             │ JSON Request/Response
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python 3.11)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Layer (main.py)                                 │  │
│  │  - Request validation                                │  │
│  │  - Orchestration                                     │  │
│  │  - Response formatting                               │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  Git Analysis Layer (git_utils.py)                   │  │
│  │  DETERMINISTIC - No AI                               │  │
│  │  - Extract commit history                            │  │
│  │  - Parse imports                                     │  │
│  │  - Find co-changed files                            │  │
│  │  - Read file content                                │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  LLM Integration Layer (llm_client.py)               │  │
│  │  AI-POWERED - Reasoning & NLG                        │  │
│  │  - Build structured prompts                          │  │
│  │  - Call LLM API                                      │  │
│  │  - Parse JSON responses                              │  │
│  │  - Handle errors & fallbacks                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                     │
                     │ HTTPS API Call
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              LLM API Provider                               │
│         (Groq / OpenAI / AWS Bedrock)                       │
│         Model: llama-3.1-8b-instant                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. VS Code Extension (Frontend)

**Technology:** TypeScript, VS Code Extension API

**Files:**
- `vscode-extension/src/extension.ts` - Entry point, command registration
- `vscode-extension/src/apiClient.ts` - HTTP client for backend
- `vscode-extension/src/sidebarProvider.ts` - Webview UI provider

**Responsibilities:**
- Register commands and UI elements
- Detect workspace and file paths
- Call backend API
- Render results in sidebar webview
- Handle user interactions (click file links)

**Key Design Decisions:**
- **Sidebar webview** instead of editor decorations for better readability
- **Synchronous command execution** to ensure sidebar is visible before API call
- **Configurable backend URL** to support remote deployments
- **Error handling with suggestions** to guide users through common issues

---

### 2. FastAPI Backend (API Layer)

**Technology:** Python 3.11, FastAPI, Pydantic

**Files:**
- `backend/main.py` - API endpoints and orchestration
- `backend/schemas.py` - Pydantic models for request/response
- `backend/git_utils.py` - Git analysis (deterministic)
- `backend/llm_client.py` - LLM integration (AI-powered)

**Responsibilities:**
- Expose HTTP API endpoints
- Validate inputs with Pydantic
- Orchestrate Git analysis and LLM calls
- Format responses
- Handle errors and logging

**Key Design Decisions:**
- **FastAPI** for automatic OpenAPI docs and async support
- **Pydantic** for type-safe request/response validation
- **CORS enabled** to allow VS Code extension to call API
- **Environment variables** for configuration (never hardcode secrets)
- **Structured logging** for debugging and monitoring

---

### 3. Git Analysis Layer (Deterministic)

**Technology:** GitPython

**File:** `backend/git_utils.py`

**Responsibilities:**
- Extract commit history for a file
- Parse import statements (Python, JS/TS, Java)
- Find co-changed files (files that change together)
- Read file content from disk

**Key Design Decisions:**
- **Pure data extraction** - no interpretation or AI
- **Language-aware import parsing** using regex patterns
- **Co-change analysis** based on commit frequency
- **Truncation for large files** to avoid memory issues
- **Graceful error handling** for edge cases (no commits, binary files)

**Why Separate from AI Layer:**
- Fast and reliable (no API calls)
- Testable with mock Git repos
- Can be used independently
- Provides structured data for LLM

---

### 4. LLM Integration Layer (AI-Powered)

**Technology:** httpx (async HTTP client), OpenAI-compatible API

**File:** `backend/llm_client.py`

**Responsibilities:**
- Construct structured prompts
- Call external LLM API
- Parse JSON responses
- Handle errors and fallbacks
- Provide mock mode when LLM unavailable

**Key Design Decisions:**
- **OpenAI-compatible API** for easy model swapping
- **Structured prompts** with clear instructions and examples
- **Low temperature (0.3)** for consistency
- **JSON output format** for structured parsing
- **Fallback to mock mode** on errors (never crash)
- **Source grounding** - all evidence provided in prompt

**Prompt Engineering Strategy:**
- Clear role definition: "You are helping a junior developer..."
- Explicit tasks: numbered list of what to do
- Output format: "JSON only, no markdown"
- Uncertainty handling: "Admit when evidence is weak"
- Audience adaptation: "Use simple language"

---

## Data Flow

### End-to-End Flow: "Explain this file"

**Step 1: User Action**
- User opens a file in VS Code
- User runs command: "ContextWeave: Explain this file"

**Step 2: Extension (extension.ts)**
```typescript
1. Get active editor and file path
2. Detect workspace folder (repo root)
3. Get selected code (if any)
4. Show sidebar and loading state
5. Call backend API via apiClient.analyzeFile()
```

**Step 3: API Client (apiClient.ts)**
```typescript
1. Read configuration (backendUrl, commitLimit)
2. Construct request body:
   {
     repo_path: "/path/to/repo",
     file_path: "/path/to/file.py",
     selected_code: "optional code snippet",
     commit_limit: 50
   }
3. POST to http://localhost:8000/context/file
4. Return AnalysisResult or throw error
```

**Step 4: Backend API (main.py)**
```python
1. Validate inputs (repo exists, file exists)
2. Call get_commit_history() → List[Dict]
3. Call read_file_content() → str
4. Call get_related_files() → Dict
5. Call analyze_file_with_llm() → ContextResponse
6. Return JSON response
```

**Step 5: Git Analysis (git_utils.py)**
```python
1. get_commit_history():
   - Use GitPython to query commits
   - Extract hash, author, date, message, lines_changed
   - Return list of commit dicts

2. get_related_files():
   - extract_imports(): Parse import statements
   - find_co_changed_files(): Analyze commit co-occurrence
   - Return dict with 'imports' and 'co_changed' lists
```

**Step 6: LLM Integration (llm_client.py)**
```python
1. build_analysis_prompt():
   - Include file content (truncated if needed)
   - Include last 20 commits
   - Include related files data
   - Include selected code (if provided)
   - Return structured prompt string

2. call_llm():
   - POST to LLM API with prompt
   - Parse JSON from response
   - Return dict

3. parse_llm_response():
   - Extract summary, decisions, related_files
   - Create ContextResponse with Pydantic
   - Add metadata
   - Return ContextResponse
```

**Step 7: Sidebar Display (sidebarProvider.ts)**
```typescript
1. Receive AnalysisResult from API
2. Generate HTML with sections:
   - Summary
   - Design decisions (with commit badges)
   - Related files (with clickable links)
   - Selected code explanation (if applicable)
3. Render in webview
4. Handle user interactions (click file links)
```

---

## Design Patterns

### 1. Layered Architecture

**Pattern:** Separation of concerns into distinct layers

**Layers:**
1. **Presentation Layer** (VS Code Extension) - UI and user interaction
2. **API Layer** (FastAPI) - HTTP endpoints and orchestration
3. **Business Logic Layer** (Git Analysis + LLM) - Core functionality
4. **Data Layer** (Git Repository) - Data source

**Benefits:**
- Clear separation of concerns
- Easy to test each layer independently
- Can swap implementations (e.g., different LLM providers)

---

### 2. Deterministic vs AI Separation

**Pattern:** Separate deterministic logic from AI-powered logic

**Deterministic Layer (git_utils.py):**
- Fast, reliable, testable
- No API calls or external dependencies
- Provides structured data

**AI Layer (llm_client.py):**
- Interprets and reasons
- Generates human-readable text
- Handles uncertainty

**Benefits:**
- System works even if LLM fails (mock mode)
- Can test deterministic logic without LLM
- Clear understanding of what requires AI

---

### 3. Fallback Strategy

**Pattern:** Graceful degradation when dependencies fail

**Implementation:**
- LLM API unavailable → Mock mode (deterministic responses)
- Git history empty → Show "No commits found"
- File too large → Truncate with note
- Network timeout → Show clear error message

**Benefits:**
- System never crashes
- Users always get some value
- Clear error messages guide users

---

### 4. Configuration via Environment Variables

**Pattern:** Externalize configuration

**Implementation:**
- Backend loads `.env` file with `python-dotenv`
- VS Code extension reads workspace settings
- No hardcoded secrets or URLs

**Benefits:**
- Easy to configure for different environments
- Secrets never committed to Git
- Can swap LLM providers without code changes

---

## Technology Choices

### Why FastAPI?

**Alternatives:** Flask, Django, Express.js

**Reasons:**
- Automatic OpenAPI documentation
- Built-in async support (for LLM API calls)
- Pydantic integration for type safety
- Fast and modern
- Easy to deploy

---

### Why GitPython?

**Alternatives:** subprocess + git CLI, libgit2

**Reasons:**
- Pure Python (no external dependencies)
- High-level API (easy to use)
- Well-maintained and documented
- Handles edge cases gracefully

---

### Why Groq?

**Alternatives:** OpenAI, AWS Bedrock, Anthropic Claude

**Reasons:**
- Fast inference (< 2 seconds)
- Free tier with generous limits
- OpenAI-compatible API (easy to swap)
- Good code understanding
- No credit card required for testing

---

### Why VS Code Extension?

**Alternatives:** CLI tool, web app, IDE plugin

**Reasons:**
- Developers already use VS Code
- Native integration with workspace and Git
- Rich UI capabilities (webviews)
- Easy to distribute (VS Code Marketplace)
- Access to file system and Git

---

## Security Considerations

### 1. API Key Management

**Risk:** API keys leaked in Git

**Mitigation:**
- Store keys in `.env` file
- Add `.env` to `.gitignore`
- Provide `.env.example` template
- Never log API keys
- Health endpoint shows `llm_configured: true/false` but never exposes key

---

### 2. Code Privacy

**Risk:** Proprietary code sent to external LLM

**Mitigation:**
- User provides their own API key (not shared)
- Code sent only for analysis (not training)
- No long-term storage of code
- Documentation warns about sending proprietary code
- Future: Support self-hosted LLMs

---

### 3. Input Validation

**Risk:** Malicious inputs crash backend

**Mitigation:**
- Pydantic validates all inputs
- Check file paths exist before reading
- Validate Git repository before querying
- Truncate large files to prevent memory issues
- Timeout on LLM API calls (30 seconds)

---

### 4. CORS Configuration

**Risk:** Unauthorized access to backend

**Mitigation:**
- CORS allows all origins (for MVP)
- Future: Restrict to specific origins
- No authentication required (local deployment)
- Future: Add API key authentication for remote deployments

---

## Performance Considerations

### 1. Latency Optimization

**Target:** < 15 seconds end-to-end

**Optimizations:**
- Truncate large files to 6000 chars
- Limit commits to 50 by default
- Use fast LLM model (llama-3.1-8b-instant)
- Async API calls (FastAPI + httpx)
- Show loading indicator immediately

**Measured Latency:**
- Git analysis: 0.5-2 seconds
- LLM API call: 2-5 seconds
- Network round-trip: 0.1-0.5 seconds
- UI rendering: < 0.1 seconds
- **Total:** 3-8 seconds (well under target)

---

### 2. Memory Management

**Risk:** Large files or repos cause memory issues

**Mitigation:**
- Truncate files > 10,000 lines
- Limit commits to 100 max
- Stream file reading (not load entire file)
- No caching (for MVP)

---

### 3. API Rate Limits

**Risk:** Exceed LLM API rate limits

**Mitigation:**
- Use free tier with generous limits (Groq: 30 requests/minute)
- Show clear error message on rate limit
- Future: Implement request queuing
- Future: Cache results for 5 minutes

---

## Scalability Considerations

### Current Architecture (MVP)

**Deployment:** Local development (localhost:8000)

**Limitations:**
- Single user
- No caching
- No load balancing
- No monitoring

**Suitable for:** Hackathon demo, personal use, small teams

---

### Future Architecture (Production)

**Deployment:** Cloud-based (AWS/Azure/GCP)

**Enhancements:**
- Load balancer for multiple backend instances
- Redis cache for repeated queries
- Database for user preferences and history
- Monitoring and logging (CloudWatch, Datadog)
- Authentication and authorization
- Rate limiting per user

**Suitable for:** Enterprise teams, public service

---

## Testing Strategy

### Unit Tests

**Backend:**
- `test_git_utils.py` - Test Git analysis functions with mock repos
- `test_llm_client.py` - Test prompt construction and response parsing
- `test_main.py` - Test API endpoints with mock dependencies

**Extension:**
- `test_apiClient.ts` - Test HTTP client with mock backend
- `test_sidebarProvider.ts` - Test HTML generation

---

### Integration Tests

**Backend:**
- Test full API flow with real Git repo and mock LLM
- Test error handling (invalid inputs, Git errors, LLM errors)

**Extension:**
- Test command execution with mock backend
- Test sidebar rendering with sample data

---

### End-to-End Tests

**Manual Testing:**
- Test with real repositories (open-source projects)
- Test edge cases (empty files, no commits, binary files)
- Test error scenarios (backend down, invalid API key)
- Test UI/UX (readability, clickability, responsiveness)

---

## Deployment Options

### Option 1: Local Development (Current)

**Setup:**
```bash
# Backend
cd backend
python main.py

# Extension
cd vscode-extension
npm run compile
# Press F5 in VS Code
```

**Pros:** Simple, no infrastructure needed  
**Cons:** Single user, no remote access

---

### Option 2: Team Deployment (Future)

**Setup:**
- Deploy backend to AWS EC2 or Lightsail
- Configure VS Code extension to use remote backend URL
- Share backend URL with team

**Pros:** Multiple users, centralized backend  
**Cons:** Requires server management, costs money

---

### Option 3: Enterprise Deployment (Future)

**Setup:**
- Deploy backend to Kubernetes cluster
- Use AWS Bedrock for LLM (data residency)
- Add authentication and authorization
- Set up monitoring and logging

**Pros:** Scalable, secure, enterprise-ready  
**Cons:** Complex setup, higher costs

---

## Future Enhancements

### Phase 2: Enhanced Analysis
- Multi-file analysis (module-level, feature-level)
- Architectural diagram generation
- Code quality insights (complexity, duplication)
- Test coverage analysis

### Phase 3: Collaboration
- Shared annotations and notes
- Team knowledge base
- Onboarding checklists
- Learning paths

### Phase 4: Enterprise Features
- Self-hosted LLM option
- Fine-tuned models for specific codebases
- Integration with Jira/Linear
- Analytics and insights

### Phase 5: India-Specific Features
- Multi-language UI (Hindi, Tamil, Telugu)
- Integration with Indian code schools (Masai, Scaler)
- Optimized for Indian internet speeds
- Support for Indian cloud providers

---

**Document Version:** 1.0  
**Last Updated:** February 7, 2026  
**Status:** Complete
