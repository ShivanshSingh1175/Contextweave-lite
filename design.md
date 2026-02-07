# ContextWeave Lite - Design Document

## High-Level Architecture

ContextWeave Lite follows a client-server architecture where a VS Code extension communicates with a FastAPI backend that orchestrates Git analysis and LLM-powered reasoning.

```
┌─────────────────┐
│   VS Code IDE   │
│  ┌───────────┐  │
│  │ Extension │  │ (TypeScript)
│  │  + Sidebar│  │
│  └─────┬─────┘  │
└────────┼────────┘
         │ HTTP/JSON
         ▼
┌─────────────────┐
│  FastAPI Backend│ (Python 3.11)
│  ┌───────────┐  │
│  │ API Layer │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │Git Layer  │  │ (GitPython)
│  │(commits,  │  │
│  │ diffs)    │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │LLM Adapter│  │ (OpenAI/Bedrock)
│  │(prompts,  │  │
│  │ parsing)  │  │
│  └───────────┘  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   LLM API       │ (OpenAI GPT-4 / AWS Bedrock)
│ (Claude, GPT-4) │
└─────────────────┘
```

### Component Overview

**VS Code Extension (Client)**
- Provides UI commands and context menu integration
- Renders sidebar webview with analysis results
- Manages state (loading, error, success)
- Handles user interactions (click commit hash, open related file)

**FastAPI Backend (Server)**
- Exposes REST API endpoints for file analysis
- Orchestrates Git queries and LLM calls
- Implements caching and error handling
- Can run locally or on AWS (EC2/Lightsail)

**Git Layer (GitPython)**
- Deterministic logic: queries commit history, diffs, file metadata
- Extracts structured data: commit messages, authors, dates, changed lines
- Computes simple heuristics: imports, co-changed files

**LLM Adapter**
- AI logic: interprets natural language, infers intent, synthesizes explanations
- Formats prompts with context (code + commits)
- Parses LLM responses into structured JSON
- Handles rate limits, retries, and fallbacks


## Data Flow

### Flow 1: "Explain this file"

**User Action:** Right-click a file in VS Code → "Analyze with ContextWeave"

**Step-by-step:**

1. **VS Code Extension**
   - Detects active file path: `src/services/PaymentService.java`
   - Finds Git repo root: `/home/user/banking-app`
   - Sends POST request to backend: `http://localhost:8000/api/context/file`
   - Request body:
     ```json
     {
       "repo_path": "/home/user/banking-app",
       "file_path": "src/services/PaymentService.java"
     }
     ```

2. **Backend API Layer**
   - Validates inputs (file exists, is in Git repo)
   - Checks cache (5-minute TTL, keyed by file path + latest commit hash)
   - If cache miss, proceeds to Git layer

3. **Git Layer (Deterministic)**
   - Reads file content from disk
   - Queries Git history: `git log --follow -n 50 -- <file_path>`
   - Extracts for each commit:
     - Commit hash, author, date, message
     - Diff (lines added/removed)
   - Computes related files:
     - Parse imports from file content (regex/AST)
     - Query co-changed files: `git log --name-only --follow -- <file_path>`
     - Rank by co-change frequency

4. **LLM Adapter (AI Logic)**
   - Constructs prompt with:
     - File content (truncated to 8000 tokens if needed)
     - Last 20 commits (messages + diffs)
     - Metadata (language, file size)
   - Calls LLM API (OpenAI GPT-4 or AWS Bedrock Claude)
   - Prompt structure:
     ```
     You are helping a junior developer understand a codebase.
     
     File: src/services/PaymentService.java
     Content: [file content]
     
     Recent commits (last 20):
     - abc123 (2024-01-15, Priya): "Refactored to use async/await"
       Diff: [diff]
     - def456 (2024-02-20, Arjun): "Added retry logic for failed payments"
       Diff: [diff]
     ...
     
     Tasks:
     1. Summarize what this file does in 2-3 sentences (simple language).
     2. Extract 2-3 key design decisions from commits. For each:
        - Decision description (1-2 sentences)
        - Commit hash(es) as evidence
        - Why this decision matters
     3. If evidence is weak, say "Limited commit history" instead of guessing.
     
     Output JSON:
     {
       "summary": "...",
       "design_decisions": [
         {"decision": "...", "commits": ["abc123"], "reasoning": "..."}
       ],
       "confidence": "high" | "medium" | "low"
     }
     ```
   - Parses JSON response, validates structure

5. **Backend Response**
   - Combines LLM output with related files (from Git layer)
   - Returns JSON:
     ```json
     {
       "summary": "This file handles payment processing...",
       "design_decisions": [
         {
           "decision": "Refactored to async/await for better performance",
           "commits": ["abc123"],
           "reasoning": "Reduces blocking I/O during payment gateway calls"
         }
       ],
       "related_files": [
         {
           "path": "src/repositories/PaymentRepository.java",
           "relationship": "This service calls PaymentRepository for database access"
         }
       ],
       "metadata": {
         "commits_analyzed": 20,
         "date_range": "2023-01-15 to 2024-12-20",
         "confidence": "high"
       }
     }
     ```

6. **VS Code Extension**
   - Receives response, updates sidebar UI
   - Renders three sections:
     - "What this file does" (summary)
     - "Key design decisions" (with clickable commit hashes)
     - "You should also read" (related files)
   - Shows metadata footer: "Based on 20 commits from Jan 2023 to Dec 2024"

### Flow 2: "Why is this weird?" (Selected Code Region)

