# ContextWeave Lite - Requirements Document

**Version:** 0.1.0 (MVP)  
**Track:** AI for Bharat – AI for Learning & Developer Productivity  
**Target:** Demo-ready hackathon submission

---

## Overview

ContextWeave Lite is an AI-powered VS Code extension that helps Indian students and junior developers understand large, poorly documented codebases by analyzing code and Git history to generate clear, human-readable explanations.

**Core Capability:** For any file in a Git repository, provide:
- 2-3 sentence summary of what the file does
- 2-3 key design decisions extracted from Git history (with commit evidence)
- 2-3 related files to read next
- Optional explanation of selected "weird" code

**Architecture:** VS Code extension (TypeScript) + FastAPI backend (Python) + LLM API (Groq/OpenAI)

---

## Problem Statement

### Context: Developer Productivity Crisis in India

**Target Users:**
- **Students** from Tier-2/Tier-3 colleges learning from real-world GitHub projects
- **New graduates** joining Indian companies (BFSI, govtech, startups, service firms)
- **Junior developers** (0-2 years) maintaining legacy systems in understaffed teams

**The Pain:**

Indian developers face a unique challenge: massive, poorly documented codebases with minimal institutional knowledge.

1. **Documentation Gap**
   - Legacy codebases have no README, outdated wikis, or missing design docs
   - "Documentation" is often just the code itself
   - Critical context exists only in senior developers' heads

2. **Knowledge Concentration**
   - 1-2 senior developers hold all context for a 50,000+ line codebase
   - Seniors are overloaded and can't answer every "why" question
   - New hires spend weeks just understanding basic file structure

3. **Git History is Noisy**
   - Commit messages like "fix", "update", "wip" provide no context
   - Design decisions are buried across 100+ commits
   - No one has time to manually trace history

4. **Slow Onboarding**
   - New developers take 4-6 weeks to become productive
   - Students can't learn from real projects because they're too opaque
   - Junior devs are afraid to touch code they don't understand

**Real-World Impact:**
- A new grad at a Bangalore BFSI company spends 3 days understanding a single payment processing file
- A student trying to contribute to an open-source project gives up because they can't understand the codebase structure
- A junior dev at a service company breaks production because they didn't understand why a "weird" code pattern existed

---

## Why AI is Essential (Not Just Convenient)

### What Rules Can Do (Deterministic Analysis)
✅ Extract commit history from Git  
✅ Parse import statements  
✅ Count lines changed in diffs  
✅ Find files that change together  
✅ Collect structured data  

### What Rules Cannot Do (Requires AI)
❌ **Interpret natural language** commit messages ("refactored for perf" vs "made it faster" vs "fixed blocking issue")  
❌ **Synthesize patterns** across multiple commits (e.g., "gradual migration from sync to async over 8 commits")  
❌ **Infer intent and tradeoffs** (why was async chosen? what problem did it solve?)  
❌ **Explain code semantically** ("this is a repository pattern" requires understanding design patterns)  
❌ **Generate human-readable explanations** adapted for junior developers  

**Without AI:** ContextWeave becomes a commit browser that shows raw data. The core value—building mental models quickly—disappears.

**With AI:** ContextWeave interprets noisy history, reasons about design decisions, and generates clear explanations that help developers learn 5-10x faster.

---

## Goals & Non-Goals

### Goals (MVP v0.1.0)
✅ **Demo-ready end-to-end system** that works on real Git repositories  
✅ **Meaningful AI use** that demonstrates reasoning, not just keyword matching  
✅ **Clear value for Indian students/devs** learning unfamiliar codebases  
✅ **Responsible AI design** with source attribution and uncertainty handling  
✅ **5-second comprehension** UI that's instantly useful  
✅ **AI-assisted development** using Kiro for requirements, design, and docs  

