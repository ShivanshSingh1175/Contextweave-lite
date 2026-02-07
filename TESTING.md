# Testing Guide for ContextWeave Lite

## Testing the Backend

### 1. Health Check

```bash
# Start the backend
cd backend
python main.py

# In another terminal or browser, test:
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "llm_configured": true,
  "version": "0.1.0"
}
```

### 2. Test File Analysis (with curl)

```bash
# Create a test request
curl -X POST http://localhost:8000/context/file \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/your/git/repo",
    "file_path": "/path/to/your/git/repo/some_file.py",
    "commit_limit": 20
  }'
```

Replace `/path/to/your/git/repo` with an actual Git repository path.

### 3. Test with Python Script

Create `test_backend.py`:

```python
import requests
import json

# Test health endpoint
response = requests.get("http://localhost:8000/health")
print("Health check:", response.json())

# Test file analysis
# Replace these paths with your actual repo and file
payload = {
    "repo_path": "/Users/yourname/projects/myrepo",
    "file_path": "/Users/yourname/projects/myrepo/src/main.py",
    "commit_limit": 20
}

response = requests.post(
    "http://localhost:8000/context/file",
    json=payload
)

if response.status_code == 200:
    result = response.json()
    print("\nSummary:", result["summary"])
    print("\nDesign Decisions:")
    for decision in result["decisions"]:
        print(f"  - {decision['title']}: {decision['description']}")
    print("\nRelated Files:")
    for rf in result["related_files"]:
        print(f"  - {rf['path']}: {rf['reason']}")
else:
    print("Error:", response.status_code, response.text)
```

Run it:
```bash
python test_backend.py
```

## Testing the VS Code Extension

### 1. Manual Testing

1. **Open Extension Development Host**
   - Open `vscode-extension` folder in VS Code
   - Press `F5`
   - New VS Code window opens

2. **Test Command Palette**
   - In the new window, open a Git repository
   - Open a file with commit history
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P`)
   - Type "ContextWeave"
   - Select "ContextWeave: Explain this file"

3. **Verify Sidebar**
   - Sidebar should open automatically
   - Should show loading spinner
   - Then show results with three sections

4. **Test Selected Code**
   - Select 5-10 lines of code
   - Run command again
   - Should see "Selected Code Explanation" section

5. **Test Related Files**
   - Click on a related file link
   - File should open in editor

### 2. Test Error Handling

**Test: Backend not running**
1. Stop the backend server
2. Run the command
3. Should see error: "Cannot connect to backend"

**Test: File not in Git repo**
1. Open a file outside any Git repository
2. Run the command
3. Should see error about Git repository

**Test: Empty file**
1. Create an empty file in a Git repo
2. Run the command
3. Should handle gracefully

### 3. Test Configuration

1. Open VS Code Settings (`Ctrl+,` or `Cmd+,`)
2. Search for "ContextWeave"
3. Change `backendUrl` to `http://localhost:9999` (wrong port)
4. Run command
5. Should see connection error
6. Change back to `http://localhost:8000`

## Testing Without LLM API Key

The system should work in "mock mode" without an API key:

1. **Don't set `LLM_API_KEY`** environment variable
2. Start backend
3. Run extension command
4. Should see:
   - ⚠️ Warning: "Mock Response: LLM not configured"
   - Generic summary
   - Raw commit messages as decisions
   - Related files based on imports

This is useful for:
- Testing integration without API costs
- Demonstrating the system without API access
- Development and debugging

## Testing with Different Repositories

### Good Test Cases

1. **Small Python project** (10-50 files)
   - Clear imports
   - Good commit messages
   - Multiple contributors

2. **JavaScript/TypeScript project**
   - Test import detection
   - Test with different file extensions

3. **Java project**
   - Test Java import parsing
   - Test with package structure

4. **File with rich history**
   - 50+ commits
   - Multiple refactorings
   - Clear design decisions

### Edge Cases to Test