**User Action:** Select 5-10 lines of code → Right-click → "ContextWeave: Explain this code"

**Step-by-step:**

1. **VS Code Extension**
   - Captures selected text and line range
   - Sends POST request: `http://localhost:8000/api/context/explain-code`
   - Request body:
     ```json
     {
       "repo_path": "/home/user/banking-app",
       "file_path": "src/services/PaymentService.java",
       "code_snippet": "if (amount < 0) { amount = Math.abs(amount); }",
       "line_start": 45,
       "line_end": 47
     }
     ```

2. **Backend Git Layer**
   - Queries commits that touched these specific lines: `git log -L 45,47:<file_path>`
   - Extracts commit messages and diffs for context

3. **LLM Adapter**
   - Constructs prompt:
     ```
     A junior developer is confused by this code snippet.
     Explain why it might be written this way.
     
     File: src/services/PaymentService.java
     Lines 45-47:
     if (amount < 0) { amount = Math.abs(amount); }
     
     Commits that touched these lines:
     - xyz789 (2023-06-10): "Handle negative amounts from legacy API"
       Diff: [diff]
     
     Task: Explain in 2-3 sentences why this code exists.
     If you don't know, say "No clear explanation in commit history."
     ```
   - Parses response

4. **Backend Response**
   - Returns explanation:
     ```json
     {
       "explanation": "This handles negative amounts from a legacy API that sometimes returns negative values. The code converts them to positive to avoid downstream errors.",
       "commits": ["xyz789"],
       "confidence": "medium"
     }
     ```

5. **VS Code Extension**
   - Shows explanation in a hover tooltip or sidebar panel
   - Includes commit reference for verification


## Backend Design

### API Endpoints

**POST /api/context/file**
- **Purpose:** Analyze a file and return summary, design decisions, related files
- **Input:**
  ```json
  {
    "repo_path": "/absolute/path/to/repo",
    "file_path": "relative/path/to/file.py",
    "commit_limit": 50  // optional, default 50
  }
  ```
- **Output:** See Flow 1 response above
- **Caching:** 5-minute TTL, keyed by `(file_path, latest_commit_hash)`
- **Error Codes:**
  - 400: Invalid input (file not found, not in Git repo)
  - 429: LLM API rate limit exceeded
  - 500: Internal error (Git failure, LLM timeout)

**POST /api/context/explain-code**
- **Purpose:** Explain a selected code snippet
- **Input:**
  ```json
  {
    "repo_path": "/absolute/path/to/repo",
    "file_path": "relative/path/to/file.py",
    "code_snippet": "selected code",
    "line_start": 10,
    "line_end": 15
  }
  ```
- **Output:** See Flow 2 response above

**GET /api/health**
- **Purpose:** Health check for backend and LLM API connectivity
- **Output:**
  ```json
  {
    "status": "healthy",
    "llm_api": "connected",
    "version": "0.1.0"
  }
  ```

### Git Layer Implementation

**Commit History Fetching**

```python
# Pseudocode
def get_commit_history(repo_path: str, file_path: str, limit: int = 50):
    repo = git.Repo(repo_path)
    commits = list(repo.iter_commits(paths=file_path, max_count=limit))
    
    result = []
    for commit in commits:
        # Get diff for this file
        if commit.parents:
            diff = commit.parents[0].diff(commit, paths=file_path)
        else:
            diff = None  # Initial commit
        
        result.append({
            "hash": commit.hexsha[:7],
            "author": commit.author.name,
            "date": commit.committed_datetime.isoformat(),
            "message": commit.message.strip(),
            "diff": extract_diff_text(diff) if diff else None,
            "lines_changed": count_lines_changed(diff) if diff else 0
        })
    
    # Sort by recency (most recent first)
    return result
```

**Filtering Strategy:**
- Take last 50 commits by default (configurable)
- Prioritize commits with meaningful messages (> 10 characters, not just "fix" or "update")
- Prioritize commits with larger diffs (more lines changed = more significant)
- For LLM input, send top 20 commits (balance context vs token cost)

**Related Files Computation**

```python
# Pseudocode
def get_related_files(repo_path: str, file_path: str):
    # 1. Parse imports (deterministic)
    imports = parse_imports(file_path)  # regex or AST
    
    # 2. Co-changed files (deterministic)
    repo = git.Repo(repo_path)
    commits = repo.iter_commits(paths=file_path, max_count=100)
    
    co_changed = Counter()
    for commit in commits:
        changed_files = [item.a_path for item in commit.stats.files.keys()]
        for f in changed_files:
            if f != file_path:
                co_changed[f] += 1
    
    # 3. Combine and rank
    related = []
    for imp in imports[:5]:  # Top 5 imports
        related.append({"path": imp, "score": 10, "type": "import"})
    
    for f, count in co_changed.most_common(5):
        related.append({"path": f, "score": count, "type": "co-changed"})
    
    # Sort by score, return top 3
    related.sort(key=lambda x: x["score"], reverse=True)
    return related[:3]
```

**Why this is deterministic (not AI):**
- Import parsing uses regex or AST (no interpretation needed)
- Co-change frequency is a simple count (no reasoning)
- Ranking is by score (no semantic understanding)

**AI layer adds value by:**
- Explaining *why* files are related ("This service calls that repository")
- Filtering out false positives (files changed together for unrelated reasons)

### LLM Integration

**Prompt Design Principles**

