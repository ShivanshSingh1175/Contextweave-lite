# ContextWeave Lite - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        VS Code IDE                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           ContextWeave Extension                     │  │
│  │                                                      │  │
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
│                   FastAPI Backend                           │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  API Layer                           │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  POST /context/file                            │  │  │
│  │  │  - Validate request                            │  │  │
│  │  │  - Orchestrate analysis                        │  │  │
│  │  │  - Return structured response                  │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │              Git Analysis Layer                      │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  GitPython Operations (Deterministic)          │  │  │
│  │  │  - Read file content                           │  │  │
│  │  │  - Extract commit history                      │  │  │
│  │  │  - Calculate diffs                             │  │  │
│  │  │  - Find co-changed files                       │  │  │
│  │  │  - Parse imports                               │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │              LLM Integration Layer                   │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  AI-Powered Analysis                           │  │  │
│  │  │  - Build structured prompts                    │  │  │
│  │  │  - Call LLM API                                │  │  │
│  │  │  - Parse JSON responses                        │  │  │
│  │  │  - Handle errors & fallbacks                   │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────┬───────────────────────────────────┘  │
└────────────────────┼────────────────────────────────────────┘
                     │
                     │ HTTPS API Call
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM API Provider                         │
│         (OpenAI / Azure / AWS Bedrock / Local)              │
│                                                             │
│  - Receives: Code + Commits + Instructions                 │
│  - Returns: Summary + Decisions + Explanations             │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Request Flow (User → Backend → LLM)

```
1. User Action
   ├─ Opens file in VS Code
   ├─ Runs "ContextWeave: Explain this file"
   └─ (Optional) Selects code snippet

2. Extension Processing
   ├─ Detects file path: /path/to/repo/src/main.py
   ├─ Finds repo root: /path/to/repo
   ├─ Captures selected code (if any)
   └─ Sends HTTP POST to backend

3. Backend: API Layer
   ├─ Validates request (file exists, is in Git repo)
   ├─ Checks cache (5-minute TTL)
   └─ If cache miss, proceeds to Git layer

4. Backend: Git Layer (Deterministic)
   ├─ Reads file content from disk
   ├─ Queries Git history:
   │  ├─ Last 50 commits touching this file
   │  ├─ Commit messages, authors, dates
   │  └─ Lines changed per commit
   ├─ Extracts imports:
   │  ├─ Python: import X, from Y import Z
   │  ├─ JavaScript: import X from 'Y'
   │  └─ Java: import com.example.X
   └─ Finds co-changed files:
      ├─ Files that appear in same commits
      └─ Ranked by frequency

5. Backend: LLM Layer (AI-Powered)
   ├─ Builds structured prompt:
   │  ├─ System instructions
   │  ├─ File content (truncated if large)
   │  ├─ Commit history (top 20)
   │  ├─ Related files data
   │  └─ Selected code (if provided)
   ├─ Calls LLM API:
   │  ├─ POST to OpenAI/compatible endpoint
   │  ├─ Temperature: 0.3 (low creativity)
   │  └─ Max tokens: 1500
   └─ Parses JSON response:
      ├─ Extracts summary
      ├─ Extracts design decisions
      ├─ Extracts related files
      └─ Extracts code explanation

6. Backend: Response
   ├─ Combines LLM output with metadata
   ├─ Caches result (5 minutes)
   └─ Returns JSON to extension

7. Extension: Display
   ├─ Receives JSON response
   ├─ Updates sidebar webview:
   │  ├─ "What this file does" section
   │  ├─ "Key design decisions" section
   │  └─ "You should also read" section
   └─ Makes commit hashes and files clickable
```

### Response Flow (LLM → Backend → Extension → User)

```
LLM Response (JSON):
{
  "summary": "This file handles user authentication...",
  "decisions": [
    {
      "title": "Migrated to JWT",
      "description": "Switched from sessions to JWT tokens",
      "commits": ["abc123", "def456"]
    }
  ],
  "related_files": [
    {
      "path": "src/models/user.py",
      "reason": "User model used for authentication"
    }
  ],
  "weird_code_explanation": "This handles legacy API..."
}

Backend Processing:
├─ Validates JSON structure
├─ Adds metadata:
│  ├─ commits_analyzed: 47
│  ├─ llm_model: "gpt-3.5-turbo"
│  └─ confidence: "high"
└─ Returns to extension

Extension Rendering:
├─ Parses JSON
├─ Generates HTML with VS Code theme
├─ Adds interactivity:
│  ├─ Clickable commit hashes
│  └─ Clickable file links
└─ Displays in sidebar
```