1. **New file** (no commits)
   - Should handle gracefully
   - Summary only, no decisions

2. **Binary file**
   - Should return error or skip

3. **Very large file** (10,000+ lines)
   - Should truncate for analysis
   - Should still work

4. **File with sparse commits**
   - Only 1-2 commits
   - Should say "Limited commit history"

5. **File with unclear commit messages**
   - Messages like "fix", "update", "wip"
   - LLM should admit uncertainty

## Performance Testing

### Backend Response Time

```python
import time
import requests

payload = {
    "repo_path": "/path/to/repo",
    "file_path": "/path/to/repo/file.py",
    "commit_limit": 50
}

start = time.time()
response = requests.post("http://localhost:8000/context/file", json=payload)
end = time.time()

print(f"Response time: {end - start:.2f} seconds")
print(f"Status: {response.status_code}")
```

Expected times:
- Without LLM: < 1 second
- With LLM (GPT-3.5): 3-8 seconds
- With LLM (GPT-4): 5-15 seconds

### Extension Responsiveness

1. Run command
2. Sidebar should show loading immediately (< 100ms)
3. Results should appear within 10-15 seconds
4. UI should remain responsive during loading

## Debugging

### Backend Debugging

1. **Check logs** in terminal where backend is running
2. **Add print statements** in `main.py`, `git_utils.py`, `llm_client.py`
3. **Use Python debugger**:
   ```python
   import pdb; pdb.set_trace()
   ```

### Extension Debugging

1. **Open Developer Tools** in Extension Development Host
   - Help > Toggle Developer Tools
   - Check Console for errors

2. **Add console.log** in TypeScript files:
   ```typescript
   console.log('Debug info:', variable);
   ```

3. **Use VS Code debugger**:
   - Set breakpoints in TypeScript files
   - Press `F5` to start debugging
   - Breakpoints will hit when command runs

### Common Issues

**Issue: "Module not found" in backend**
- Solution: Activate virtual environment, reinstall requirements

**Issue: Extension not loading**
- Solution: Run `npm run compile`, check for TypeScript errors

**Issue: Webview not updating**
- Solution: Check browser console in webview, verify HTML is valid

**Issue: LLM timeout**
- Solution: Increase timeout in `llm_client.py`, use faster model

## Automated Testing (Future)

### Backend Tests (pytest)

```python
# test_git_utils.py
def test_get_commit_history():
    commits = get_commit_history("/path/to/repo", "/path/to/file.py", limit=10)
    assert len(commits) <= 10
    assert all("hash" in c for c in commits)

def test_extract_imports():
    code = "import os\nfrom typing import List"
    imports = extract_imports(code, "test.py")
    assert "os" in str(imports)
```

### Extension Tests (Jest)

```typescript
// extension.test.ts
import * as assert from 'assert';
import { analyzeFile } from '../src/apiClient';

suite('API Client Tests', () => {
    test('analyzeFile returns valid response', async () => {
        const result = await analyzeFile('/repo', '/repo/file.py');
        assert.ok(result.summary);
        assert.ok(Array.isArray(result.decisions));
    });
});
```

## Checklist Before Release

- [ ] Backend starts without errors
- [ ] Health endpoint returns 200
- [ ] File analysis works with real Git repo
- [ ] Extension loads in VS Code
- [ ] Command appears in Command Palette
- [ ] Sidebar opens and shows results
- [ ] Related files are clickable
- [ ] Error messages are clear and helpful
- [ ] Works without LLM API key (mock mode)
- [ ] Works with LLM API key (real analysis)
- [ ] README is accurate and complete
- [ ] All dependencies are in requirements.txt and package.json

## Getting Help

If tests fail:
1. Check backend logs for errors
2. Check VS Code Developer Tools console
3. Verify Git repository is valid
4. Verify file has commit history
5. Check LLM API key is valid
6. Review error messages carefully

For more help, see [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md).