1. **Conciseness:** Request 2-3 sentences, not paragraphs
2. **Evidence-based:** Provide commits as context, ask for citations
3. **Uncertainty handling:** Explicitly ask model to say "limited evidence" when appropriate
4. **Structured output:** Request JSON for easy parsing
5. **Audience-aware:** Specify "junior developer" or "student" as audience

**Example Prompt Template (File Summary)**

```python
PROMPT_TEMPLATE = """
You are helping a junior developer in India understand a codebase.
They are new to this project and need clear, simple explanations.

File: {file_path}
Language: {language}
Content:
{file_content}

Recent commits (last {commit_count}):
{commit_history}

Tasks:
1. Summarize what this file does in 2-3 sentences.
   - Use simple language (avoid jargon where possible)
   - Focus on the main purpose and responsibilities
   
2. Extract 2-3 key design decisions from the commit history.
   - For each decision:
     * Describe the decision in 1-2 sentences
     * Cite the commit hash(es) as evidence
     * Explain why this decision matters (performance, maintainability, etc.)
   - If commit messages are unclear or too brief, say "Limited commit context available"
   
3. Assess your confidence:
   - "high" if commits are detailed and code is clear
   - "medium" if commits are brief but code is understandable
   - "low" if commits are sparse or code is ambiguous

Output JSON only (no markdown):
{{
  "summary": "...",
  "design_decisions": [
    {{"decision": "...", "commits": ["abc123"], "reasoning": "..."}}
  ],
  "confidence": "high" | "medium" | "low"
}}
"""
```

**LLM API Call**

```python
# Pseudocode
async def call_llm(prompt: str, model: str = "gpt-4"):
    try:
        response = await openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a code analysis assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Low creativity, high consistency
            max_tokens=1000,
            timeout=10  # 10 second timeout
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    except openai.error.RateLimitError:
        raise HTTPException(429, "LLM API rate limit exceeded")
    except openai.error.Timeout:
        raise HTTPException(504, "LLM API timeout")
    except json.JSONDecodeError:
        # Fallback: return raw text
        return {"summary": content, "design_decisions": [], "confidence": "low"}
```

**Caching Strategy**

```python
# Pseudocode
cache = {}  # In-memory cache (or Redis for production)

def get_cached_analysis(file_path: str, latest_commit_hash: str):
    cache_key = f"{file_path}:{latest_commit_hash}"
    
    if cache_key in cache:
        entry = cache[cache_key]
        if time.now() - entry["timestamp"] < 300:  # 5 minutes
            return entry["data"]
    
    return None

def set_cached_analysis(file_path: str, latest_commit_hash: str, data: dict):
    cache_key = f"{file_path}:{latest_commit_hash}"
    cache[cache_key] = {
        "data": data,
        "timestamp": time.now()
    }
```

**Why caching matters:**
- Reduces LLM API costs (OpenAI charges per token)
- Improves latency (5 seconds → instant for repeated requests)
- Keyed by commit hash ensures freshness (invalidates on new commits)

### Error Handling

**Git Errors:**
- File not found → 400 with message: "File not found in repository"
- Not a Git repo → 400 with message: "Directory is not a Git repository"
- No commit history → Return summary only, skip design decisions

**LLM Errors:**
- Rate limit → 429 with retry-after header
- Timeout → 504 with message: "LLM API timeout, try again"
- Invalid JSON → Fallback to raw text response, log warning

**Edge Cases:**
- Binary file → 400 with message: "Binary files not supported"
- File > 10,000 lines → Truncate to first 8,000 tokens, add note in response
- Empty file → Return: "This file is empty"


## VS Code Extension Design

### Activation & Discovery

**Activation Events**
```json
// package.json
{
  "activationEvents": [
    "onCommand:contextweave.analyzeFile",
    "onCommand:contextweave.explainCode",
    "onView:contextweave.sidebar"
  ]
}
```

**Commands:**
- `contextweave.analyzeFile` - Analyze current file
- `contextweave.explainCode` - Explain selected code region
- `contextweave.openSettings` - Configure backend URL, API key

**Context Menu Integration:**
```json
// package.json contributions
{
  "menus": {
    "explorer/context": [
      {
        "command": "contextweave.analyzeFile",
        "when": "resourceScheme == file",
        "group": "navigation"
      }
    ],
    "editor/context": [
      {
        "command": "contextweave.explainCode",
        "when": "editorHasSelection",
        "group": "navigation"
      }
    ]
  }
}
```

**Repo Root Discovery**

```typescript
// Pseudocode
async function findRepoRoot(filePath: string): Promise<string | null> {
  // Use VS Code Git extension API
  const gitExtension = vscode.extensions.getExtension('vscode.git')?.exports;
  const git = gitExtension.getAPI(1);
  
  // Find repository containing this file
  const repo = git.repositories.find(r => 
    filePath.startsWith(r.rootUri.fsPath)
  );
  
  return repo ? repo.rootUri.fsPath : null;
}
```

### Backend Communication

**API Client**

```typescript
// Pseudocode
class ContextWeaveClient {
  private baseUrl: string;
  
  constructor() {
    // Read from VS Code settings
    const config = vscode.workspace.getConfiguration('contextweave');
    this.baseUrl = config.get('backendUrl', 'http://localhost:8000');
  }
  
  async analyzeFile(repoPath: string, filePath: string): Promise<AnalysisResult> {
    const response = await fetch(`${this.baseUrl}/api/context/file`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo_path: repoPath, file_path: filePath })
    });
    
    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }
    
    return await response.json();
  }
  
  async explainCode(
    repoPath: string, 
    filePath: string, 
    snippet: string, 
    lineStart: number, 
    lineEnd: number
  ): Promise<ExplanationResult> {
    // Similar to analyzeFile
  }
}
```

