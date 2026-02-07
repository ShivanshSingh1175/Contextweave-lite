# ContextWeave Lite - Requirements Document

## Overview

ContextWeave Lite is a developer productivity tool designed to help Indian developers—especially freshers, students, and junior engineers—quickly understand large, poorly documented codebases. The system consists of a FastAPI backend that analyzes code and Git history using AI, plus a VS Code extension that displays insights in a sidebar panel.

**Theme:** AI for Bharat – Learning & Developer Productivity  
**Core Value:** Help developers learn real-world codebases faster and become productive sooner, reducing dependency on overworked senior developers.

**How it works:** For any file in a Git repository, ContextWeave Lite:
1. Summarizes what the file does in 2-3 sentences
2. Extracts key design decisions from Git history (commit messages + diffs)
3. Lists 2-3 related files a new developer should read next

**Technology Stack:**
- Backend: Python 3.11, FastAPI, GitPython, external LLM API (OpenAI/AWS Bedrock)
- Client: VS Code extension (TypeScript)
- Optional: AWS deployment (EC2/Lightsail for backend, Bedrock for inference)
- Development: Requirements and design generated with Kiro AI assistant

## Problem Statement

**Context: Developer Productivity in India**

Developers in India—particularly new graduates from Tier-2/Tier-3 colleges, freshers joining service companies, and junior engineers in startups—face a steep learning curve when working with large, legacy codebases. These codebases are often:
- Poorly documented or have outdated documentation
- Built by teams that have moved on, leaving no institutional knowledge
- Complex, with design decisions buried in years of Git history
- Critical to business operations, requiring quick onboarding

**Current Pain Points:**
- New developers spend weeks or months understanding code structure and intent
- Senior developers are constantly interrupted with "why was this built this way?" questions
- Reading raw commit logs is time-consuming and requires knowing what to look for
- Existing tools (IDE navigation, Git blame) show "what" but not "why"
- Students inheriting college projects or open-source contributions face similar challenges

**Why Existing Solutions Fall Short:**
- Code navigation tools (Go to Definition, Find References) only show structure, not reasoning
- Git history browsers show raw commits but don't synthesize patterns or intent
- Documentation is often missing, outdated, or doesn't explain historical context
- Asking senior developers doesn't scale and creates bottlenecks

**Why AI is Essential (Not Just Convenient):**

Without AI, we can only build a commit browser that shows raw data. AI is required because:

1. **Natural Language Understanding:** Commit messages are unstructured, inconsistent, and written in natural language. AI can interpret varied phrasing ("fixed bug", "refactored for performance", "migrated to async") and extract semantic meaning that rule-based regex patterns would miss.

2. **Cross-Commit Reasoning:** Design decisions often span multiple commits over weeks or months. AI can synthesize patterns (e.g., "gradual migration from sync to async across 8 commits") that would require complex graph analysis and heuristics to detect with rules.

3. **Code Semantics:** AI understands code intent across languages and frameworks. It can explain "this is a repository pattern for database access" without hardcoded templates for every design pattern and language.

4. **Contextual Synthesis:** AI can combine code structure, commit history, and co-change patterns to infer relationships ("this service calls that repository, which uses this config") that go beyond static import analysis.

5. **Human-Readable Explanations:** AI generates natural, accessible summaries tailored to the audience (junior developers) rather than template-based text that sounds robotic.

**If we remove AI:** The product becomes a raw commit viewer with basic file metrics—no reasoning, no synthesis, no learning acceleration. The core value (building mental models quickly) disappears.

## Goals & Non-Goals

### Goals
- **Accelerate Learning:** Help Indian developers (freshers, students, junior engineers) understand unfamiliar codebases 5-10x faster
- **Reduce Senior Dev Burden:** Decrease "why was this built this way?" interruptions by providing self-service context
- **Meaningful AI Use:** Demonstrate AI that interprets, reasons, and synthesizes—not just keyword matching or templates
- **Responsible Design:** Show sources, label AI output, handle uncertainty gracefully
- **Practical MVP:** Deliver a working tool that solves a real problem for a focused user segment
- **AI-Assisted Development:** Use Kiro and LLMs to accelerate requirements, design, and implementation

