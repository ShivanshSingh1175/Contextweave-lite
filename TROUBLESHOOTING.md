# ContextWeave Lite - Troubleshooting Guide

Solutions to common problems and error messages.

---

## Backend Issues

### Backend Won't Start

#### Error: `ModuleNotFoundError: No module named 'fastapi'`

**Cause:** Python dependencies not installed.

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

**Verify installation:**
```bash
pip list | grep fastapi
pip list | grep gitpython
pip list | grep httpx
```

---

#### Error: `Address already in use`

**Cause:** Port 8000 is already in use by another process.

**Solution 1:** Stop the other process using port 8000

**Windows:**
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -i :8000
kill -9 <PID>
```

**Solution 2:** Use a different port

Edit `backend/.env`:
```bash
PORT=8001
```

Update VS Code extension settings:
- Settings > Search "contextweave" > Backend URL: `http://localhost:8001`

---

#### Error: `python: command not found`

**Cause:** Python not installed or not in PATH.

**Solution:**
1. Install Python 3.11+ from https://www.python.org/downloads/
2. Make sure "Add Python to PATH" is checked during installation
3. Restart your terminal
4. Verify: `python --version`

---

### Backend Crashes or Errors

#### Error: `Not a valid Git repository`

**Cause:** The `repo_path` provided is not a Git repository.

**Solution:**
1. Make sure the folder is a Git repository: `git status`
2. If not, initialize Git: `git init`
3. Make at least one commit: `git add . && git commit -m "Initial commit"`

---

#### Error: `File does not exist`

**Cause:** The `file_path` provided doesn't exist.

**Solution:**
1. Check that the file exists: `ls <file_path>` (Linux/Mac) or `dir <file_path>` (Windows)
2. Make sure you're using absolute paths, not relative paths
3. Check for typos in the file path

---

#### Error: `Invalid LLM API key`

**Cause:** The LLM API key in `.env` is invalid or expired.

**Solution:**
1. Check your API key at https://console.groq.com/keys
2. Generate a new API key if needed
3. Update `backend/.env`:
   ```bash
   LLM_API_KEY=your-new-api-key-here
   ```
4. Restart the backend: `Ctrl+C` then `python main.py`

---

#### Error: `LLM API rate limit exceeded`

**Cause:** You've exceeded the API rate limit (Groq free tier: 30 requests/minute).

**Solution:**
1. Wait 1 minute and try again
2. Reduce the number of requests
3. Upgrade to a paid plan if needed

---

#### Error: `LLM API request timed out`

**Cause:** The LLM API took too long to respond (> 30 seconds).

**Solution:**
1. Check your internet connection
2. Try again (might be temporary)
3. Try a smaller file or fewer commits
4. Check LLM API status page

---

## VS Code Extension Issues

### Extension Won't Load

#### Error: `Cannot find module './sidebarProvider'`

**Cause:** TypeScript code not compiled.

**Solution:**
```bash
cd vscode-extension
npm run compile
```

**Verify compilation:**
```bash
ls out/  # Should see extension.js, apiClient.js, sidebarProvider.js
```

---

#### Error: `npm: command not found`

**Cause:** Node.js/npm not installed.

**Solution:**
1. Install Node.js 16+ from https://nodejs.org/
2. Restart your terminal
3. Verify: `node --version` and `npm --version`

---

#### Extension Doesn't Appear in Command Palette

**Cause:** Extension not activated or not running in Extension Development Host.

**Solution:**
1. Make sure you pressed **F5** to launch Extension Development Host
2. Check that a new VS Code window opened
3. In the new window, press `Ctrl+Shift+P` and search for "ContextWeave"
4. Check the Debug Console (View > Debug Console) for activation errors

---

### Extension Runtime Errors

#### Error: `Cannot connect to backend server`

**Cause:** Backend not running or wrong URL.

**Solution:**
1. Make sure backend is running: `cd backend && python main.py`
2. Check backend URL in VS Code settings:
   - Settings > Search "contextweave" > Backend URL
   - Default: `http://localhost:8000`
3. Test backend manually: Open http://localhost:8000 in browser
4. Check firewall settings (allow localhost:8000)

---

#### Error: `No active file to analyze`

**Cause:** No file is open in the editor.

**Solution:**
1. Open a file in VS Code
2. Make sure the file is in the active editor tab
3. Try again

---

#### Error: `File is not in a workspace`

**Cause:** The file is not part of an opened workspace/folder.

**Solution:**
1. Open a folder in VS Code: File > Open Folder
2. Make sure the file is inside that folder
3. Try again

---

#### Error: `Request timed out after 30 seconds`

**Cause:** Analysis took too long (file too large, too many commits, slow LLM API).

**Solution:**
1. Try a smaller file
2. Reduce commit limit in VS Code settings:
   - Settings > Search "contextweave" > Commit Limit: `20`
3. Check your internet connection
4. Try again (might be temporary)

---

## Git-Related Issues

### No Commit History Found

**Problem:** Analysis shows "No commit history found for this file".

**Cause:** The file has no commits in Git history.

**Solution:**
1. Check if file is tracked: `git status`
2. If untracked, add it: `git add <file>`
3. Commit it: `git commit -m "Add file"`
4. Try analysis again