**Loading States**

```typescript
// Pseudocode
async function handleAnalyzeFile() {
  const editor = vscode.window.activeTextEditor;
  if (!editor) return;
  
  const filePath = editor.document.uri.fsPath;
  const repoPath = await findRepoRoot(filePath);
  
  if (!repoPath) {
    vscode.window.showErrorMessage('File is not in a Git repository');
    return;
  }
  
  // Show loading in sidebar
  sidebarView.showLoading('Analyzing file...');
  
  try {
    const result = await client.analyzeFile(repoPath, filePath);
    sidebarView.showResult(result);
  } catch (error) {
    if (error.status === 429) {
      vscode.window.showErrorMessage('Rate limit exceeded. Try again in a minute.');
    } else {
      vscode.window.showErrorMessage(`Analysis failed: ${error.message}`);
    }
    sidebarView.showError(error);
  }
}
```

### Sidebar UI Design

**Layout Structure**

```
┌─────────────────────────────────┐
│ ContextWeave Insights           │
├─────────────────────────────────┤
│ 📄 PaymentService.java          │
│                                 │
│ ✨ What this file does          │
│ ─────────────────────────────── │
│ This file handles payment       │
│ processing for the banking app. │
│ It validates transactions and   │
│ communicates with the payment   │
│ gateway API.                    │
│                                 │
│ 🔍 Key design decisions         │
│ ─────────────────────────────── │
│ • Refactored to async/await     │
│   for better performance        │
│   📎 abc123 (Jan 15, 2024)      │
│                                 │
│ • Added retry logic for failed  │
│   payments to handle timeouts   │
│   📎 def456 (Feb 20, 2024)      │
│                                 │
│ 📚 You should also read         │
│ ─────────────────────────────── │
│ • PaymentRepository.java        │
│   This service calls this repo  │
│   for database access           │
│                                 │
│ • PaymentConfig.java            │
│   Configuration for payment     │
│   gateway settings              │
│                                 │
├─────────────────────────────────┤
│ ℹ️ Based on 20 commits          │
│    Jan 2023 - Dec 2024          │
│    Confidence: High             │
│                                 │
│ ⚠️ AI-generated insights may be │
│    incomplete. Verify sources.  │
└─────────────────────────────────┘
```

**Webview Implementation**

```typescript
// Pseudocode
class SidebarProvider implements vscode.WebviewViewProvider {
  resolveWebviewView(webviewView: vscode.WebviewView) {
    webviewView.webview.options = {
      enableScripts: true
    };
    
    webviewView.webview.html = this.getHtmlContent();
    
    // Handle messages from webview
    webviewView.webview.onDidReceiveMessage(message => {
      switch (message.type) {
        case 'openCommit':
          this.openCommitInGitHistory(message.hash);
          break;
        case 'openFile':
          this.openRelatedFile(message.path);
          break;
      }
    });
  }
  
  private getHtmlContent(): string {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <style>
          body { 
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            padding: 16px;
          }
          .section { margin-bottom: 24px; }
          .section-title { 
            font-weight: bold; 
            margin-bottom: 8px;
            display: flex;
            align-items: center;
          }
          .commit-link {
            color: var(--vscode-textLink-foreground);
            cursor: pointer;
            text-decoration: none;
          }
          .commit-link:hover {
            text-decoration: underline;
          }
          .ai-badge {
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
            margin-left: 8px;
          }
          .footer {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            border-top: 1px solid var(--vscode-panel-border);
            padding-top: 12px;
            margin-top: 24px;
          }
        </style>
      </head>
      <body>
        <div id="content">Loading...</div>
        <script>
          const vscode = acquireVsCodeApi();
          
          function openCommit(hash) {
            vscode.postMessage({ type: 'openCommit', hash });
          }
          
          function openFile(path) {
            vscode.postMessage({ type: 'openFile', path });
          }
        </script>
      </body>
      </html>
    `;
  }
  
  showResult(result: AnalysisResult) {
    // Update webview content with result
    this.webview.postMessage({ type: 'showResult', data: result });
  }
}
```

**UX Principles for Learning**

1. **5-Second Comprehension:** Use clear headings, short paragraphs, bullet points
2. **Visual Hierarchy:** Icons (✨ 🔍 📚) help scan sections quickly
3. **Clickable Evidence:** Commit hashes are links, not just text
4. **Simple Language:** Avoid jargon; explain in terms a student would understand
5. **Transparency:** Always show AI badge and disclaimer
6. **Progressive Disclosure:** Collapsible sections for advanced details

### Settings & Configuration

**User Settings (settings.json)**

```json
{
  "contextweave.backendUrl": "http://localhost:8000",
  "contextweave.commitLimit": 50,
  "contextweave.autoAnalyze": false,  // Auto-analyze on file open
  "contextweave.showConfidence": true  // Show confidence scores
}
```

**Settings UI (package.json)**

```json
{
  "contributes": {
    "configuration": {
      "title": "ContextWeave",
      "properties": {
        "contextweave.backendUrl": {
          "type": "string",
          "default": "http://localhost:8000",
          "description": "URL of the ContextWeave backend server"
        },
        "contextweave.commitLimit": {
          "type": "number",
          "default": 50,
          "description": "Number of commits to analyze (max 100)"
        }
      }
    }
  }
}
```


## AI Design

### Why LLMs are Required (Not Rule-Based Systems)

**The Core Problem: Natural Language Understanding + Reasoning**

Rule-based systems excel at deterministic tasks (parsing syntax, counting lines, sorting data) but fail at:

1. **Interpreting Noisy Natural Language**
   - Commit messages are inconsistent: "fix bug", "refactored for perf", "updated logic", "asdfasdf"
   - No standard format or vocabulary
   - Typos, abbreviations, context-dependent meaning
   - Example: "migrated to async" vs "made it faster" vs "fixed blocking issue" all mean similar things

2. **Synthesizing Multiple Signals**
   - A design decision often spans 5-10 commits over weeks
   - Need to merge "added async method" + "refactored callers" + "removed old sync code" into one narrative
   - Rule-based systems would need complex graph analysis and hardcoded heuristics for every pattern

3. **Inferring Intent and Tradeoffs**
   - Why was async chosen over sync? (Performance vs complexity tradeoff)
   - Why was this library replaced? (Security, maintenance, licensing)
   - Rules can't infer "why" from "what"—they lack reasoning capability

4. **Explaining Code Semantically**
   - "This is a repository pattern" requires understanding design patterns across languages
   - "This handles edge case X" requires understanding business logic, not just syntax
   - Rules would need language-specific parsers + pattern databases for every framework

5. **Adapting to Audience**
   - Junior developers need simpler explanations than senior engineers
   - Students need more context than experienced professionals
   - LLMs can adjust tone and detail level; templates cannot

**What Happens Without AI:**

Without LLMs, ContextWeave becomes a glorified commit browser:
- Shows raw commit messages (no synthesis)
- Lists files that changed together (no explanation of relationships)
- Displays code (no semantic understanding)

**The learning value disappears.** Users still need to manually read commits, infer patterns, and build mental models—exactly the problem we're solving.

### Prompt Strategy

**Design Principle: Structured Prompts with Evidence Grounding**

All prompts follow this pattern:
1. **Role definition:** "You are helping a junior developer..."
2. **Context:** File content, commit history, metadata
3. **Task:** Specific, measurable output (2-3 sentences, JSON format)
4. **Constraints:** Simple language, cite sources, admit uncertainty
5. **Output format:** JSON schema for easy parsing

**Prompt 1: File Summary**

```
You are helping a junior developer in India understand a codebase.
They are new to this project and need clear, simple explanations.