### Non-Goals (Out of Scope for MVP)
❌ Multi-repo or monorepo support (single repo at a time)  
❌ Enterprise features (auth, teams, permissions, cloud storage)  
❌ Real-time collaboration or shared annotations  
❌ Complex architectural analysis across multiple files  
❌ Fine-tuned or self-hosted models (use external APIs)  
❌ Production-grade deployment infrastructure  

---

## User Personas

### Persona 1: Priya - Computer Science Student
**Background:**
- 3rd year B.Tech student at a Tier-2 college in Pune
- Learning web development from YouTube and GitHub projects
- Wants to contribute to open-source but finds codebases overwhelming

**Pain Points:**
- Opens a React project with 200+ files and doesn't know where to start
- Spends hours reading code without understanding the "why"
- Gives up on contributing because she can't understand the architecture

**How ContextWeave Helps:**
- Right-clicks any file → instantly sees what it does
- Understands design decisions from Git history
- Gets suggestions for related files to build mental model

**Success Metric:** Reduces time to understand a file from 30 minutes to 3 minutes

---

### Persona 2: Arjun - New Graduate Engineer
**Background:**
- 22 years old, just joined a BFSI company in Bangalore
- Assigned to a 5-year-old banking application (Java/Spring Boot)
- Team has 1 senior developer who's always busy

**Pain Points:**
- Needs to fix a bug in payment processing but doesn't understand the code
- Afraid to ask senior dev too many questions
- Spends 3 days reading code and Git history manually

**How ContextWeave Helps:**
- Analyzes payment processing file → sees it handles transaction validation
- Learns from Git history that async/await was added for performance
- Discovers related files (PaymentRepository, PaymentConfig) to read next

**Success Metric:** Reduces onboarding time from 6 weeks to 3 weeks

---

### Persona 3: Sneha - Junior Developer
**Background:**
- 1 year experience at a Hyderabad startup
- Inherited a Node.js microservice from a developer who left
- Sparse documentation, inconsistent commit messages

**Pain Points:**
- Sees "weird" code patterns but doesn't know why they exist
- Worried about breaking things by refactoring
- No one to ask because original author is gone

**How ContextWeave Helps:**
- Selects weird code → gets explanation from Git history
- Learns it's a workaround for a legacy API issue
- Gains confidence to maintain and improve the code

**Success Metric:** Reduces "why" questions to senior devs by 50%

---

## User Stories

### Story 1: Quick File Understanding
**As a** new graduate joining a large BFSI codebase  
**I want to** right-click a Java file and instantly see what it does  
**So that** I can quickly decide if it's relevant to my bug fix without reading 500 lines of code

**Acceptance Criteria:**
- Command appears in VS Code context menu
- Sidebar opens within 2 seconds
- Summary is 2-3 sentences in simple language
- No jargon or assumptions about prior knowledge

---

### Story 2: Design Decision Discovery
**As a** junior developer maintaining a legacy service  
**I want to** see key design decisions extracted from Git history  
**So that** I understand why the code evolved this way and don't accidentally break important patterns

**Acceptance Criteria:**
- Shows 2-3 design decisions with titles and descriptions
- Each decision cites commit hashes as evidence
- Commit hashes are clickable (open in Git history)
- Admits when commit history is too sparse

---

### Story 3: Related File Navigation
**As a** student exploring an open-source project  
**I want to** see which files I should read next  
**So that** I can build a mental model of the system without randomly browsing

**Acceptance Criteria:**
- Shows 2-3 related files with explanations
- Explanations are in simple language (e.g., "This service calls UserRepository for database access")
- File paths are clickable (open in editor)
- Based on imports and co-change patterns

---

### Story 4: Code Pattern Explanation
**As a** developer seeing unfamiliar code  
**I want to** select a "weird" code block and get an explanation  
**So that** I understand why it exists before modifying it

**Acceptance Criteria:**
- Can select 5-10 lines of code
- Run command to get explanation
- Explanation references Git history if available
- Admits when no clear explanation exists

---

### Story 5: Trust Through Transparency
**As a** user of AI tools  
**I want to** see which commits were used as evidence  
**So that** I can verify claims and dig deeper if needed