### Non-Goals
- Multi-repo or monorepo support (single repo at a time for MVP)
- Real-time collaboration or team features
- Authentication, user management, or cloud storage
- Support for non-Git version control (SVN, Mercurial)
- Fine-tuned or self-hosted models (use external APIs)
- Comprehensive language support (focus on Python, JavaScript, Java for MVP)
- Production-grade deployment infrastructure (local/dev deployment is sufficient)

## User Personas

**Primary Persona: Priya, New Graduate Engineer**
- 22 years old, B.Tech from Tier-2 college in Pune
- Just joined a BFSI service company working on a 5-year-old banking application
- Comfortable with Java basics but unfamiliar with Spring Boot, microservices architecture
- Assigned to fix bugs in payment processing module by end of sprint
- Hesitant to constantly ask senior developers who are already overloaded
- Needs to build mental models of code structure and design decisions quickly

**Secondary Persona: Arjun, Junior Developer**
- 1 year experience at a Bangalore startup
- Inherited a Node.js/React codebase from a team that left the company
- Documentation is sparse; commit messages are inconsistent
- Needs to add features but doesn't understand why certain patterns were used
- Wants to learn best practices by understanding historical decisions

**Tertiary Persona: Sneha, Computer Science Student**
- Final year student at Tier-3 college in Jaipur
- Working on a college project inherited from seniors
- Codebase has 50+ files with no README or comments
- Needs to understand what each file does to extend the project
- Limited access to original authors for questions

## User Stories

1. **As a new graduate joining a large BFSI codebase**, I want to right-click a Java file in VS Code and instantly see a 2-3 sentence summary of what it does, so I can quickly decide if it's relevant to my bug fix without reading 500 lines of code.

2. **As a junior developer inheriting a legacy project**, I want to see key design decisions extracted from Git history (e.g., "Refactored to use async/await in commit abc123 to improve performance"), so I understand why the code evolved this way and don't accidentally break important patterns.

3. **As a student working on an inherited college project**, I want to see 2-3 related files I should read next (e.g., "UserService.java calls this repository; see UserController.java for API endpoints"), so I can build a mental model of the system without randomly browsing files.

4. **As a developer learning a new codebase**, I want to see which specific commits and PRs informed the AI's analysis (with clickable hashes), so I can verify claims and dig deeper into the history if needed.

5. **As a user of AI tools**, I want the system to clearly label AI-generated content and admit when commit history is too sparse to extract meaningful decisions, so I trust the tool and don't rely on hallucinated information.

6. **As a fresher with limited English proficiency**, I want explanations in simple, clear language (avoiding jargon where possible), so I can understand the reasoning even if I'm still learning technical terminology.

## Functional Requirements

### Backend (FastAPI + Python)

**FR-1: File Summary Endpoint**
- **Input:** File path (relative to repo root), repo root path
- **Process:**
  - Use GitPython to verify file exists and is tracked
  - Read file content
  - Send to LLM with prompt: "Summarize what this file does in 2-3 sentences for a junior developer"
- **Output:** 2-3 sentence summary in simple, clear language
- **AI Role:** Interpret code semantics, identify main responsibilities, generate human-readable explanation

**FR-2: Design Decisions Endpoint**
- **Input:** File path, repo root path, optional commit limit (default: 50)
- **Process:**
  - Use GitPython to extract commit history for the file (last 50 commits)
  - For each commit: get message, diff, author, date
  - Send structured data to LLM with prompt: "Extract key design decisions from these commits. Focus on architectural changes, refactorings, and reasoning."
- **Output:** List of 2-5 design decisions, each with:
  - Decision description (1-2 sentences)
  - Commit hash(es) as evidence
  - Timestamp