File: {file_path}
Language: {language}
Size: {line_count} lines

Content:
{file_content}

Task: Summarize what this file does in 2-3 sentences.
- Use simple language (avoid jargon where possible)
- Focus on the main purpose and responsibilities
- Mention key classes/functions if relevant

Output JSON only:
{
  "summary": "..."
}
```

**Why this works:**
- Specifies audience (junior developer) → adjusts complexity
- Requests conciseness (2-3 sentences) → avoids verbosity
- Provides full context (file content) → grounds response in reality

**Prompt 2: Design Decisions**

```
You are analyzing Git history to help a new developer understand design decisions.

File: {file_path}

Recent commits (last {commit_count}):
{commit_list}

Each commit includes:
- Hash, author, date
- Commit message
- Diff (lines added/removed)

Task: Extract 2-3 key design decisions from these commits.
Focus on:
- Architectural changes (e.g., "migrated from REST to GraphQL")
- Refactorings (e.g., "switched to async/await")
- Performance improvements
- Bug fixes with reasoning (not just "fixed bug")

For each decision:
1. Describe the decision in 1-2 sentences
2. Cite the commit hash(es) as evidence
3. Explain why this decision matters (performance, maintainability, security, etc.)

Important:
- If commit messages are too brief or unclear, say "Limited commit context available"
- If fewer than 5 commits, say "Insufficient commit history for design analysis"
- Never invent information not present in commits

Output JSON only:
{
  "design_decisions": [
    {
      "decision": "...",
      "commits": ["abc123", "def456"],
      "reasoning": "...",
      "category": "performance" | "architecture" | "refactoring" | "bugfix"
    }
  ],
  "confidence": "high" | "medium" | "low",
  "notes": "Optional: explain why confidence is low"
}
```

**Why this works:**
- Provides structured commit data → LLM doesn't need to parse Git output
- Requests citations → prevents hallucination
- Explicitly handles uncertainty → builds trust
- Categorizes decisions → helps users understand types of changes

**Prompt 3: "Why is this weird?" (Code Explanation)**

```
A junior developer is confused by this code snippet and wants to understand why it's written this way.

File: {file_path}
Lines {line_start}-{line_end}:
{code_snippet}

Commits that touched these lines:
{commit_list}

Task: Explain in 2-3 sentences why this code exists or why it's written this way.
- Look for clues in commit messages (e.g., "workaround for X", "handles edge case Y")
- If the code seems unusual, explain the likely reason (performance, compatibility, bug fix)
- If you don't know, say "No clear explanation in commit history"