**Acceptance Criteria:**
- All AI output is labeled "AI-generated"
- Commit hashes are shown and clickable
- Metadata shows how many commits were analyzed
- Disclaimer about potential incompleteness

---

### Story 6: Works Without Friction
**As a** developer with limited English proficiency  
**I want** explanations in simple, clear language  
**So that** I can understand even if I'm still learning technical terminology

**Acceptance Criteria:**
- Avoids jargon where possible
- Uses short sentences
- Explains concepts in plain language
- Suitable for junior developers

---

## Functional Requirements

### Backend (FastAPI + Python 3.11)

#### FR-1: Health Check Endpoint
**Endpoint:** `GET /health`

**Purpose:** Verify backend is running and LLM is configured

**Response:**
```json
{
  "status": "healthy",
  "llm_configured": true,
  "version": "0.1.0"
}
```

**Requirements:**
- Returns 200 OK if backend is operational
- `llm_configured` is `true` if `LLM_API_KEY` is set, `false` otherwise
- No authentication required

---

#### FR-2: File Analysis Endpoint
**Endpoint:** `POST /context/file`

**Purpose:** Analyze a file and return AI-powered context

**Request Body:**
```json
{
  "repo_path": "/absolute/path/to/repo",
  "file_path": "/absolute/path/to/file.py",
  "selected_code": "optional code snippet or null",
  "commit_limit": 50
}
```

**Response Body:**
```json
{
  "summary": "2-3 sentence summary",
  "decisions": [
    {
      "title": "Short title",
      "description": "One-line explanation",
      "commits": ["abc123", "def456"]
    }
  ],
  "related_files": [
    {
      "path": "relative/path/to/file.py",
      "reason": "Why this file is related"
    }
  ],
  "weird_code_explanation": "Explanation or null",
  "metadata": {
    "commits_analyzed": 47,
    "llm_model": "llama-3.1-8b-instant",
    "has_commit_history": true
  }
}
```

**Requirements:**
- Validate that `repo_path` is a valid Git repository
- Validate that `file_path` exists and is tracked by Git
- Extract last N commits (up to `commit_limit`) that touched the file
- Read current file content from disk
- Compute related files (imports + co-changed files)
- Call LLM API with structured prompt
- Parse LLM response into JSON
- Return 400 if inputs are invalid
- Return 500 if Git or LLM fails
- Include error messages in response

---

#### FR-3: Git History Extraction
**Purpose:** Collect structured data from Git (deterministic, no AI)

**Requirements:**
- Use GitPython to query commit history
- For each commit, extract:
  - Short hash (7 chars)
  - Full hash
  - Author name
  - Commit date (ISO format)
  - Commit message (full text)
  - Lines changed (rough count from diff)
- Sort commits by recency (most recent first)
- Limit to `commit_limit` commits (default 50, max 100)
- Handle edge cases:
  - File has no commits → return empty list
  - File is new (not committed) → return empty list
  - Binary file → skip diff analysis

---

#### FR-4: Related Files Computation
**Purpose:** Find files a developer should read next (deterministic, no AI)

**Requirements:**
- **Import Detection:**
  - Parse Python imports: `import X`, `from Y import Z`
  - Parse JavaScript imports: `import X from 'Y'`, `require('Y')`
  - Parse Java imports: `import com.example.X;`
  - Return list of imported file paths (relative to repo root)
- **Co-Change Detection:**
  - Query last 100 commits that touched the target file
  - For each commit, get list of all files changed
  - Count how often each file appears with target file
  - Return top 5 files by co-change frequency
- **Ranking:**
  - Combine imports and co-changed files
  - Prioritize imports (score 10) over co-changes (score = frequency)
  - Return top 3 files overall

---

#### FR-5: LLM Integration
**Purpose:** Call external LLM API to generate explanations (AI-powered)

