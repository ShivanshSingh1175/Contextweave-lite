# ContextWeave Lite - Testing Guide

How to test ContextWeave Lite manually and verify it works correctly.

---

## Testing Overview

ContextWeave Lite testing consists of:

1. **Backend API Testing** - Test FastAPI endpoints
2. **Git Analysis Testing** - Test Git operations
3. **LLM Integration Testing** - Test LLM API calls
4. **VS Code Extension Testing** - Test extension functionality
5. **End-to-End Testing** - Test complete user workflows

---

## Prerequisites

Before testing, make sure:

- Backend is running: `cd backend && python main.py`
- Extension is compiled: `cd vscode-extension && npm run compile`
- You have a Git repository to test with (can use this project)
- LLM API key is configured in `backend/.env` (optional, can test mock mode)

---

## 1. Backend API Testing

### Test 1.1: Health Check Endpoint

**Purpose:** Verify backend is running and healthy.

**Steps:**
1. Open browser or use curl:
   ```bash
   curl http://localhost:8000/
   ```

**Expected Result:**
```json
{
  "status": "healthy",
  "service": "ContextWeave Lite API",
  "version": "0.1.0"
}
```

**Pass Criteria:** Status code 200, JSON response with correct fields.

---

### Test 1.2: Health Check with LLM Status

**Purpose:** Verify LLM configuration status.

**Steps:**
```bash
curl http://localhost:8000/health
```

**Expected Result (with API key):**
```json
{
  "status": "healthy",
  "llm_configured": true,
  "version": "0.1.0"
}
```

**Expected Result (without API key):**
```json
{
  "status": "healthy",
  "llm_configured": false,
  "version": "0.1.0"
}
```

**Pass Criteria:** Status code 200, `llm_configured` matches actual configuration.

---

### Test 1.3: File Analysis Endpoint (Valid Request)

**Purpose:** Test main analysis endpoint with valid inputs.

**Steps:**
```bash
curl -X POST http://localhost:8000/context/file \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/absolute/path/to/contextweave-lite",
    "file_path": "/absolute/path/to/contextweave-lite/backend/main.py",
    "selected_code": null,
    "commit_limit": 50
  }'
```

**Note:** Replace paths with actual absolute paths on your system.

**Expected Result:**
```json
{
  "summary": "This file is the main entry point...",
  "decisions": [
    {
      "title": "...",
      "description": "...",
      "commits": ["abc123"]
    }
  ],
  "related_files": [
    {
      "path": "backend/git_utils.py",
      "reason": "..."
    }
  ],
  "weird_code_explanation": null,
  "metadata": {
    "commits_analyzed": 10,
    "llm_model": "llama-3.1-8b-instant",
    "has_commit_history": true
  }
}
```

**Pass Criteria:**
- Status code 200
- All required fields present
- Summary is 2-3 sentences
- Decisions have titles, descriptions, and commit hashes
- Related files have paths and reasons

---

### Test 1.4: File Analysis Endpoint (Invalid Repo)

**Purpose:** Test error handling for invalid repository.

**Steps:**
```bash
curl -X POST http://localhost:8000/context/file \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/nonexistent/path",
    "file_path": "/nonexistent/path/file.py",
    "selected_code": null,
    "commit_limit": 50
  }'
```

**Expected Result:**
```json
{
  "detail": "Repository path does not exist: /nonexistent/path"
}
```

**Pass Criteria:** Status code 400, clear error message.

---

### Test 1.5: File Analysis Endpoint (Not a Git Repo)

**Purpose:** Test error handling for non-Git directory.

**Steps:**
1. Create a temporary directory: `mkdir /tmp/not-a-repo`
2. Create a file: `echo "test" > /tmp/not-a-repo/test.py`
3. Call API:
   ```bash
   curl -X POST http://localhost:8000/context/file \
     -H "Content-Type: application/json" \
     -d '{
       "repo_path": "/tmp/not-a-repo",
       "file_path": "/tmp/not-a-repo/test.py",
       "selected_code": null,
       "commit_limit": 50
     }'
   ```

**Expected Result:**
```json
{
  "detail": "Not a valid Git repository: /tmp/not-a-repo"
}
```

**Pass Criteria:** Status code 400, clear error message.

---

## 2. Git Analysis Testing

### Test 2.1: Commit History Extraction

**Purpose:** Verify commit history is extracted correctly.