Output JSON only:
{
  "explanation": "...",
  "commits": ["xyz789"],
  "confidence": "high" | "medium" | "low"
}
```

**Why this works:**
- Focuses on specific lines → reduces context size
- Looks for historical reasoning → grounds explanation in reality
- Admits ignorance when appropriate → avoids hallucination

### Responsible AI Behaviors

**RAI-1: Citation & Source Grounding**

Every AI-generated claim must be traceable to source data:
- Design decisions cite commit hashes
- Code explanations reference specific commits
- Related file explanations show import statements or co-change data

**Implementation:**
```python
# Pseudocode
def validate_citations(response: dict, commits: list):
    """Ensure all cited commits actually exist"""
    cited_hashes = [c for d in response["design_decisions"] for c in d["commits"]]
    valid_hashes = [c["hash"] for c in commits]
    
    for hash in cited_hashes:
        if hash not in valid_hashes:
            # Log warning, remove invalid citation
            logger.warning(f"LLM cited non-existent commit: {hash}")
```

**RAI-2: Labeling AI Output**

All AI-generated content is clearly marked:
- Sidebar shows "✨ AI-generated" badge
- Footer includes disclaimer: "AI-generated insights may be incomplete. Always verify with source code."
- Confidence scores shown when available (high/medium/low)

**RAI-3: Handling Uncertainty**

The system explicitly handles cases where evidence is weak:

| Scenario | Response |
|----------|----------|
| < 5 commits | "Limited commit history available for this file" |
| Brief commit messages | "Commit messages are brief; design decisions may be incomplete" |
| No commits touching selected lines | "No commit history found for this code region" |
| LLM confidence = low | Show warning: "Analysis confidence is low due to limited context" |

**Implementation:**
```python
# Pseudocode
def handle_sparse_history(commits: list):
    if len(commits) < 5:
        return {
            "summary": generate_summary_from_code_only(),
            "design_decisions": [],
            "notes": "Limited commit history available for this file"
        }
    
    if avg_commit_message_length(commits) < 20:
        # Warn user that analysis may be incomplete
        return {
            "design_decisions": extract_decisions(commits),
            "confidence": "low",
            "notes": "Commit messages are brief; design decisions may be incomplete"
        }