**Requirements:**
- **Configuration (from `.env`):**
  - `LLM_API_KEY` - API key (required for full mode)
  - `LLM_API_BASE` - API endpoint (e.g., `https://api.groq.com/openai/v1`)
  - `LLM_MODEL` - Model name (e.g., `llama-3.1-8b-instant`)
- **Prompt Construction:**
  - Include file path and content (truncated to 6000 chars if needed)
  - Include last 20 commits (messages + dates + lines changed)
  - Include related files data (imports + co-changes)
  - Include selected code if provided
  - Request JSON output with specific schema
  - Emphasize: simple language, cite commits, admit uncertainty
- **API Call:**
  - Use OpenAI-compatible chat completions endpoint
  - Temperature: 0.3 (low creativity, high consistency)
  - Max tokens: 1500
  - Timeout: 30 seconds
- **Response Parsing:**
  - Extract JSON from response (handle markdown code blocks)
  - Validate against expected schema
  - Fall back to mock response if parsing fails
- **Error Handling:**
  - 400/401 → Invalid API key
  - 429 → Rate limit exceeded
  - 500/503 → LLM service error
  - Timeout → Network issue
  - All errors → Fall back to mock mode with warning

---

#### FR-6: Mock Mode
**Purpose:** Provide deterministic responses when LLM is not configured

**Requirements:**
- Activate when `LLM_API_KEY` is not set or LLM call fails
- Generate response using only deterministic data:
  - Summary: Generic description mentioning file name and commit count
  - Decisions: First 2 commit messages as-is
  - Related files: Top 3 from imports/co-changes
  - Weird code explanation: "Configure LLM_API_KEY for AI analysis"
- Include metadata: `"mock_response": true`
- Log warning: "Creating mock response (LLM not configured)"

---

#### FR-7: Error Handling
**Purpose:** Provide clear, actionable error messages

**Requirements:**
- **400 Bad Request:**
  - File not found
  - Not a Git repository
  - Invalid input format
- **500 Internal Server Error:**
  - Git operation failed
  - File read failed
  - Unexpected exception
- **Error Response Format:**
```json
{
  "detail": "Human-readable error message",
  "error_type": "git_error" | "file_error" | "llm_error",
  "suggestions": ["Try this", "Or this"]
}
```

---

### VS Code Extension (TypeScript)

#### FR-8: Command Registration
**Command:** `contextweave.explainFile`  
**Label:** "ContextWeave: Explain this file"

**Requirements:**
- Appears in Command Palette (`Ctrl+Shift+P`)
- Appears in file explorer context menu (right-click)
- Appears in editor context menu (right-click)
- Only enabled when a file is open
- Only enabled when file is in a workspace

---

#### FR-9: Workspace Detection
**Purpose:** Find Git repository root

**Requirements:**
- Use VS Code Git extension API to find repo
- Detect workspace folder containing current file
- Validate that workspace is a Git repository
- Show error if file is not in a Git repo
- Show error if file is not in a workspace

---

#### FR-10: Backend Communication
**Purpose:** Call FastAPI backend

**Requirements:**
- **Configuration (from VS Code settings):**
  - `contextweave.backendUrl` - Backend URL (default: `http://localhost:8000`)
  - `contextweave.commitLimit` - Max commits (default: 50, range: 1-100)
- **Request Construction:**
  - Get absolute path to repo root
  - Get absolute path to current file
  - Get selected text (if any)
  - Build JSON request body
- **HTTP Call:**
  - POST to `{backendUrl}/context/file`
  - Content-Type: `application/json`
  - Timeout: 30 seconds
- **Error Handling:**
  - ECONNREFUSED → Backend not running
  - 400 → Invalid request (show backend error message)
  - 500 → Backend error (show backend error message)
  - Timeout → Network issue
  - All errors → Show user-friendly message in sidebar

---

#### FR-11: Sidebar UI
**Purpose:** Display analysis results