**Steps:**
1. Open Python REPL:
   ```bash
   cd backend
   python
   ```

2. Test function:
   ```python
   from git_utils import get_commit_history
   
   commits = get_commit_history(
       repo_path="/path/to/contextweave-lite",
       file_path="/path/to/contextweave-lite/backend/main.py",
       limit=10
   )
   
   print(f"Found {len(commits)} commits")
   print(commits[0])  # Print first commit
   ```

**Expected Result:**
```python
Found 10 commits
{
  'hash': 'abc123',
  'full_hash': 'abc123def456...',
  'author': 'Your Name',
  'date': '2026-02-07T10:30:00+00:00',
  'message': 'Initial commit',
  'lines_changed': 50
}
```

**Pass Criteria:**
- Returns list of commit dicts
- Each commit has all required fields
- Commits are sorted by recency (most recent first)

---

### Test 2.2: Import Extraction (Python)

**Purpose:** Verify Python imports are extracted correctly.

**Steps:**
```python
from git_utils import extract_imports

code = """
import os
import sys
from pathlib import Path
from typing import List, Dict
"""

imports = extract_imports(code, "test.py")
print(imports)
```

**Expected Result:**
```python
['os.py', 'sys.py', 'pathlib.py', 'typing.py']
```

**Pass Criteria:** Returns list of imported module paths.

---

### Test 2.3: Import Extraction (JavaScript)

**Purpose:** Verify JavaScript imports are extracted correctly.

**Steps:**
```python
from git_utils import extract_imports

code = """
import React from 'react';
import { useState } from 'react';
const axios = require('axios');
"""

imports = extract_imports(code, "test.js")
print(imports)
```

**Expected Result:**
```python
['react', 'react', 'axios']
```

**Pass Criteria:** Returns list of imported modules.

---

### Test 2.4: Co-Changed Files

**Purpose:** Verify co-changed files are detected.

**Steps:**
```python
from git_utils import find_co_changed_files

co_changed = find_co_changed_files(
    repo_path="/path/to/contextweave-lite",
    relative_path="backend/main.py",
    limit=100
)

print(f"Found {len(co_changed)} co-changed files")
print(co_changed[:3])  # Print top 3
```

**Expected Result:**
```python
Found 5 co-changed files
[
  {'path': 'backend/git_utils.py', 'frequency': 8},
  {'path': 'backend/llm_client.py', 'frequency': 6},
  {'path': 'backend/schemas.py', 'frequency': 4}
]
```

**Pass Criteria:**
- Returns list of dicts with 'path' and 'frequency'
- Sorted by frequency (highest first)

---

## 3. LLM Integration Testing

### Test 3.1: Mock Mode (No API Key)

**Purpose:** Verify mock mode works when LLM is not configured.

**Steps:**
1. Remove API key from `backend/.env`:
   ```bash
   # Comment out or remove LLM_API_KEY
   # LLM_API_KEY=...
   ```

2. Restart backend: `Ctrl+C` then `python main.py`

3. Call API:
   ```bash
   curl -X POST http://localhost:8000/context/file \
     -H "Content-Type: application/json" \
     -d '{
       "repo_path": "/path/to/contextweave-lite",
       "file_path": "/path/to/contextweave-lite/backend/main.py",
       "selected_code": null,
       "commit_limit": 50
     }'
   ```

**Expected Result:**
- Status code 200
- Response includes `"mock_response": true` in metadata
- Summary mentions "Configure LLM_API_KEY"
- Decisions are based on raw commit messages
- Related files are based on imports/co-changes

**Pass Criteria:** System works without LLM, provides deterministic response.

---

### Test 3.2: LLM Mode (With API Key)

**Purpose:** Verify LLM integration works correctly.

**Steps:**
1. Add API key to `backend/.env`:
   ```bash
   LLM_API_KEY=your-groq-api-key-here
   LLM_API_BASE=https://api.groq.com/openai/v1
   LLM_MODEL=llama-3.1-8b-instant
   ```

2. Restart backend: `Ctrl+C` then `python main.py`

3. Call API (same as Test 3.1)

**Expected Result:**
- Status code 200
- Response includes `"llm_configured": true` in metadata
- Summary is coherent and human-readable
- Decisions are synthesized from multiple commits
- Related files have clear explanations