```

**RAI-4: Privacy & Data Handling**

- Repository code is sent to LLM API only for analysis (not training)
- No long-term storage of code or analysis (5-minute cache only)
- Users provide their own API keys (no shared keys)
- Optional: use AWS Bedrock for data residency in India

**Warning in UI:**
```
⚠️ Privacy Notice:
Code is sent to [OpenAI/AWS Bedrock] for analysis.
Do not use with proprietary code unless your organization approves.
```

**RAI-5: Bias & Fairness**

- Use simple, clear language accessible to non-native English speakers
- Avoid cultural assumptions (e.g., don't assume familiarity with Western tech companies)
- Test with codebases from Indian companies and colleges
- Avoid jargon specific to Silicon Valley or US tech culture

**Example:**
- ❌ "This is a typical FAANG-style microservice"
- ✅ "This is a microservice that handles user authentication"


## Alignment with AI for Bharat: Learning & Developer Productivity

### Target User Context

**Who We're Helping:**
- **New graduates** from Tier-2/Tier-3 colleges joining large BFSI or service companies
- **Junior developers** (0-2 years experience) working on legacy codebases with poor documentation
- **Students** inheriting college projects or contributing to open source
- **Self-taught developers** learning professional development practices

**Their Challenges:**
- Large codebases (1000+ files) with minimal documentation
- Senior developers too busy to answer "why" questions
- Pressure to deliver quickly without understanding context
- Limited exposure to design patterns and architectural reasoning
- English may not be first language (need simple, clear explanations)

### How ContextWeave Helps

**1. Accelerates Learning (5-10x faster)**

Traditional approach:
- Read 500 lines of code → 30 minutes
- Search Git history manually → 20 minutes
- Ask senior developer → 10 minutes (if available)
- **Total: ~60 minutes per file**

With ContextWeave:
- Right-click file → see summary, decisions, related files
- **Total: ~5 minutes per file**

**Impact:** New developers can explore 10-12 files per hour instead of 1-2.

**2. Reduces Senior Developer Burden**

Common interruptions:
- "What does this file do?"
- "Why was this refactored?"
- "Which files should I read next?"

ContextWeave answers these questions automatically, freeing senior developers to focus on architecture and mentoring.

**Impact:** Reduce interruptions by 50%, improve team productivity.

**3. Builds Mental Models Faster**

Understanding code requires:
- **What:** What does this code do? (syntax, structure)
- **Why:** Why was it built this way? (design decisions, tradeoffs)
- **How:** How does it fit into the system? (related files, dependencies)

ContextWeave provides all three in one view, helping developers build accurate mental models quickly.

**Impact:** Developers make fewer mistakes, write more consistent code.

**4. Supports Upskilling**

By explaining design decisions and reasoning, ContextWeave teaches:
- Design patterns (repository, factory, observer)
- Architectural tradeoffs (sync vs async, REST vs GraphQL)
- Best practices (error handling, performance optimization)

**Impact:** Junior developers learn professional practices faster, become more valuable to their teams.

**5. Democratizes Access to Knowledge**

In many Indian companies:
- Knowledge is concentrated in 1-2 senior developers
- Documentation is sparse or outdated
- Onboarding is informal and inconsistent

ContextWeave makes codebase knowledge accessible to everyone, regardless of seniority or access to mentors.

**Impact:** More equitable learning opportunities, especially for developers in smaller cities or companies.

### Why This Matters for India

**Scale of Opportunity:**
- India has 5+ million software developers
- 300,000+ new CS graduates per year
- Many join service companies with large, legacy codebases
- Onboarding is a major bottleneck for productivity

**Economic Impact:**
- Faster onboarding → developers productive 2-3 weeks sooner
- Reduced senior dev burden → more time for innovation
- Better code quality → fewer bugs, lower maintenance costs

**Social Impact:**
- Empowers developers from Tier-2/3 colleges (often underestimated)
- Reduces dependency on expensive bootcamps or mentors
- Supports self-taught developers and career switchers

### Alignment with AI for Bharat Theme

**Learning:**
- ContextWeave is fundamentally a learning tool, not just a productivity tool
- Teaches "why" and "how", not just "what"
- Adapts explanations for junior developers and students

**Developer Productivity:**
- Reduces time spent understanding code by 10x
- Eliminates repetitive questions to senior developers
- Enables faster, more confident decision-making

**Meaningful AI Use:**
- AI interprets natural language (commit messages)
- AI reasons about design decisions (synthesis across commits)
- AI explains code semantically (not just syntax)
- Without AI, the product loses its core value

**Responsible Design:**
- Shows sources (commit hashes)
- Labels AI output clearly
- Handles uncertainty gracefully
- Respects privacy (no long-term storage)


## Trade-offs & Limitations

### Scope Limitations (By Design)

**Single-Repo Focus**
- **Limitation:** Only analyzes one Git repository at a time
- **Rationale:** Simplifies MVP, avoids complexity of cross-repo dependencies
- **Impact:** Users working on microservices or monorepos need to analyze each repo separately
- **Future:** Could support multi-repo context in v2

**File-Level Analysis**
- **Limitation:** Analyzes individual files, not system-wide architecture
- **Rationale:** Keeps scope manageable, aligns with "understand this file" use case
- **Impact:** Doesn't show how multiple files interact to implement a feature
- **Future:** Could add "feature flow" analysis (trace request through multiple files)

**Simple Related Files Heuristic**
- **Limitation:** Uses imports + co-change frequency, not deep semantic analysis
- **Rationale:** Deterministic heuristics are fast and predictable; AI adds explanations
- **Impact:** May miss conceptual relationships (e.g., two files that solve similar problems but don't import each other)
- **Future:** Could use embeddings to find semantically similar files

**No Real-Time Collaboration**
- **Limitation:** Single-user tool, no team features (shared annotations, discussions)
- **Rationale:** MVP focuses on individual learning, not team workflows
- **Impact:** Teams can't collaboratively build knowledge base
- **Future:** Could add team features (shared insights, annotations)

### Technical Trade-offs

**Latency vs Cost**

| Approach | Latency | Cost | Quality |
|----------|---------|------|---------|
| No caching | 8-10s | High | High |
| 5-min cache | 0-10s | Medium | High |
| 1-hour cache | 0-10s | Low | Medium (stale) |

**Decision:** 5-minute cache balances freshness and cost.

**Commit Limit (50 commits)**
- **Trade-off:** More commits = better context but higher latency and cost
- **Decision:** 50 commits covers ~6 months of active development for most files
- **Impact:** Very old design decisions (> 6 months) may be missed
- **Mitigation:** Users can increase limit in settings (up to 100)

**LLM Model Selection**

| Model | Cost | Latency | Quality |
|-------|------|---------|---------|
| GPT-4 | High | 3-5s | Excellent |
| GPT-3.5-turbo | Low | 1-2s | Good |
| Claude 3 | Medium | 2-4s | Excellent |

**Decision:** Default to GPT-3.5-turbo for cost, allow GPT-4 for complex files.

**Token Limits**
- **Limitation:** LLMs have token limits (8k-32k tokens)
- **Impact:** Very large files (> 10,000 lines) must be truncated
- **Mitigation:** Truncate to first 8,000 tokens, add note: "File truncated for analysis"

### Known Limitations

**Commit Message Quality**
- **Problem:** If commit messages are uninformative ("fix", "update"), AI can't extract meaningful decisions
- **Mitigation:** System detects sparse messages, shows "Limited commit context available"
- **Impact:** Users still get file summary (from code), just not historical context

**Language Support**
- **Problem:** AI works best with popular languages (Python, JavaScript, Java)
- **Impact:** Less common languages (Rust, Elixir) may get lower-quality summaries
- **Mitigation:** Focus MVP on top 5 languages, expand later

**Binary Files**
- **Problem:** Can't analyze images, PDFs, compiled binaries
- **Mitigation:** Detect binary files, show "Not supported" message

**New Files (No History)**
- **Problem:** Files with < 5 commits have limited historical context
- **Mitigation:** Still provide summary from code, skip design decisions section

**Hallucination Risk**
- **Problem:** LLMs may invent plausible-sounding but incorrect information
- **Mitigation:** 
  - Ground all claims in actual commits (require citations)
  - Show confidence scores
  - Encourage users to verify with source code

### Performance Considerations

**Backend Scalability**
- **Current:** Single FastAPI instance, in-memory cache
- **Limitation:** Can handle ~10 concurrent users
- **Future:** Add Redis cache, horizontal scaling for production

**VS Code Extension Performance**
- **Current:** Synchronous API calls block UI briefly
- **Limitation:** Large files (> 5000 lines) may cause 10+ second delays
- **Future:** Add streaming responses, show incremental results

**LLM API Rate Limits**
- **Problem:** OpenAI free tier: 3 requests/min, paid tier: 60 requests/min
- **Impact:** Multiple users or rapid file switching may hit limits
- **Mitigation:** Cache aggressively, show rate limit errors clearly


## Future Extensions

### Near-Term Enhancements (v1.1 - v1.3)

**1. Multi-Language UI**
- Add Hindi, Tamil, Telugu translations for UI
- LLM can generate explanations in regional languages
- **Impact:** Accessible to non-English-speaking developers in India

**2. Improved Related Files**
- Use code embeddings (e.g., OpenAI embeddings) to find semantically similar files
- Analyze call graphs (which functions call which)
- **Impact:** Better recommendations, especially for large codebases

**3. "Explain This Function"**
- Right-click a function → get focused explanation
- Show callers and callees
- **Impact:** More granular analysis for debugging

**4. Commit Timeline View**
- Visualize how file evolved over time (timeline of major changes)
- Show which developers contributed most
- **Impact:** Better understanding of file history

**5. Offline Mode**
- Cache LLM responses for 24 hours
- Allow analysis without internet (using cached data)
- **Impact:** Works in low-connectivity environments

### Medium-Term Enhancements (v2.0)

**6. Multi-Repo Context**
- Analyze dependencies across multiple repositories
- Show how microservices interact
- **Impact:** Essential for microservices architectures

**7. Chat Interface**
- Ask follow-up questions: "Why was async chosen over sync?"
- Conversational exploration of codebase
- **Impact:** More natural learning experience

**8. Team Features**
- Share insights with team (annotations, comments)
- Collaborative knowledge base
- **Impact:** Builds institutional knowledge

**9. Integration with Issue Trackers**
- Link design decisions to Jira tickets or GitHub issues
- Show "this change fixed bug #123"
- **Impact:** Better traceability

**10. Custom Prompts**
- Allow users to define custom analysis prompts
- Example: "Identify security vulnerabilities" or "Find performance bottlenecks"
- **Impact:** Flexible tool for different use cases

### Long-Term Vision (v3.0+)

**11. Proactive Insights**
- Automatically analyze files when opened (background)
- Suggest related files as you code
- **Impact:** Zero-friction learning

**12. Code Review Assistant**
- Analyze PRs, explain changes in plain language
- Suggest reviewers based on file history
- **Impact:** Faster, more thorough code reviews

**13. Onboarding Workflows**
- Generate personalized learning paths for new hires
- "Read these 10 files to understand the payment system"
- **Impact:** Structured onboarding experience

**14. Architecture Visualization**
- Generate diagrams showing how files/modules interact
- Visual representation of system architecture
- **Impact:** Better mental models for visual learners

**15. Fine-Tuned Models**
- Train custom models on company-specific codebases
- Better understanding of domain-specific patterns
- **Impact:** Higher quality insights for specialized domains

### Deployment & Infrastructure

**Current (MVP):**
- Backend: Local (`uvicorn main:app`)
- LLM: OpenAI API (user-provided key)
- Cache: In-memory (Python dict)

**Near-Term:**
- Backend: AWS EC2 (t3.small) or Lightsail
- LLM: AWS Bedrock (Claude or Titan) for data residency
- Cache: Redis (ElastiCache)

**Long-Term:**
- Backend: Kubernetes cluster (auto-scaling)
- LLM: Mix of cloud APIs and self-hosted models
- Cache: Distributed cache (Redis Cluster)
- Storage: PostgreSQL for persistent insights

### Success Metrics

**MVP (v1.0):**
- 50+ active users (developers, students)
- 80% of summaries rated "helpful" or "very helpful"
- 50% reduction in "why" questions to senior developers
- 5-10x faster file comprehension (measured by user surveys)

**v2.0:**
- 500+ active users
- 10+ companies using for onboarding
- Integration with 3+ popular IDEs (VS Code, IntelliJ, Vim)

**v3.0:**
- 5,000+ active users
- Enterprise customers (BFSI, service companies)
- Measurable impact on onboarding time (2-3 weeks faster)

---

## Appendix: Technology Stack Summary

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI (async web framework)
- **Git Integration:** GitPython (Git operations)
- **LLM Client:** OpenAI Python SDK or AWS Boto3 (Bedrock)
- **Validation:** Pydantic (data models)
- **Caching:** In-memory dict (MVP), Redis (production)
- **Deployment:** Uvicorn (ASGI server), Docker (containerization)

### Frontend (VS Code Extension)
- **Language:** TypeScript
- **Framework:** VS Code Extension API
- **UI:** Webview API (HTML/CSS/JS)
- **HTTP Client:** Fetch API or Axios
- **Build:** Webpack or esbuild
- **Package:** vsce (VS Code extension packager)

### Infrastructure (Optional)
- **Compute:** AWS EC2 (t3.small) or Lightsail
- **LLM:** AWS Bedrock (Claude 3 or Titan)
- **Cache:** AWS ElastiCache (Redis)
- **Monitoring:** CloudWatch (logs, metrics)

### Development Tools
- **AI Assistants:** Kiro (requirements, design), GitHub Copilot (code generation)
- **Version Control:** Git + GitHub
- **Testing:** pytest (backend), Jest (extension)
- **Linting:** mypy (Python), ESLint (TypeScript)

---

## Document Metadata

**Generated by:** Kiro AI Assistant  
**Date:** February 7, 2026  
**Version:** 1.0 (MVP Design)  
**Theme:** AI for Bharat – Learning & Developer Productivity  
**Target Users:** Indian developers (students, freshers, junior engineers)

**Related Documents:**
- `requirements.md` - Product requirements and user stories
- `README.md` - Setup and usage instructions (to be created)
- `ARCHITECTURE.md` - Detailed technical architecture (to be created)

**Review Status:** Draft (pending technical review)