- **AI Role:** Interpret natural language commit messages, synthesize patterns across multiple commits, infer intent from diffs
- **Fallback:** If < 5 commits or no meaningful decisions, return: "Limited commit history available for this file"

**FR-3: Related Files Endpoint**
- **Input:** File path, repo root path
- **Process:**
  - Use GitPython to extract:
    - Files imported/required by this file (static analysis)
    - Files frequently co-changed with this file (Git history)
    - Files in same directory or module
  - Send file content + metadata to LLM with prompt: "Identify 2-3 related files a new developer should read next. Explain the relationship."
- **Output:** List of 2-3 related files, each with:
  - File path
  - Relationship explanation (e.g., "This service calls UserRepository for database access")
- **AI Role:** Understand conceptual relationships beyond imports, rank by relevance, generate explanations

**FR-4: Combined Analysis Endpoint**
- **Input:** File path, repo root path
- **Output:** Single JSON response with summary, design decisions, and related files
- **Optimization:** Batch LLM calls where possible to reduce latency

**FR-5: Health Check & Configuration**
- **Endpoint:** `/health` - returns backend status, LLM API connectivity
- **Endpoint:** `/config` - returns supported file types, commit limit defaults
- **Error Handling:**
  - Return structured errors for: file not found, not a Git repo, LLM API failure, rate limiting
  - Include user-friendly messages and suggested actions

### VS Code Extension (TypeScript)

**FR-6: Context Menu Integration**
- Add "Analyze with ContextWeave" to file explorer right-click menu
- Add command to VS Code command palette: "ContextWeave: Analyze Current File"
- Trigger analysis for selected file, send request to backend

**FR-7: Sidebar Panel ("ContextWeave Insights")**
- Display three collapsible sections:
  1. **"What this file does"** - AI-generated summary
  2. **"Key design decisions"** - List with commit hashes and timestamps
  3. **"You should also read"** - Related files with explanations
- Show loading spinner while backend processes request (with estimated time)
- Use VS Code theme colors for consistency

**FR-8: Source Attribution & Transparency**
- Label all AI-generated content with icon/badge: "✨ AI-generated"
- Render commit hashes as clickable links (open in VS Code Git history view)
- Include disclaimer at bottom: "AI-generated insights may be incomplete. Always verify with source code and commits."
- Show which commits were analyzed (e.g., "Based on 47 commits from Jan 2023 to Dec 2024")

**FR-9: Related File Navigation**
- Make related file names clickable to open in editor
- Show file paths relative to repo root
- Highlight if related file is already open in editor

**FR-10: Error Handling & Edge Cases**
- Show user-friendly error messages for:
  - File not in a Git repository
  - Backend unreachable
  - LLM API rate limit exceeded
  - File too large (> 10,000 lines)
- Provide actionable guidance (e.g., "Ensure this file is in a Git repository with commit history")
- Handle binary files gracefully: "This file type is not supported for analysis"

**FR-11: Configuration**
- Allow user to set backend URL in VS Code settings (default: `http://localhost:8000`)
- Optional: set LLM API key in settings (if backend requires it)
- Optional: set commit history limit (default: 50)

## Non-Functional Requirements

**NFR-1: Latency & Performance**
- Target: < 10 seconds for combined analysis (summary + decisions + related files)
- Show progress indicators with estimated time remaining
- Optimize LLM calls: batch requests, use streaming if available
- Cache results for 5 minutes (same file, same commit hash)

**NFR-2: Usability (5-Second Comprehension Rule)**
- Sidebar content must be scannable in 5 seconds
- Use clear section headings: "What this file does", "Key design decisions", "You should also read"
- Avoid jargon; use simple language suitable for junior developers
- Use visual hierarchy: bold headings, bullet points, whitespace

**NFR-3: Reliability**
- Handle common edge cases gracefully:
  - Binary files (images, PDFs): show "Not supported" message
  - Empty files or files with no history: show "No analysis available"
  - New files (not yet committed): show "File has no Git history"
  - Very large files (> 10,000 lines): warn or truncate