**Pass Criteria:**
- LLM API is called successfully
- Response is more detailed than mock mode
- No "mock_response" flag in metadata

---

### Test 3.3: LLM Error Handling

**Purpose:** Verify graceful fallback when LLM fails.

**Steps:**
1. Set invalid API key in `backend/.env`:
   ```bash
   LLM_API_KEY=invalid-key-12345
   ```

2. Restart backend

3. Call API

**Expected Result:**
- Status code 200 (not 500)
- Falls back to mock mode
- Response includes `"mock_response": true`
- Backend logs show LLM error

**Pass Criteria:** System doesn't crash, falls back gracefully.

---

## 4. VS Code Extension Testing

### Test 4.1: Extension Activation

**Purpose:** Verify extension loads correctly.

**Steps:**
1. Open `vscode-extension` in VS Code
2. Press **F5** to launch Extension Development Host
3. Check Debug Console (View > Debug Console)

**Expected Result:**
```
ContextWeave Lite extension activated
```

**Pass Criteria:** No activation errors, extension loads successfully.

---

### Test 4.2: Command Registration

**Purpose:** Verify command appears in Command Palette.

**Steps:**
1. In Extension Development Host, press `Ctrl+Shift+P`
2. Type "ContextWeave"

**Expected Result:**
- Command "ContextWeave: Explain this file" appears in list

**Pass Criteria:** Command is registered and visible.

---

### Test 4.3: Sidebar Display

**Purpose:** Verify sidebar opens and displays correctly.

**Steps:**
1. Open a Git repository in Extension Development Host
2. Open a code file (e.g., `backend/main.py`)
3. Run command: "ContextWeave: Explain this file"

**Expected Result:**
- Sidebar opens on the right
- Shows loading spinner initially
- After 3-10 seconds, shows results:
  - Summary section
  - Design decisions section
  - Related files section
- All sections are readable and well-formatted

**Pass Criteria:**
- Sidebar opens without errors
- Results display correctly
- UI is responsive and themed

---

### Test 4.4: File Link Clicking

**Purpose:** Verify clicking related files opens them.

**Steps:**
1. Run analysis on a file
2. In sidebar, click on a related file path

**Expected Result:**
- File opens in editor
- Correct file is opened

**Pass Criteria:** File links work correctly.

---

### Test 4.5: Error Handling (No Backend)

**Purpose:** Verify error handling when backend is down.

**Steps:**
1. Stop the backend: `Ctrl+C` in backend terminal
2. In Extension Development Host, run command

**Expected Result:**
- Error message: "Cannot connect to backend server at http://localhost:8000"
- Sidebar shows error with suggestions:
  - "Make sure the backend is running: cd backend && python main.py"
  - "Check that the backend URL is correct in VS Code settings"
  - "Verify no firewall is blocking localhost:8000"

**Pass Criteria:** Clear error message with actionable suggestions.

---

### Test 4.6: Error Handling (Not a Git Repo)

**Purpose:** Verify error handling for non-Git directories.

**Steps:**
1. Create a temporary directory: `mkdir /tmp/not-a-repo`
2. Open it in Extension Development Host
3. Create a file: `test.py`
4. Run command

**Expected Result:**
- Error message: "Invalid request: Not a valid Git repository"
- Sidebar shows error with suggestions:
  - "Make sure the file is in a Git repository"
  - "Check that the file exists and is tracked by Git"
  - "Try running: git status"

**Pass Criteria:** Clear error message with actionable suggestions.

---

## 5. End-to-End Testing

### Test 5.1: Complete User Workflow

**Purpose:** Test complete user journey from start to finish.

**Steps:**
1. Start backend: `cd backend && python main.py`
2. Compile extension: `cd vscode-extension && npm run compile`
3. Launch extension: Press **F5** in VS Code
4. Open a Git repository in Extension Development Host
5. Open a code file
6. Run command: "ContextWeave: Explain this file"
7. Wait for results
8. Click on a related file
9. Run command again on the new file

**Expected Result:**
- All steps complete without errors
- Results are displayed correctly
- File navigation works
- Second analysis works on new file

**Pass Criteria:** Complete workflow works end-to-end.

---

### Test 5.2: Selected Code Explanation

**Purpose:** Test "weird code" explanation feature.

**Steps:**
1. Open a code file
2. Select 5-10 lines of code
3. Run command: "ContextWeave: Explain this file"

