# ContextWeave Lite - Technical Design Document

**Version:** 0.1.0 (MVP)  
**Track:** AI for Bharat – AI for Learning & Developer Productivity  
**Architecture:** VS Code Extension + FastAPI Backend + LLM API

---

## High-Level Architecture

### System Overview

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

### Component Responsibilities

**VS Code Extension:**
- User interface and command registration
- Workspace and file path detection
- HTTP communication with backend
- Result rendering in sidebar webview
- Error handling and user feedback

**FastAPI Backend:**
- API endpoint exposure and request validation
- Orchestration of Git analysis and LLM calls
- Response formatting and error handling
- Configuration management (environment variables)

**Git Analysis Layer (Deterministic):**
- Pure data extraction, no interpretation
- Commit history querying
- Import statement parsing
- Co-change frequency analysis
- File content reading

**LLM Integration Layer (AI-Powered):**
- Natural language understanding
- Reasoning and synthesis
- Human-readable text generation
- Uncertainty handling
- Source grounding

---

## Data Flow

### Flow 1: "Explain this file"

**User Action:** Right-click file → "ContextWeave: Explain this file"

**Step-by-Step:**

1. **VS Code Extension (extension.ts)**
   ```typescript
   // Detect file and repo
   const filePath = editor.document.uri.fsPath;
   const repoPath = findGitRepoRoot(filePath);
   const selectedCode = getSelectedText();
   
   // Call backend
   const response = await axios.post(`${backendUrl}/context/file`, {
     repo_path: repoPath,
     file_path: filePath,
     selected_code: selectedCode,
     commit_limit: 50
   });
   ```

2. **Backend API Layer (main.py)**
   ```python
   @app.post("/context/file")
   async def analyze_file_context(request: ContextRequest):
       # Validate inputs
       validate_git_repo(request.repo_path)
       validate_file_exists(request.file_path)
       
       # Get Git data (deterministic)
       commits = get_commit_history(request.repo_path, request.file_path)
       file_content = read_file_content(request.file_path)
       related_files = get_related_files(request.repo_path, request.file_path)
       
       # Call LLM (AI-powered)
       response = await analyze_file_with_llm(
           file_content, commits, related_files, request.selected_code
       )
       
       return response
   ```

3. **Git Analysis Layer (git_utils.py)**
   ```python
   def get_commit_history(repo_path, file_path, limit=50):
       repo = Repo(repo_path)
       relative_path = os.path.relpath(file_path, repo_path)
       commits = repo.iter_commits(paths=relative_path, max_count=limit)
       
       return [{
           "hash": commit.hexsha[:7],
           "author": commit.author.name,
           "date": commit.committed_datetime.isoformat(),
           "message": commit.message.strip(),
           "lines_changed": calculate_diff_stats(commit, relative_path)
       } for commit in commits]
   ```

4. **LLM Integration Layer (llm_client.py)**
   ```python
   async def analyze_file_with_llm(file_content, commits, related_files, selected_code):
       # Build prompt
       prompt = build_analysis_prompt(file_content, commits, related_files, selected_code)
       
       # Call LLM API
       response = await call_llm_api(prompt)
       
       # Parse JSON
       return parse_llm_response(response)
   ```

5. **VS Code Extension (sidebarProvider.ts)**
   ```typescript
   // Render results in sidebar
   showResult(response) {
       this.webview.html = `
           <h3>📄 What this file does</h3>
           <p>${response.summary}</p>
           
           <h3>🔍 Key design decisions</h3>
           ${response.decisions.map(d => `
               <div>
                   <h4>${d.title}</h4>
                   <p>${d.description}</p>
                   <span>${d.commits.join(', ')}</span>
               </div>
           `).join('')}
           
           <h3>📚 You should also read</h3>
           ${response.related_files.map(rf => `
               <a href="${rf.path}">${rf.path}</a>
               <p>${rf.reason}</p>
           `).join('')}
       `;
   }
   ```

---

## Backend Design

### API Layer (main.py)

**Responsibilities:**
- HTTP request/response handling
- Input validation (Pydantic schemas)
- Orchestration of Git analysis and LLM calls
- Error handling and logging
- CORS configuration for VS Code extension

**Key Endpoints:**