- Graceful degradation if LLM API is slow or rate-limited
- Retry logic for transient backend failures (max 2 retries)

**NFR-4: Transparency & Responsible AI**
- **Citation:** Always show which commits were used as evidence (hashes, dates)
- **Labeling:** Clearly mark AI-generated content with icon/badge
- **Uncertainty:** When commit history is sparse or ambiguous, say so explicitly:
  - "Only 3 commits found; limited design context available"
  - "Commit messages are brief; design decisions may be incomplete"
- **No Hallucination:** Ground all claims in actual commits/code; never invent information
- **Privacy:** Repository code is processed only for analysis; no long-term storage or external sharing

**NFR-5: Code Quality & Maintainability**
- Use Python type hints (mypy-compatible)
- Use TypeScript strict mode for VS Code extension
- Basic error logging for debugging (log to file or console)
- AI-assisted code generation for boilerplate (document in README)
- Unit tests for core backend logic (GitPython integration, prompt formatting)

**NFR-6: Deployment & Infrastructure (Optional)**
- Backend can run locally (`uvicorn main:app`) or on AWS (EC2/Lightsail)
- Optional: use AWS Bedrock for LLM inference (instead of OpenAI) for enterprise alignment
- Configuration via environment variables (LLM API key, endpoint URL)
- Docker support for easy deployment

## AI Requirements

### AI vs. Rule-Based Logic: Clear Separation

**Rule-Based Components (GitPython, static analysis):**
- Extract file content from disk
- Query Git history (commits, diffs, authors, dates)
- Parse import statements (basic regex or AST)
- Identify co-changed files (Git log analysis)
- Calculate basic metrics (file size, commit count)

**AI Components (LLM API):**
- Interpret code semantics and generate summaries
- Analyze natural language commit messages
- Synthesize design decisions across multiple commits
- Infer conceptual relationships between files
- Generate human-readable explanations

**Critical Insight:** Rule-based logic collects structured data; AI interprets and reasons about it. Without AI, we have a commit browser. Without rules, we have no data to reason about.

### Where AI is Used

**AI-1: Code Summarization**
- **Task:** Generate 2-3 sentence summary of file purpose
- **Input:** File content (code), file path, language
- **LLM Prompt Example:**
  ```
  You are helping a junior developer understand a codebase.
  Summarize what this file does in 2-3 clear sentences.
  Avoid jargon; use simple language.
  
  File: src/services/PaymentService.java
  Content: [file content]
  ```
- **Why AI:** Understands semantic intent across languages and frameworks. Can identify main responsibilities even in poorly documented code. Adapts explanation style for junior developers.
- **Why Not Rules:** Would require language-specific parsers, hardcoded templates for every pattern (factory, repository, controller), and can't handle novel code structures.

**AI-2: Design Decision Extraction**
- **Task:** Analyze commit history to infer architectural choices and reasoning
- **Input:** List of commits (message, diff, date, author)
- **LLM Prompt Example:**
  ```
  You are analyzing Git history to help a new developer understand design decisions.
  Extract 2-5 key design decisions from these commits.
  Focus on: architectural changes, refactorings, performance improvements, bug fixes with reasoning.
  For each decision, cite the commit hash.
  
  Commits:
  - abc123 (2024-01-15): "Refactored to use async/await for better performance"
    Diff: [diff content]
  - def456 (2024-02-20): "Migrated from REST to GraphQL"
    Diff: [diff content]
  ...
  ```
- **Why AI:** 
  - Interprets unstructured natural language commit messages (varied phrasing, typos, abbreviations)
  - Understands code diffs semantically (not just line changes)
  - Synthesizes patterns across multiple commits (e.g., "gradual migration over 8 commits")
  - Infers intent even when commit messages are brief
- **Why Not Rules:** Commit messages have infinite variation. Regex patterns would miss most meaningful decisions. Diff analysis requires understanding code semantics, not just text changes.