## Component Details

### 1. VS Code Extension (TypeScript)

**Files**:
- `extension.ts` - Main entry point, command registration
- `apiClient.ts` - HTTP client for backend communication
- `sidebarProvider.ts` - Webview UI rendering

**Responsibilities**:
- Register commands in VS Code
- Detect file path and repo root
- Call backend API
- Render results in sidebar
- Handle user interactions (click file, click commit)

**Key Technologies**:
- VS Code Extension API
- TypeScript (strict mode)
- Axios (HTTP client)
- Webview API (UI)

### 2. FastAPI Backend (Python)

**Files**:
- `main.py` - API endpoints, CORS, error handling
- `schemas.py` - Pydantic models for validation
- `git_utils.py` - Git operations (deterministic)
- `llm_client.py` - LLM integration (AI-powered)

**Responsibilities**:
- Expose REST API endpoints
- Validate requests
- Orchestrate Git analysis
- Call LLM API
- Cache results
- Handle errors gracefully

**Key Technologies**:
- FastAPI (async web framework)
- Pydantic (data validation)
- GitPython (Git operations)
- httpx (async HTTP client)

### 3. Git Analysis Layer (Deterministic)

**What it does**:
- Reads file content from disk
- Queries Git history with GitPython
- Extracts commit metadata (hash, author, date, message)
- Calculates diff statistics (lines changed)
- Parses imports using regex/AST
- Finds co-changed files using commit analysis

**Why it's deterministic**:
- No interpretation or reasoning
- Pure data extraction
- Predictable, repeatable results
- No AI involved

**Output**:
```python
{
  "file_content": "...",
  "commits": [
    {
      "hash": "abc123",
      "author": "John Doe",
      "date": "2024-01-15",
      "message": "Refactored authentication",
      "lines_changed": 45
    }
  ],
  "imports": ["os", "typing", "fastapi"],
  "co_changed": [
    {"path": "src/models/user.py", "frequency": 12}
  ]
}
```

### 4. LLM Integration Layer (AI-Powered)

**What it does**:
- Builds structured prompts with context
- Calls OpenAI-compatible LLM API
- Parses JSON responses
- Handles errors and retries
- Provides fallback (mock mode)

**Why AI is needed**:
- Interprets natural language commit messages
- Synthesizes patterns across multiple commits
- Infers design intent and tradeoffs
- Generates human-readable explanations
- Adapts tone for junior developers

**Prompt Structure**:
```
System: You are a code analysis assistant
User: 
  - File content
  - Commit history (20 commits)
  - Related files data
  - Instructions (summarize, extract decisions, suggest files)
  - Output format (JSON schema)
```

**Output**:
```json
{
  "summary": "AI-generated summary",
  "decisions": [...],
  "related_files": [...],
  "weird_code_explanation": "..."
}
```

## Separation of Concerns

### Deterministic Logic (Git Layer)
- ✅ Extract data from Git
- ✅ Parse imports
- ✅ Count co-changes
- ✅ Calculate metrics
- ❌ No interpretation
- ❌ No reasoning
- ❌ No natural language generation

### AI Logic (LLM Layer)
- ✅ Interpret commit messages
- ✅ Synthesize patterns
- ✅ Infer intent
- ✅ Generate explanations
- ✅ Reason about relationships
- ❌ No data extraction
- ❌ No Git operations

**Why this separation matters**:
- Clear responsibilities
- Easy to test
- Easy to swap LLM providers
- Can work without LLM (mock mode)
- Demonstrates meaningful AI use

## Error Handling

### Extension Error Handling
```
User Action
    ↓
Try to analyze file
    ↓
Error? ─────────────┐
    │               │
    No              Yes
    ↓               ↓
Show results    Show error message
                    ├─ "Backend not reachable"
                    ├─ "File not in Git repo"
                    ├─ "No commit history"
                    └─ "LLM API error"
```

### Backend Error Handling
```
Request received
    ↓
Validate inputs ────────┐
    │                   │
    Valid               Invalid
    ↓                   ↓
Git operations      Return 400 error
    ↓
Git error? ─────────────┐
    │                   │
    No                  Yes
    ↓                   ↓
Call LLM            Return 500 error
    ↓
LLM error? ─────────────┐
    │                   │
    No                  Yes
    ↓                   ↓
Return result       Return mock response
```

## Caching Strategy