**Requirements:**
- **Layout:**
  - Section 1: "📄 What this file does" (summary)
  - Section 2: "🔍 Key design decisions" (list)
  - Section 3: "📚 You should also read" (list)
  - Section 4: "🤔 Selected Code Explanation" (if selected_code provided)
  - Footer: Metadata (commits analyzed, model, confidence)
- **Styling:**
  - Use VS Code theme colors
  - Clear visual hierarchy
  - Readable font sizes
  - Proper spacing
- **Interactivity:**
  - Commit hashes are clickable → open Git history
  - Related file paths are clickable → open in editor
  - Collapsible sections (optional)
- **States:**
  - Loading: Show spinner + "Analyzing file..."
  - Success: Show results
  - Error: Show error message + suggestions
  - Empty: Show "Open a file and run the command"

---

#### FR-12: AI Output Labeling
**Purpose:** Responsible AI transparency

**Requirements:**
- All AI-generated content has "✨ AI-generated" badge
- Mock responses show warning: "⚠️ Mock Response: LLM not configured"
- Footer shows: "AI-generated insights may be incomplete. Always verify with source code."
- Metadata shows which model was used
- Metadata shows how many commits were analyzed

---

#### FR-13: Source Attribution
**Purpose:** Show evidence for AI claims

**Requirements:**
- Each design decision lists commit hashes
- Commit hashes are clickable (open in Git view)
- Footer shows date range of commits analyzed
- Related files show reason for relationship

---

## Non-Functional Requirements

### NFR-1: Latency
**Requirement:** Analysis completes in < 15 seconds for typical files

**Rationale:** Interactive use requires fast feedback

**Measurement:**
- Backend processing: < 10 seconds
- Network round-trip: < 2 seconds
- UI rendering: < 1 second

**Optimization:**
- Truncate large files to 6000 chars
- Limit commits to 50 by default
- Use fast LLM model (e.g., llama-3.1-8b-instant)
- Show progress indicator during analysis

---

### NFR-2: Usability (5-Second Comprehension Rule)
**Requirement:** User understands results within 5 seconds of viewing sidebar

**Rationale:** Developers need quick context, not essays

**Design Principles:**
- Clear section headings with icons
- 2-3 sentences max for summary
- Bullet points for decisions and related files
- No jargon or complex terminology
- Visual hierarchy (bold, spacing, colors)

---

### NFR-3: Reliability
**Requirement:** System handles edge cases gracefully without crashes

**Edge Cases:**
- Empty file → Show "File is empty"
- No commit history → Show "No Git history available"
- Binary file → Show "Binary files not supported"
- Very large file (> 10,000 lines) → Truncate with note
- LLM timeout → Fall back to mock mode
- Invalid API key → Show clear error message

---

### NFR-4: Responsible AI

#### Transparency
- All AI output is clearly labeled
- Sources (commits) are always shown
- Model name is displayed in metadata

#### Uncertainty Handling
- When commit history is sparse (< 5 commits): "Limited commit history available"
- When commit messages are brief: "Commit messages are brief; analysis may be incomplete"
- When LLM confidence is low: Show warning

#### No Hallucination
- All claims must be grounded in actual commits or code
- Never invent commit hashes or file names
- Admit when evidence is insufficient

#### Privacy
- Code is sent to LLM API only for analysis (not training)
- No long-term storage of code (5-minute cache only)
- User provides their own API key (no shared keys)
- Warn users about sending proprietary code to cloud APIs

---

### NFR-5: Configuration Security
**Requirement:** API keys are never hardcoded or committed to Git

**Implementation:**
- Backend loads `LLM_API_KEY` from `.env` file
- `.env` is in `.gitignore`
- `.env.example` provided as template (no real keys)
- Documentation emphasizes: "Never commit API keys"
- Health endpoint shows `llm_configured: true/false` but never exposes key

---

## AI Requirements

### AI-1: Where AI is Used