**AI-3: Related File Recommendation**
- **Task:** Identify conceptually related files and explain relationships
- **Input:** File content, import statements, co-changed files (from Git), directory structure
- **LLM Prompt Example:**
  ```
  You are helping a new developer navigate a codebase.
  Identify 2-3 related files they should read next to understand this file.
  Explain the relationship in simple terms.
  
  Current file: src/services/UserService.java
  Content: [file content]
  Imports: [list of imports]
  Frequently co-changed with: [list of files]
  ```
- **Why AI:**
  - Understands conceptual relationships beyond imports (e.g., "both handle authentication")
  - Ranks by relevance for learning (not just technical coupling)
  - Generates natural explanations ("This service calls UserRepository for database access")
- **Why Not Rules:** Static analysis finds imports but misses semantic relationships. Co-change analysis produces false positives (files changed together for unrelated reasons).

**AI-4: Natural Language Generation**
- **Task:** Produce human-readable explanations for all insights
- **Why AI:** Adapts tone and detail level for junior developers. Avoids robotic template text. Handles edge cases gracefully ("Limited commit history available").
- **Why Not Rules:** Templates are rigid and don't handle nuance.

### LLM Selection & Configuration

**Recommended Models:**
- **OpenAI GPT-4 or GPT-3.5-turbo:** Strong code understanding, good instruction following
- **AWS Bedrock (Claude or Titan):** For enterprise deployment, data residency in India
- **Fallback:** Any LLM with code understanding capabilities (Gemini, Llama 3)

**Prompt Engineering Strategy:**
- Use structured prompts with clear instructions and examples
- Request JSON output for structured data (design decisions, related files)
- Include source grounding: "Base your answer only on the provided commits"
- Use temperature = 0.3 for consistency (low creativity, high accuracy)
- Iterate prompts during development using Kiro AI assistance

### Responsible AI Behavior

**RAI-1: Citation & Transparency**
- Every design decision must cite commit hash(es) as evidence
- Show which commits were analyzed (count, date range)
- Make commit hashes clickable for verification

**RAI-2: Labeling**
- Mark all AI-generated content with "✨ AI-generated" badge
- Include disclaimer: "AI-generated insights may be incomplete. Always verify with source code."

**RAI-3: Handling Uncertainty**
- When commit history is sparse (< 5 commits), say: "Limited commit history available"
- When commit messages are uninformative ("fix", "update"), say: "Commit messages are brief; design decisions may be incomplete"
- Never hallucinate or invent information not grounded in actual commits/code

**RAI-4: Privacy & Data Handling**
- Repository code is sent to LLM API only for analysis (no training, no storage)
- No long-term storage of code or analysis results (optional 5-minute cache)
- User must provide their own LLM API key (no shared keys)
- Warn users if using cloud LLM APIs with proprietary code

**RAI-5: Bias & Fairness**
- Use simple, clear language accessible to non-native English speakers
- Avoid cultural assumptions or jargon specific to Western tech companies
- Test with codebases from Indian companies and colleges

## Constraints & Assumptions

**Constraints:**
- **Single Repo Focus:** MVP supports one Git repository at a time (no multi-repo or monorepo support)
- **Local Git Clone:** Repository must be cloned locally; no remote Git API access
- **External LLM Dependency:** Requires API key for OpenAI, AWS Bedrock, or similar (subject to rate limits and costs)
- **File-Level Analysis:** Focus on individual files, not cross-file architectural analysis
- **Limited Resources:** Small team, limited time; prioritize core features over polish

**Assumptions:**
- Target repositories are Git-based with meaningful commit history (50+ commits)
- Files are text-based code (Python, JavaScript, Java, TypeScript, Go) or config files
- Users have VS Code installed and can install extensions locally
- Backend runs locally (`localhost:8000`) or on accessible dev server
- LLM API is available and responsive (< 5 seconds per request)
- Users are comfortable with basic Git concepts (commits, diffs, branches)
- Target audience: Indian developers with English proficiency (may not be native speakers)

