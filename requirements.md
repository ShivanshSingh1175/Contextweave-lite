# ContextWeave Lite - Requirements Document

**Version:** 1.0  
**Date:** February 2026  
**Track:** AI for Bharat - AI for Learning & Developer Productivity  
**Status:** Production Ready

---

## Project Overview

ContextWeave Lite is an AI-powered VS Code extension that accelerates code comprehension by analyzing Git history and generating human-readable explanations. The system combines deterministic Git analysis with large language model reasoning to help developers understand unfamiliar codebases 5-10x faster.

### Problem Statement

**Who Faces This Problem:**
- Students from Tier-2/Tier-3 colleges in India learning from real-world GitHub projects
- New graduates joining Indian companies (BFSI, govtech, startups) with large legacy codebases
- Junior developers (0-2 years experience) maintaining inherited systems with minimal documentation

**The Problem:**
Indian developers face a critical productivity bottleneck when working with large, poorly documented codebases. New hires spend 4-6 weeks understanding code structure, constantly interrupting overworked senior developers with "why" questions. Legacy systems have sparse documentation, cryptic commit messages, and concentrated knowledge in 1-2 senior developers. This creates a knowledge monopoly that slows onboarding, reduces productivity, and limits career growth for junior developers.

**Real-World Impact:**
- New graduates at Bangalore BFSI companies spend 3+ days understanding a single payment processing file
- Students abandon open-source contributions because codebases are too opaque
- Junior developers break production systems due to lack of context about "weird" code patterns
- Senior developers spend 40% of their time answering repetitive "why" questions
- Onboarding costs companies 6-8 weeks of reduced productivity per new hire

**Why This Matters:**
India has 5+ million software developers, with 300,000+ new graduates entering the workforce annually. Most join companies with legacy codebases built over 5-10 years. Accelerating code comprehension directly impacts India's developer productivity, reduces dependency on scarce senior talent, and democratizes access to complex codebases.

---

## Solution Overview

ContextWeave Lite provides instant code context through AI-powered analysis of Git history and file relationships.

**Core Capabilities:**
- Generates 2-3 sentence summaries explaining what a file does
- Extracts key design decisions from commit history with evidence (commit hashes)
- Suggests 2-3 related files developers should read next
- Explains selected code snippets when highlighted
- Works directly in VS Code with zero configuration

**How It Works:**
1. Developer right-clicks any file in VS Code
2. Selects "ContextWeave: Explain this file"
3. System analyzes Git history (last 50 commits) and file relationships
4. LLM interprets data and generates human-readable explanations
5. Results appear in sidebar within 10-15 seconds

**Key Innovation:**
Separates deterministic data collection (GitPython) from AI reasoning (LLM), ensuring transparency and allowing graceful degradation when Git is unavailable.

---

## Objectives

### Success Criteria

**User Success:**
- Reduce file comprehension time from 30 minutes to 3 minutes (10x improvement)
- Achieve 80%+ accuracy in summaries (measured by user feedback)
- Reduce "why" questions to senior developers by 50%
- Enable students to contribute to open-source projects they previously couldn't understand

**Technical Success:**
- Analysis completes in under 15 seconds for typical files
- System works with or without Git (graceful degradation)
- 99%+ uptime during demonstrations
- Zero manual backend configuration required

**Business Success:**
- Reduce onboarding time from 6 weeks to 3 weeks
- Demonstrate clear ROI for Indian companies hiring junior developers
- Validate product-market fit with 20+ active users from target segment

---

## Key Features

### 1. AI-Powered File Summarization

**Description:**  
Generates concise 2-3 sentence summaries explaining file purpose, responsibilities, and role in the system.

**Why Important:**  
Developers waste hours reading code to understand basic file purpose. AI summarization provides instant context, allowing developers to quickly decide if a file is relevant to their task.

**Implementation:**  
LLM analyzes file content, commit messages, and import relationships to generate semantic understanding beyond what static analysis can provide.

---

### 2. Design Decision Extraction

**Description:**  
Identifies 2-3 key architectural or design decisions from Git commit history, with supporting evidence (commit hashes, dates, authors).

**Why Important:**  
Design rationale is rarely documented. Commit history contains this knowledge but is buried in hundreds of commits with cryptic messages. Extracting and synthesizing decisions prevents developers from unknowingly breaking important patterns.

**Implementation:**  
System analyzes commit messages and diffs across multiple commits, using LLM to infer intent and synthesize patterns (e.g., "gradual migration from sync to async over 8 commits").

---

### 3. Related File Recommendations