| Task | Deterministic (Rules) | AI-Powered (LLM) |
|------|----------------------|------------------|
| Extract commit history | ✅ GitPython | ❌ |
| Parse imports | ✅ Regex/AST | ❌ |
| Find co-changed files | ✅ Git log analysis | ❌ |
| **Summarize file purpose** | ❌ | ✅ Semantic understanding |
| **Interpret commit messages** | ❌ | ✅ Natural language processing |
| **Infer design decisions** | ❌ | ✅ Reasoning across commits |
| **Explain code patterns** | ❌ | ✅ Semantic code understanding |
| **Generate human-readable text** | ❌ | ✅ Natural language generation |

---

### AI-2: Why AI is Required

#### Task: File Summarization
**Input:** File content (code)  
**Output:** 2-3 sentence summary

**Why AI:**
- Understands code semantics across languages and frameworks
- Identifies main responsibilities even without docstrings
- Adapts explanation style for junior developers
- Handles novel code structures not seen in training

**Why Not Rules:**
- Would need language-specific parsers for every language
- Would need hardcoded templates for every design pattern
- Cannot handle new patterns or frameworks
- Cannot adapt tone for audience

**Example:**
- **Code:** 200 lines of Java Spring Boot controller
- **Rule-based:** "This is a Java file with 5 methods"
- **AI-powered:** "This controller handles user authentication endpoints, validates JWT tokens, and manages session state for the web application"

---

#### Task: Design Decision Extraction
**Input:** List of commits (messages + diffs)  
**Output:** 2-3 key decisions with reasoning

**Why AI:**
- Interprets unstructured natural language commit messages
- Synthesizes patterns across multiple commits (e.g., "gradual migration over 8 commits")
- Infers intent even when messages are brief ("perf fix" → "improved performance by...")
- Understands code changes semantically, not just line diffs

**Why Not Rules:**
- Commit messages have infinite variation
- No standard format or vocabulary
- Regex patterns would miss 90% of meaningful decisions
- Cannot reason about "why" from "what"

**Example:**
- **Commits:** 
  - "async refactor" (50 lines changed)
  - "update callers" (30 lines changed)
  - "remove old sync code" (20 lines changed)
- **Rule-based:** Shows 3 separate commits
- **AI-powered:** "Migrated from synchronous to asynchronous processing to improve API response time and handle concurrent requests"

---

#### Task: Related File Recommendation
**Input:** Imports + co-changed files  
**Output:** 2-3 files with explanations

**Why AI:**
- Understands conceptual relationships beyond imports
- Ranks by relevance for learning (not just technical coupling)
- Generates natural explanations ("This service calls UserRepository for database access")
- Filters out false positives (files changed together for unrelated reasons)

**Why Not Rules:**
- Static analysis finds imports but misses semantic relationships
- Co-change analysis produces false positives
- Cannot explain "why" files are related
- Cannot rank by learning value

**Example:**
- **Imports:** `UserRepository`, `Logger`, `Config`
- **Co-changed:** `UserService`, `AuthMiddleware`, `database.sql`
- **Rule-based:** Lists all 6 files
- **AI-powered:** 
  1. "UserRepository - This service calls it for database access"
  2. "AuthMiddleware - Both handle user authentication"
  3. "UserService - Tests this controller's endpoints"

---

### AI-3: Prompt Engineering Strategy

#### Principle 1: Structured Prompts
- Clear role definition: "You are helping a junior developer..."
- Explicit task breakdown: "1. Summarize... 2. Extract decisions... 3. Suggest files..."
- Output format specification: "Output JSON only, no markdown"

#### Principle 2: Source Grounding
- Provide all evidence in prompt (commits, code, imports)
- Instruct: "Base your answer only on the provided commits"
- Request citations: "Reference commit hashes for each decision"

#### Principle 3: Uncertainty Handling
- Instruct: "If commit messages are unclear, say 'Limited commit context available'"
- Instruct: "Never invent information not present in commits"
- Request confidence scores: "Assess your confidence: high/medium/low"

#### Principle 4: Audience Adaptation
- Specify: "Use simple language suitable for junior developers"
- Specify: "Avoid jargon where possible"
- Specify: "Explain concepts in plain language"