---

### Commit Messages Are Unhelpful

**Problem:** Design decisions are generic or unhelpful (e.g., "fix", "update").

**Cause:** Commit messages in the repository are too brief or generic.

**Solution:**
1. This is a limitation of the repository's commit history
2. ContextWeave can only work with the information available
3. For future commits, write better commit messages:
   - Explain **why** the change was made, not just **what** changed
   - Example: "Refactored to use async/await for better performance" instead of "refactor"

---

### Binary Files Not Supported

**Problem:** Analysis fails on binary files (images, PDFs, etc.).

**Cause:** ContextWeave only analyzes text files.

**Solution:**
1. Only use ContextWeave on text-based code files
2. Supported: `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.go`, etc.
3. Not supported: `.png`, `.jpg`, `.pdf`, `.exe`, etc.

---

## LLM-Related Issues

### Mock Response Instead of AI Analysis

**Problem:** Sidebar shows "⚠️ Mock Response: LLM not configured".

**Cause:** No LLM API key configured or LLM API call failed.

**Solution:**
1. Add API key to `backend/.env`:
   ```bash
   LLM_API_KEY=your-api-key-here
   ```
2. Restart backend: `Ctrl+C` then `python main.py`
3. Get a free Groq API key: https://console.groq.com/keys

---

### AI Analysis Is Inaccurate

**Problem:** Summary or design decisions don't match the code.

**Cause:** LLM misinterpreted the code or commit messages.

**Solution:**
1. Check the commit history manually to verify
2. Try with a different file
3. Report the issue with examples (if this happens frequently)
4. Remember: AI is not perfect, always verify important information

---

### AI Analysis Is Too Generic

**Problem:** Summary is too vague or doesn't provide useful insights.

**Cause:** File has limited commit history or very brief commit messages.

**Solution:**
1. Check commit history: `git log <file>`
2. If commit messages are brief, AI has limited information
3. Try analyzing a file with richer commit history
4. For future commits, write detailed commit messages

---

## Performance Issues

### Analysis Takes Too Long

**Problem:** Analysis takes > 30 seconds.

**Cause:** Large file, many commits, or slow LLM API.

**Solution:**
1. Reduce commit limit in VS Code settings:
   - Settings > Search "contextweave" > Commit Limit: `20`
2. Try a smaller file
3. Check your internet connection
4. Check LLM API status

---

### Backend Uses Too Much Memory

**Problem:** Backend process uses excessive memory.

**Cause:** Very large files or repositories.

**Solution:**
1. ContextWeave automatically truncates files > 10,000 lines
2. Limit commits to 50 or fewer
3. Restart backend periodically: `Ctrl+C` then `python main.py`

---

## Configuration Issues

### Environment Variables Not Loaded

**Problem:** Backend doesn't see `LLM_API_KEY` even though it's in `.env`.

**Cause:** `.env` file not in the correct location or not loaded.

**Solution:**
1. Make sure `.env` is in the `backend/` directory (same level as `main.py`)
2. Check file name is exactly `.env` (not `.env.txt` or `env`)
3. Restart backend: `Ctrl+C` then `python main.py`
4. Check backend logs for "LLM_API_KEY not set" warning

---

### VS Code Settings Not Applied

**Problem:** Changed settings in VS Code but extension still uses old values.

**Cause:** Settings not saved or extension not reloaded.

**Solution:**
1. Make sure you saved settings: File > Save
2. Reload extension:
   - In Extension Development Host, press `Ctrl+R` (Windows/Linux) or `Cmd+R` (Mac)
   - Or close and reopen Extension Development Host (F5 again)

---

## Debugging Tips

### Enable Verbose Logging

**Backend:**
Edit `backend/main.py` and change logging level:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Extension:**
Check Debug Console in VS Code:
- View > Debug Console
- Look for console.log() messages

---

### Test Backend Manually

Use `curl` or Postman to test the backend directly:

```bash
# Health check
curl http://localhost:8000/health

# Analyze file
curl -X POST http://localhost:8000/context/file \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/repo",
    "file_path": "/path/to/file.py",
    "selected_code": null,
    "commit_limit": 50
  }'
```

---

### Check Git Repository

Verify Git is working:
```bash
cd /path/to/repo
git status
git log --oneline -10
git log --follow <file>
```

---

### Verify Python Environment

Check Python and dependencies:
```bash
python --version
pip list
which python  # Linux/Mac
where python  # Windows
```

---

## Still Having Issues?

If none of these solutions work:

1. **Check the logs:**
   - Backend: Terminal where you ran `python main.py`
   - Extension: VS Code Debug Console (View > Debug Console)

2. **Read the documentation:**
   - `README.md` - Overview and features
   - `ARCHITECTURE.md` - Technical details
   - `GETTING_STARTED.md` - Setup guide

3. **Search for similar issues:**
   - Check GitHub Issues (if available)
   - Search for error messages online

4. **Report the issue:**
   - Open a GitHub Issue with:
     - Error message (full text)
     - Steps to reproduce
     - Your environment (OS, Python version, Node version)
     - Backend logs
     - Extension logs

---

**Last Updated:** February 7, 2026