**Description:**  
Suggests 2-3 files developers should read next, based on import relationships and co-change patterns, with explanations for each recommendation.

**Why Important:**  
Understanding one file in isolation is insufficient. Developers need to build mental models of how components interact. Manual exploration is time-consuming and error-prone.

**Implementation:**  
Combines static analysis (import parsing) with temporal analysis (files that change together) to identify conceptual relationships.

---

### 4. Code Snippet Explanation

**Description:**  
When developers select 5-10 lines of "weird" code, system explains why it exists based on Git history and code context.

**Why Important:**  
Unusual patterns often exist for good reasons (workarounds, performance optimizations, legacy API compatibility). Without context, developers either avoid touching the code or break it during refactoring.

**Implementation:**  
LLM analyzes selected code in context of surrounding code and commit history to infer rationale.

---

### 5. Zero-Configuration Backend

**Description:**  
VS Code extension automatically spawns and manages Python backend process. No manual setup required.

**Why Important:**  
Manual backend management creates friction and failure points. Students and junior developers often struggle with environment setup. Automatic management ensures "it just works."

**Implementation:**  
Extension detects Python environment, spawns FastAPI server, monitors health, and gracefully handles failures.

---

## Functional Requirements

### FR-1: File Analysis Endpoint

**Requirement:**  
System shall accept file path and repository path, returning structured analysis within 15 seconds.

**Input:**
- Repository path (absolute)
- File path (absolute)
- Optional: selected code snippet
- Optional: commit limit (default 50)

**Output:**
- Summary (2-3 sentences)
- Design decisions (0-3 items, each with title, description, commit hashes)
- Related files (0-3 items, each with path and reason)
- Optional: code explanation
- Metadata (commits analyzed, model used, confidence indicators)

**Behavior:**
- Validate inputs (file exists, readable)
- Extract Git history (gracefully handle non-Git repos)
- Parse file imports
- Analyze co-change patterns
- Call LLM with structured prompt
- Return validated JSON response

---

### FR-2: Git History Analysis

**Requirement:**  
System shall extract commit history for specified file, including messages, authors, dates, and diff statistics.

**Behavior:**
- Query last N commits (configurable, default 50)
- Extract commit metadata (hash, author, date, message)
- Calculate lines changed per commit
- Handle edge cases (no commits, binary files, merge commits)
- Return structured data for LLM consumption

---

### FR-3: Import Detection

**Requirement:**  
System shall parse import statements for Python, JavaScript, TypeScript, and Java files.

**Behavior:**
- Use language-specific regex patterns
- Extract imported module/file paths
- Convert to relative paths from repository root
- Return list of imported files

---

### FR-4: Co-Change Analysis

**Requirement:**  
System shall identify files that frequently change together with target file.

**Behavior:**
- Analyze last 100 commits touching target file
- Count co-occurrence of other files in same commits
- Rank by frequency
- Return top 5 co-changed files with frequency counts

---

### FR-5: LLM Integration

**Requirement:**  
System shall call external LLM API with structured prompts and parse JSON responses.

**Behavior:**
- Build prompts with file content, commit history, related files
- Use instructor library for guaranteed valid JSON
- Implement token-aware truncation (max 6000 tokens)
- Handle API failures gracefully (fallback to mock mode)
- Retry on transient errors (max 2 retries)

---

### FR-6: VS Code Extension

**Requirement:**  
System shall provide VS Code command for analyzing files and displaying results in sidebar.

**Behavior:**
- Register command: "ContextWeave: Explain this file"
- Detect active file and workspace
- Extract selected code if any
- Call backend API
- Display results in webview sidebar
- Handle errors with clear messages and suggestions

---

### FR-7: Graceful Degradation

**Requirement:**  
System shall analyze files even when Git is unavailable, falling back to file-only analysis.

**Behavior:**
- Attempt Git operations with try-catch
- If Git unavailable, continue with imports-only analysis
- Log warnings (not errors) for missing Git
- Clearly indicate in response metadata what data is available
- Never fail hard due to missing Git

---

## Non-Functional Requirements

### Performance

**Latency:**
- End-to-end analysis: < 15 seconds (p95)
- Git analysis: < 2 seconds
- LLM API call: < 10 seconds
- UI rendering: < 1 second

**Throughput:**
- Support 10 concurrent analyses (single-user MVP)
- Handle files up to 10,000 lines
- Process repositories with 10,000+ commits

---

### Scalability

**Current Scope:**
- Single user, local deployment
- One repository at a time
- File-level analysis only