**Out of Scope for MVP:**
- Multi-language UI (English only for MVP; Hindi/regional languages in future)
- Real-time collaboration or team features
- Integration with Jira, Slack, or other tools
- Caching beyond 5 minutes or persistent storage
- Fine-tuned models or self-hosted LLMs
- Support for non-Git VCS (SVN, Mercurial)
- Comprehensive language support (focus on top 5 languages)

**Development Context:**
- Requirements and design documents generated with Kiro AI assistant
- Backend and extension code may use AI-assisted development (Copilot, ChatGPT, Kiro)
- Document AI assistance in README for transparency

## Success Criteria

The MVP is successful if:

1. **Functional:** A developer can right-click a file in VS Code and see all three insights (summary, design decisions, related files) in < 15 seconds

2. **Accurate:** AI-generated summaries are accurate and helpful when validated by manual review of 20 sample files from real Indian company codebases

3. **Grounded:** Design decisions include real commit references that can be verified; no hallucinated information

4. **Relevant:** Related files are genuinely useful (at least 2/3 relevant per manual review by target users)

5. **Reliable:** System handles edge cases gracefully (binary files, sparse history, large files) without crashes

6. **Transparent:** Users understand which commits were analyzed and can verify AI claims

7. **AI Justification:** Stakeholders (judges, users, investors) understand why AI is essential—not just convenient—for this product

8. **User Validation:** 5+ developers from target segment (freshers, Tier-2/3 students, junior engineers) report that ContextWeave helps them understand code faster than existing tools

## Target Impact (Qualitative)

- **Learning Speed:** New developers understand unfamiliar files 5-10x faster (from 30 minutes to 3 minutes per file)
- **Senior Dev Time:** Reduce "why was this built this way?" interruptions by 50%
- **Confidence:** Junior developers feel more confident exploring codebases independently
- **Onboarding:** New hires become productive 2-3 weeks faster

## Development Approach

**AI-Assisted Development:**
- Use Kiro AI assistant to generate requirements.md and design.md
- Use LLMs (ChatGPT, Claude, Copilot) to generate boilerplate code:
  - FastAPI route scaffolding
  - VS Code extension structure (package.json, activation events)
  - TypeScript interfaces and types
- Use AI to draft and refine LLM prompt templates for code analysis
- Use AI to generate test cases and sample data
- Document all AI assistance in README for transparency

**Iteration Strategy:**
1. **Backend Core:** Implement file summary endpoint with basic LLM integration
2. **Git Integration:** Add GitPython logic to extract commit history and diffs
3. **Design Decisions:** Implement design decision extraction with prompt engineering
4. **Related Files:** Add related file recommendation logic
5. **VS Code Extension:** Build sidebar UI and backend integration
6. **Polish:** Error handling, edge cases, UX improvements
7. **Testing:** Validate with real codebases from Indian companies/colleges
8. **Documentation:** README, setup guide, demo video

**Testing Strategy:**
- Unit tests for backend logic (GitPython integration, prompt formatting)
- Manual testing with sample repositories:
  - Large BFSI codebase (Java/Spring Boot)
  - Node.js/React startup project
  - Python data science project
  - College project (PHP/MySQL)
- User testing with 5+ developers from target segment
- Edge case testing (binary files, sparse history, large files)

**Deployment Options:**
- **Local:** Run backend with `uvicorn main:app --reload`
- **AWS EC2/Lightsail:** Deploy backend on small instance (t3.micro)
- **AWS Bedrock:** Use Bedrock for LLM inference (data residency in India)
- **Docker:** Provide Dockerfile for easy deployment

## Appendix: Technical Stack

**Backend:**
- Python 3.11+
- FastAPI (web framework)
- GitPython (Git operations)
- OpenAI Python SDK (LLM API)
- Pydantic (data validation)

**Frontend:**
- TypeScript
- VS Code Extension API
- Axios or fetch (HTTP client)
- VS Code Webview API (sidebar rendering)

**Development Tools:**
- AI coding assistants (GitHub Copilot, ChatGPT, Claude)
- Git for version control
- Postman or curl for API testing