#### Example Prompt Structure:
```
You are helping a junior developer in India understand a codebase.

FILE: src/services/PaymentService.java
CONTENT: [file content]

RECENT COMMITS:
- abc123 (2024-01-15): "Refactored to use async/await"
- def456 (2024-02-20): "Added retry logic"

TASKS:
1. Summarize what this file does (2-3 sentences, simple language)
2. Extract 2-3 key design decisions (cite commit hashes)
3. Suggest 2-3 related files (explain why)

IMPORTANT:
- Be concise and clear
- Admit uncertainty when evidence is weak
- Reference actual commit hashes

OUTPUT JSON:
{
  "summary": "...",
  "decisions": [...],
  "related_files": [...]
}
```

---

### AI-4: Model Selection

**Current:** Groq llama-3.1-8b-instant

**Rationale:**
- Fast (< 2 seconds response time)
- Good code understanding
- Free tier with generous limits
- OpenAI-compatible API

**Alternatives:**
- OpenAI GPT-3.5-turbo (slower, costs money, better quality)
- OpenAI GPT-4 (much slower, expensive, best quality)
- AWS Bedrock Claude (enterprise, data residency)

**Configuration:** Via `.env` file, easy to swap models

---

## Constraints & Assumptions

### Constraints
- **Single Repository:** MVP analyzes one Git repo at a time
- **Local Git Clone:** Repository must be cloned locally (no remote Git API)
- **File-Level Analysis:** No cross-file architectural analysis
- **External LLM:** Requires internet and API key (or mock mode)
- **Text Files Only:** Binary files not supported
- **Token Limits:** Very large files (> 10,000 lines) are truncated

### Assumptions
- Target repositories have meaningful commit history (50+ commits)
- Commit messages are in English (or transliterated)
- Users have VS Code installed and can install extensions
- Backend runs locally or on accessible server
- LLM API is available and responsive (< 5 seconds)
- Users are comfortable with basic Git concepts

### Out of Scope (MVP)
- Multi-repo or monorepo support
- Real-time collaboration features
- Persistent storage or databases
- Authentication or user management
- Fine-tuned or self-hosted models
- Support for non-Git version control
- Multi-language UI (English only for MVP)

---

## Success Criteria

### Technical Success (MVP)
✅ Backend starts without errors  
✅ Extension loads in VS Code  
✅ Command appears in Command Palette  
✅ Analysis completes in < 15 seconds  
✅ Results display in sidebar  
✅ Commit hashes are clickable  
✅ Related files are clickable  
✅ Error messages are clear  
✅ Works in mock mode (no API key)  
✅ Works with real LLM (with API key)  

### User Success (Validation)
- **Accuracy:** 80%+ of summaries are helpful (manual review)
- **Speed:** 5-10x faster than manual analysis (user survey)
- **Adoption:** 5+ developers from target segment report value
- **Learning:** Users understand files they couldn't before

### Hackathon Success (Judging)
- **AI Justification:** Judges understand why AI is essential
- **India Impact:** Clear value for Indian students/devs
- **Responsible AI:** Transparent, sourced, uncertainty-aware
- **Demo Quality:** Works reliably during presentation
- **Documentation:** Clear, comprehensive, well-organized

---

## Development Approach

### AI-Assisted Development
- **Kiro:** Used to generate requirements, design, and documentation
- **LLMs:** Used to generate boilerplate code (FastAPI routes, TypeScript interfaces)
- **Copilot:** Used for code completion and test generation
- **Transparency:** All AI assistance documented in README

### Iteration Strategy
1. Backend core (Git analysis + mock mode)
2. LLM integration (prompt engineering)
3. VS Code extension (UI + commands)
4. Error handling and edge cases
5. Documentation and polish
6. User testing with target segment

---

**Document Version:** 1.0  
**Last Updated:** February 7, 2026  
**Status:** Ready for Implementation