**Design for Future Scale:**
- Stateless backend (can horizontally scale)
- No persistent storage (can add caching layer)
- API-first design (can support multiple clients)

---

### Reliability

**Availability:**
- 99% uptime during demonstrations
- Graceful degradation on component failures
- Clear error messages with recovery suggestions

**Error Handling:**
- No crashes on invalid inputs
- Fallback to mock mode if LLM unavailable
- Continue analysis if Git unavailable
- Retry transient API failures

---

### Security

**API Key Management:**
- Store keys in .env file (never hardcoded)
- .env in .gitignore (never committed)
- Health endpoint shows key status without exposing value

**Data Privacy:**
- Code sent to LLM only for analysis (not training)
- No long-term storage of code
- User provides own API key (not shared)
- Warn users about sending proprietary code to cloud

**Input Validation:**
- Validate all file paths (prevent directory traversal)
- Validate repository paths (prevent arbitrary command execution)
- Sanitize user inputs before LLM prompts

---

### Usability

**5-Second Comprehension Rule:**
- Users understand results within 5 seconds of viewing
- Clear section headings with icons
- 2-3 sentences max for summaries
- Bullet points for decisions and related files

**Accessibility:**
- Use VS Code theme colors (respects user preferences)
- Keyboard navigation support
- Screen reader compatible (semantic HTML)

**Error Messages:**
- Clear, actionable error messages
- Suggest specific fixes (not generic "try again")
- Provide links to documentation when relevant

---

## Constraints

### Technical Constraints

**Dependencies:**
- Requires Python 3.11+ installed locally
- Requires Node.js 18+ for extension development
- Requires VS Code 1.85+ as host environment
- Requires internet connection for LLM API calls

**Platform:**
- Supports Windows, macOS, Linux
- Tested on Windows 11 (primary development platform)

**Git:**
- Works best with Git repositories
- Gracefully degrades without Git
- Requires meaningful commit history for best results

---

### Time Constraints

**Hackathon Scope:**
- 2-day development window
- Focus on core MVP features only
- Defer advanced features (caching, multi-repo, chat interface)

---

### Data Constraints

**Token Limits:**
- LLM context window: 8,192 tokens (llama-3.1-8b-instant)
- File content truncated to 6,000 tokens
- Commit history limited to 50 commits (configurable)

**Rate Limits:**
- Groq free tier: 30 requests/minute
- No caching in MVP (each request hits API)

---

### Resource Constraints

**Memory:**
- Backend: ~150 MB RAM
- Extension: ~50 MB RAM
- Total: ~200 MB (acceptable for development tools)

**Storage:**
- No persistent storage required
- Temporary data in memory only

---

## Future Scope

### Phase 2 Enhancements

**Multi-File Analysis:**
- Analyze entire modules or features
- Generate architectural diagrams
- Identify cross-file patterns

**Caching Layer:**
- Cache analysis results for 5 minutes
- Reduce API costs and latency
- Invalidate on file changes

**Improved Related Files:**
- AST-based analysis for deeper relationships
- Workspace indexing for faster lookups
- LLM-based relationship inference

---

### Phase 3 Enhancements

**Chat Interface:**
- Follow-up questions about code
- Interactive exploration
- Conversational code review

**Team Collaboration:**
- Shared annotations
- Team knowledge base
- Onboarding checklists

**Enterprise Features:**
- Self-hosted LLM option
- Fine-tuned models for specific codebases
- Analytics and insights dashboard

---

### Phase 4 Enhancements

**India-Specific Features:**
- Multi-language UI (Hindi, Tamil, Telugu, Bengali)
- Integration with Indian code schools (Masai, Scaler)
- Optimized for Indian internet speeds
- Support for Indian cloud providers

**Advanced AI:**
- Proactive insights (suggest refactoring opportunities)
- Code quality analysis
- Security vulnerability detection
- Performance optimization suggestions

---

## Appendix

### Glossary

**Deterministic Analysis:** Data extraction using rule-based logic (no AI interpretation)  
**LLM:** Large Language Model (AI system for natural language understanding and generation)  
**Co-Change Pattern:** Files that frequently appear together in commits  
**Token:** Unit of text for LLM processing (roughly 0.75 words)  
**Graceful Degradation:** System continues functioning with reduced capabilities when components fail

### References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- VS Code Extension API: https://code.visualstudio.com/api
- Groq API Documentation: https://console.groq.com/docs
- GitPython Documentation: https://gitpython.readthedocs.io/

---

**Document Control:**  
Version: 1.0  
Last Updated: February 2026  
Approved By: Technical Lead  
Status: Final