```
Request arrives
    ↓
Generate cache key: file_path + latest_commit_hash
    ↓
Check cache ────────────┐
    │                   │
    Hit                 Miss
    ↓                   ↓
Return cached       Analyze file
result                  ↓
(instant)           Cache result (5 min TTL)
                        ↓
                    Return result
```

**Why caching works**:
- Key includes commit hash → invalidates on new commits
- 5-minute TTL → balances freshness and performance
- Reduces LLM API costs
- Improves response time (instant vs 5-10 seconds)

## Security Considerations

### API Key Security
- ✅ API key stored in environment variable (not code)
- ✅ Never logged or exposed
- ✅ User provides their own key
- ❌ No shared keys
- ❌ No key storage in database

### Code Privacy
- ✅ Code sent to LLM only for analysis
- ✅ No long-term storage (5-minute cache only)
- ✅ No training on user code (OpenAI policy)
- ⚠️ User should verify LLM provider's privacy policy
- ⚠️ Don't use with proprietary code unless approved

### Input Validation
- ✅ Pydantic validates all inputs
- ✅ File paths checked for existence
- ✅ Git repo validated
- ✅ File size limits enforced
- ✅ Commit limit capped at 100

## Performance Characteristics

### Latency Breakdown
```
Total: 5-15 seconds

├─ Extension → Backend: 10-50ms
├─ Git operations: 100-500ms
│  ├─ Read file: 10-50ms
│  ├─ Query commits: 50-200ms
│  └─ Find co-changes: 50-200ms
├─ LLM API call: 3-10 seconds
│  ├─ Network: 100-500ms
│  ├─ LLM processing: 2-8 seconds
│  └─ Response parsing: 10-50ms
└─ Backend → Extension: 10-50ms
```

### Optimization Opportunities
- ✅ Cache results (5-minute TTL) - implemented
- ⚠️ Use faster LLM (GPT-3.5 vs GPT-4)
- ⚠️ Reduce commit limit (20 vs 50)
- ⚠️ Truncate large files
- ❌ Batch multiple requests - not implemented
- ❌ Stream LLM responses - not implemented

## Scalability

### Current Limits
- **Concurrent users**: ~10 (single backend instance)
- **Requests per minute**: ~60 (LLM API limit)
- **File size**: 10,000 lines (truncated beyond)
- **Commit history**: 100 commits max

### Scaling Options
1. **Horizontal scaling**: Multiple backend instances + load balancer
2. **Caching**: Redis for shared cache across instances
3. **Rate limiting**: Queue requests, throttle per user
4. **Async processing**: Background jobs for slow requests

## Deployment Architecture

### Development (Current)
```
Developer Machine
├─ Backend: localhost:8000
├─ Extension: VS Code Extension Development Host
└─ LLM: OpenAI API (internet)
```

### Production (Future)
```
                    ┌─────────────┐
                    │  VS Code    │
                    │  Extension  │
                    └──────┬──────┘
                           │
                           │ HTTPS
                           ▼
                    ┌─────────────┐
                    │ Load        │
                    │ Balancer    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         ┌────────┐   ┌────────┐   ┌────────┐
         │Backend │   │Backend │   │Backend │
         │   1    │   │   2    │   │   3    │
         └────┬───┘   └────┬───┘   └────┬───┘
              │            │            │
              └────────────┼────────────┘
                           │
                    ┌──────▼──────┐
                    │    Redis    │
                    │   (Cache)   │
                    └─────────────┘
                           │
                    ┌──────▼──────┐
                    │  LLM API    │
                    │  (Bedrock)  │
                    └─────────────┘
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | VS Code Extension API | IDE integration |
| Frontend | TypeScript | Type-safe code |
| Frontend | Webview API | Rich UI |
| Backend | FastAPI | Async web framework |
| Backend | Pydantic | Data validation |
| Backend | GitPython | Git operations |
| Backend | httpx | Async HTTP client |
| AI | OpenAI API | LLM inference |
| AI | Structured prompts | Consistent output |

## Design Principles

1. **Separation of Concerns**: Git logic ≠ AI logic
2. **Fail Gracefully**: Mock mode when LLM unavailable
3. **User Transparency**: Show sources, label AI output
4. **Performance**: Cache aggressively, optimize prompts
5. **Security**: No key storage, validate inputs
6. **Extensibility**: Easy to add new LLM providers
7. **Testability**: Pure functions, clear interfaces

---

For implementation details, see:
- [README.md](README.md) - Complete documentation
- [design.md](design.md) - Detailed technical design
- [requirements.md](requirements.md) - Product requirements