1. **GET /** - Health check
   - Returns service status and version
   - No authentication required

2. **GET /health** - Detailed health check
   - Returns LLM configuration status
   - Used by extension to verify backend connectivity

3. **POST /context/file** - Main analysis endpoint
   - Validates repo_path and file_path
   - Orchestrates Git analysis → LLM call → response formatting
   - Returns structured ContextResponse

**Error Handling:**
- 400: Invalid inputs (missing paths, not a Git repo)
- 500: Internal errors (Git failures, LLM timeouts)
- All errors include actionable messages

**Configuration:**
- Loads environment variables from `.env` file
- PORT (default: 8000)
- LLM_API_KEY, LLM_API_BASE, LLM_MODEL

---

### Git Analysis Layer (git_utils.py)

**Responsibilities:**
- Pure data extraction (no AI, no interpretation)
- Commit history querying
- Import statement parsing
- Co-change frequency analysis
- File content reading

**Key Functions:**

1. **get_commit_history(repo_path, file_path, limit)**
   - Uses GitPython to query commits
   - Returns list of commit dicts with hash, author, date, message, lines_changed
   - Handles edge cases: no commits, new files, binary files

2. **get_related_files(repo_path, file_path, file_content)**
   - Combines import detection and co-change analysis
   - Returns dict with 'imports' and 'co_changed' lists
   - Top 5 of each type

3. **extract_imports(file_content, file_path)**
   - Language-aware import parsing (Python, JS/TS, Java)
   - Uses regex patterns for each language
   - Returns list of imported file paths

4. **find_co_changed_files(repo_path, relative_path, limit)**
   - Analyzes last N commits touching the file
   - Counts how often other files appear in same commits
   - Returns top 10 files by frequency

5. **read_file_content(file_path, max_lines)**
   - Reads file with UTF-8 encoding
   - Truncates very large files (> 10,000 lines)
   - Handles encoding errors gracefully

**Design Rationale:**
- Deterministic layer provides structured data for LLM
- No interpretation or reasoning at this layer
- Fast and reliable (no API calls)
- Can be tested independently of LLM

---

### LLM Integration Layer (llm_client.py)

**Responsibilities:**
- Prompt construction
- LLM API communication
- Response parsing and validation
- Fallback to mock mode on errors

**Key Functions:**

1. **analyze_file_with_llm(...)**
   - Main entry point for LLM analysis
   - Checks if LLM_API_KEY is configured
   - Falls back to mock mode if not configured or on error
   - Returns ContextResponse

2. **build_analysis_prompt(...)**
   - Constructs structured prompt with:
     - File path and content (truncated if needed)
     - Last 20 commits (formatted)
     - Related files data
     - Selected code (if provided)
   - Includes instructions for JSON output
   - Emphasizes: simple language, cite commits, admit uncertainty

3. **call_llm(prompt)**
   - Makes HTTP POST to OpenAI-compatible API
   - Uses chat completions format
   - Temperature: 0.3 (low creativity)
   - Max tokens: 1500
   - Timeout: 30 seconds
   - Parses JSON from response (handles markdown code blocks)

4. **parse_llm_response(llm_response, commits, related_files_data)**
   - Extracts fields from LLM JSON
   - Creates ContextResponse with Pydantic models
   - Adds metadata (commits analyzed, model name)

5. **create_mock_response(...)**
   - Generates deterministic response when LLM unavailable
   - Uses only Git data (no AI)
   - Includes warning: "Configure LLM_API_KEY for AI analysis"
   - Useful for testing and demos without API key

**Prompt Engineering Strategy:**
- Clear role: "You are helping a junior developer..."
- Structured tasks: numbered list of what to do
- Source grounding: all evidence provided in prompt
- Uncertainty handling: "Admit when evidence is weak"
- Audience adaptation: "Use simple language"
- Output format: "JSON only, no markdown"

**Error Handling:**
- Invalid API key → Mock mode
- Rate limit → Mock mode
- Timeout → Mock mode
- Parse error → Mock mode
- All errors logged with details

---

## VS Code Extension Design

### Extension Entry Point (extension.ts)

**Responsibilities:**
- Extension activation and lifecycle
- Command registration
- Sidebar provider initialization
- Workspace and file detection
- Backend communication orchestration

**Key Functions:**

1. **activate(context)**
   - Registers sidebar provider
   - Registers command: `contextweave.explainFile`
   - Adds subscriptions to context

2. **handleExplainFile()**
   - Gets active editor and file path
   - Detects workspace folder (repo root)
   - Gets selected code if any
   - Shows sidebar and loading state
   - Calls backend API via apiClient
   - Shows results or error in sidebar

3. **getBackendUrl()**
   - Reads from VS Code settings
   - Default: `http://localhost:8000`
   - Configurable per workspace

**Error Handling:**
- No active file → Show error message
- File not in workspace → Show error message
- Backend connection refused → Show clear message with backend URL
- Backend error → Show backend error detail
- Network timeout → Show timeout message

---

### API Client (apiClient.ts)

**Responsibilities:**
- HTTP communication with backend
- Request/response type definitions
- Configuration management

**Key Types:**

```typescript
interface AnalysisResult {
    summary: string;
    decisions: DesignDecision[];
    related_files: RelatedFile[];
    weird_code_explanation?: string;
    metadata: {
        commits_analyzed: number;
        llm_configured?: boolean;
        mock_response?: boolean;
    };
}
```

**Key Functions:**

1. **analyzeFile(repoPath, filePath, selectedCode)**
   - Reads configuration (backendUrl, commitLimit)
   - Constructs request body
   - Makes POST request to `/context/file`
   - Returns AnalysisResult
   - Throws errors for caller to handle

**Configuration:**
- `contextweave.backendUrl` - Backend URL
- `contextweave.commitLimit` - Max commits (default: 50)

---

### Sidebar Provider (sidebarProvider.ts)

**Responsibilities:**
- Webview lifecycle management
- HTML generation for different states
- User interaction handling (click file links)
- Styling with VS Code theme colors

**Key Methods:**

1. **resolveWebviewView(webviewView, context, token)**
   - Initializes webview with options
   - Sets initial HTML
   - Registers message handlers

2. **showLoading(filePath)**
   - Displays spinner and "Analyzing..." message
   - Shows file name being analyzed

3. **showResult(result)**
   - Generates HTML from AnalysisResult
   - Renders sections: summary, decisions, related files, weird code
   - Shows mock warning if applicable
   - Makes commit hashes and file paths clickable

4. **showError(errorMessage)**
   - Displays error with suggestions
   - Styled with VS Code error colors

**HTML Generation:**
- Uses VS Code CSS variables for theming
- Responsive layout
- Clear visual hierarchy
- Accessible markup

**Interactivity:**
- File links send `openFile` message to extension
- Extension opens file in editor
- Commit badges could link to Git view (future)

**Styling:**
- Uses VS Code theme colors (foreground, background, borders)
- Consistent spacing and typography
- Icons for visual clarity (📄, 🔍, 📚, 🤔)
- Responsive to theme changes

---

## AI Design Rationale

### Why AI is Essential

**Problem:** Developers need to understand code quickly, but:
- Commit messages are unstructured natural language
- Design decisions span multiple commits
- Code semantics require deep understanding
- Explanations must be adapted for audience

**Why Rules Fail:**
- Cannot interpret natural language
- Cannot reason across multiple data points
- Cannot generate human-readable explanations
- Cannot adapt to novel code patterns

**Why AI Succeeds:**
- Natural language understanding (commit messages)
- Semantic code understanding (what code does)
- Reasoning and synthesis (patterns across commits)
- Natural language generation (clear explanations)
- Audience adaptation (junior developer tone)

### Deterministic vs AI Layers

**Deterministic Layer (Git Analysis):**
- Fast and reliable
- No API costs
- Testable and predictable
- Provides structured data for AI

**AI Layer (LLM Integration):**
- Interprets unstructured data
- Reasons about intent and tradeoffs
- Generates human-readable text
- Handles novel situations

**Design Principle:** Use rules where possible, AI where necessary.

### Responsible AI Practices

**Transparency:**
- All AI output labeled "AI-generated"
- Model name shown in metadata
- Mock mode clearly indicated

**Source Attribution:**
- Commit hashes cited for all decisions
- Clickable links to evidence
- Metadata shows how many commits analyzed

**Uncertainty Handling:**
- Prompt instructs: "Admit when evidence is weak"
- System shows warnings when commit history is sparse
- Never invents information not in data

**Privacy:**
- Code sent to LLM only for analysis (not training)
- User provides their own API key
- No long-term storage of code
- Warning about sending proprietary code to cloud

**No Hallucination:**
- Prompt emphasizes: "Base answer only on provided commits"
- Response validation checks for invented commit hashes
- Fallback to mock mode if LLM response is invalid

---

## Alignment with AI for Bharat

### Target Users: Indian Developers

**Students (Tier-2/Tier-3 colleges):**
- Learning from real-world GitHub projects
- Limited access to mentors
- Need to understand code quickly to contribute

**New Graduates:**
- Joining companies with large legacy codebases
- Minimal documentation
- Senior developers are overloaded

**Junior Developers:**
- Maintaining inherited code
- Original authors have left
- Afraid to break things

### Value Proposition

**5-10x Faster Learning:**
- Manual analysis: 30 minutes per file
- With ContextWeave: 3 minutes per file
- Reduces onboarding time from 6 weeks to 3 weeks

**Democratized Knowledge:**
- No need to wait for senior developer
- Self-service understanding
- Builds confidence to contribute

**Reduced Dependency:**
- Less "why" questions to seniors
- Empowers junior developers
- Frees up senior time for high-value work

### India-Specific Challenges Addressed

**Documentation Gap:**
- Legacy codebases have no docs
- ContextWeave generates docs from Git history

**Knowledge Concentration:**
- 1-2 seniors hold all context
- ContextWeave extracts knowledge from commits

**Noisy Git History:**
- Commit messages like "fix", "update"
- AI interprets and synthesizes patterns

**Slow Onboarding:**
- New hires take 4-6 weeks to be productive
- ContextWeave accelerates learning curve

---

## Trade-offs and Design Decisions

### Trade-off 1: External LLM vs Self-Hosted

**Decision:** Use external LLM API (Groq/OpenAI)

**Rationale:**
- Faster development (no model training/hosting)
- Better quality (state-of-the-art models)
- Lower cost for MVP (free tiers available)
- Easier to swap models (just change API key)

**Downside:**
- Requires internet connection
- Privacy concerns (code sent to cloud)
- API costs at scale

**Mitigation:**
- Provide mock mode for offline use
- Warn users about sending proprietary code
- Support multiple providers (Groq, OpenAI, Bedrock)

---

### Trade-off 2: File-Level vs Repository-Level Analysis

**Decision:** File-level analysis only (MVP)

**Rationale:**
- Simpler to implement
- Faster response time
- Easier to understand results
- Fits VS Code workflow (one file at a time)

**Downside:**
- Misses cross-file architectural patterns
- Cannot explain system-level design decisions

**Future Extension:**
- Add "Explain this module" command
- Add "Explain this feature" command
- Add architectural diagram generation

---

### Trade-off 3: Real-Time vs Cached Analysis

**Decision:** Real-time analysis (no caching for MVP)

**Rationale:**
- Simpler implementation
- Always up-to-date results
- No cache invalidation complexity

**Downside:**
- Slower for repeated queries
- Higher API costs

**Future Extension:**
- Cache results for 5 minutes
- Invalidate on file changes
- Show "cached" indicator in UI

---

### Trade-off 4: Structured Prompt vs Fine-Tuned Model

**Decision:** Structured prompt with general-purpose model

**Rationale:**
- No training data required
- Works with any OpenAI-compatible model
- Easy to iterate on prompt
- Lower cost and complexity

**Downside:**
- Less consistent than fine-tuned model
- Longer prompts (more tokens)

**Future Extension:**
- Fine-tune on high-quality examples
- Reduce prompt length
- Improve consistency

---

## Future Extensions

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

## Deployment Architecture (Future)

### Local Development (Current)
```
Developer Machine
├── VS Code Extension
├── Backend (localhost:8000)
└── External LLM API (Groq/OpenAI)
```

### Team Deployment (Future)
```
Developer Machines (VS Code Extension)
         ↓
    Load Balancer
         ↓
Backend Cluster (AWS EC2/ECS)
         ↓
AWS Bedrock (LLM) or OpenAI API
```

### Enterprise Deployment (Future)
```
Developer Machines (VS Code Extension)
         ↓
    API Gateway
         ↓
Backend Cluster (Kubernetes)
         ↓
Self-Hosted LLM (AWS SageMaker)
         ↓
Vector DB (Pinecone) for caching
```

---

## Testing Strategy

### Unit Tests
- Git analysis functions (mock Git repos)
- Import parsing (sample code files)
- Prompt construction (verify format)
- Response parsing (mock LLM responses)

### Integration Tests
- Backend API endpoints (mock LLM)
- VS Code extension commands (mock backend)
- End-to-end flow (real Git repo, mock LLM)

### Manual Testing
- Real repositories (open-source projects)
- Edge cases (empty files, no commits, binary files)
- Error scenarios (backend down, invalid API key)
- UI/UX (readability, clickability, responsiveness)

### User Testing
- 5+ developers from target segment
- Task: Understand a file in an unfamiliar codebase
- Metrics: Time to understanding, accuracy, satisfaction
- Feedback: What worked, what didn't, what's missing

---

## Success Metrics

### Technical Metrics
- Latency: < 15 seconds per analysis
- Accuracy: 80%+ helpful summaries (manual review)
- Reliability: 99%+ uptime during demo
- Error rate: < 5% of requests fail

### User Metrics
- Speed: 5-10x faster than manual analysis
- Adoption: 5+ developers report value
- Learning: Users understand files they couldn't before
- Satisfaction: 4+ stars out of 5

### Hackathon Metrics
- Demo quality: Works reliably during presentation
- Judge understanding: Clear why AI is essential
- India impact: Clear value for target users
- Documentation: Comprehensive and well-organized

---

**Document Version:** 1.0  
**Last Updated:** February 7, 2026  
**Status:** Complete