**Expected Result:**
- Sidebar shows additional section: "🤔 Selected Code Explanation"
- Explanation is relevant to selected code
- Explanation references Git history if available

**Pass Criteria:** Selected code explanation works correctly.

---

### Test 5.3: Multiple Files

**Purpose:** Test analyzing multiple files in sequence.

**Steps:**
1. Analyze file A
2. Analyze file B
3. Analyze file C

**Expected Result:**
- Each analysis completes successfully
- Results are different for each file
- No memory leaks or performance degradation

**Pass Criteria:** Multiple analyses work correctly.

---

## 6. Performance Testing

### Test 6.1: Latency Measurement

**Purpose:** Measure end-to-end latency.

**Steps:**
1. Start timer
2. Run command: "ContextWeave: Explain this file"
3. Stop timer when results appear

**Expected Result:**
- Latency < 15 seconds for typical files
- Latency breakdown:
  - Git analysis: 0.5-2 seconds
  - LLM API call: 2-5 seconds
  - Network: 0.1-0.5 seconds
  - UI rendering: < 0.1 seconds

**Pass Criteria:** Total latency < 15 seconds.

---

### Test 6.2: Large File Handling

**Purpose:** Test handling of large files.

**Steps:**
1. Create or find a file > 10,000 lines
2. Run analysis

**Expected Result:**
- Analysis completes successfully
- File is truncated with note: "[File truncated after 10,000 lines]"
- No memory issues or crashes

**Pass Criteria:** Large files are handled gracefully.

---

### Test 6.3: Many Commits Handling

**Purpose:** Test handling of files with many commits.

**Steps:**
1. Find a file with > 100 commits
2. Set commit limit to 100 in VS Code settings
3. Run analysis

**Expected Result:**
- Analysis completes successfully
- Only top 100 commits are analyzed
- Metadata shows: `"commits_analyzed": 100`

**Pass Criteria:** Many commits are handled efficiently.

---

## 7. Edge Case Testing

### Test 7.1: Empty File

**Purpose:** Test handling of empty files.

**Steps:**
1. Create empty file: `touch empty.py`
2. Add to Git: `git add empty.py && git commit -m "Add empty file"`
3. Run analysis

**Expected Result:**
- Analysis completes
- Summary mentions file is empty
- No crashes

**Pass Criteria:** Empty files are handled gracefully.

---

### Test 7.2: No Commit History

**Purpose:** Test handling of files with no commits.

**Steps:**
1. Create new file: `echo "test" > new.py`
2. Add to Git but don't commit: `git add new.py`
3. Run analysis

**Expected Result:**
- Analysis completes
- Shows: "No commit history found for this file"
- Related files still work (based on imports)

**Pass Criteria:** Files without commits are handled gracefully.

---

### Test 7.3: Binary File

**Purpose:** Test handling of binary files.

**Steps:**
1. Try to analyze a binary file (e.g., `.png`, `.pdf`)

**Expected Result:**
- Error or graceful handling
- Clear message that binary files are not supported

**Pass Criteria:** Binary files don't crash the system.

---

## Test Results Template

Use this template to record test results:

```
Test ID: 1.1
Test Name: Health Check Endpoint
Date: 2026-02-07
Tester: Your Name
Result: PASS / FAIL
Notes: [Any observations or issues]
```

---

## Automated Testing (Future)

For future development, consider adding:

### Backend Unit Tests
```python
# tests/test_git_utils.py
def test_get_commit_history():
    commits = get_commit_history(...)
    assert len(commits) > 0
    assert 'hash' in commits[0]
```

### Backend Integration Tests
```python
# tests/test_api.py
def test_analyze_file_endpoint():
    response = client.post("/context/file", json={...})
    assert response.status_code == 200
```

### Extension Tests
```typescript
// src/test/extension.test.ts
test('Command is registered', () => {
    const commands = vscode.commands.getCommands();
    assert(commands.includes('contextweave.explainFile'));
});
```

---

## Reporting Issues

When reporting test failures, include:

1. **Test ID and name**
2. **Steps to reproduce**
3. **Expected result**
4. **Actual result**
5. **Environment:**
   - OS and version
   - Python version
   - Node.js version
   - VS Code version
6. **Logs:**
   - Backend logs
   - Extension Debug Console logs
7. **Screenshots** (if applicable)

---

**Last Updated:** February 7, 2026
