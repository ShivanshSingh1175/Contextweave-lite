# Troubleshooting Guide

Common issues and solutions for ContextWeave Lite.

## Backend Issues

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

**Error**: `Address already in use` or `Port 8000 is already allocated`

**Solution**:
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>

# Or use a different port:
export PORT=8001
python main.py
```

---

**Error**: `Not a valid Git repository`

**Solution**: Make sure you're passing the correct repo path. The path should be the root of a Git repository (containing `.git` folder).

```python
# Check if path is a Git repo:
import os
print(os.path.exists("/path/to/repo/.git"))  # Should be True
```

## Extension Issues

### Extension won't load

**Error**: `Cannot find module` or TypeScript errors

**Solution**:
```bash
cd vscode-extension
npm install
npm run compile
```

Check for errors in the compile output. Fix any TypeScript errors before running.

---

**Error**: Extension doesn't appear in Command Palette

**Solution**:
1. Make sure you pressed `F5` to launch Extension Development Host
2. Check the Debug Console in the original VS Code window for errors
3. Try reloading the Extension Development Host window (`Ctrl+R` or `Cmd+R`)

---

**Error**: Sidebar doesn't open

**Solution**:
1. Look for "ContextWeave" in the Activity Bar (left side)
2. Click the icon to open the sidebar
3. If icon is missing, check `package.json` for correct configuration

### Connection Issues

**Error**: `Cannot connect to backend` or `ECONNREFUSED`

**Solution**:
1. Make sure backend is running: visit `http://localhost:8000/health`
2. Check backend URL in VS Code settings:
   - Open Settings (`Ctrl+,` or `Cmd+,`)
   - Search "ContextWeave"
   - Verify `backendUrl` is `http://localhost:8000`
3. Check firewall isn't blocking port 8000

---

**Error**: `Network Error` or `Timeout`

**Solution**:
1. Backend might be slow (LLM call takes time)
2. Check backend logs for errors
3. Try with a smaller file or fewer commits
4. Increase timeout in `apiClient.ts`:
   ```typescript
   timeout: 60000  // 60 seconds
   ```

## Git Issues

**Error**: `No commit history found for this file`

**Solution**:
1. Make sure file has been committed:
   ```bash
   git log -- path/to/file.py
   ```
2. If file is new (not committed), you'll only get a summary, no design decisions
3. Try with a different file that has more commits

---

**Error**: `File not found in repository`

**Solution**:
1. Make sure file path is correct
2. File must be inside the workspace folder
3. Check file hasn't been deleted or moved

## LLM Issues

**Error**: `Invalid API key` or `Unauthorized`

**Solution**:
1. Check your API key is correct:
   ```bash
   echo $LLM_API_KEY  # Should show your key
   ```
2. Make sure key hasn't expired
3. Verify key has proper permissions
4. For OpenAI, check: https://platform.openai.com/api-keys

---

**Error**: `Rate limit exceeded`

**Solution**:
1. Wait a few minutes before trying again
2. Upgrade to paid tier (OpenAI free tier is limited)
3. Use caching to reduce requests
4. Try a different API provider

---

**Error**: `Model not found`

**Solution**:
1. Check model name is correct:
   ```bash
   echo $LLM_MODEL  # Should be gpt-3.5-turbo, gpt-4, etc.
   ```
2. Some providers use different names (e.g., Azure uses `gpt-35-turbo`)
3. Check provider documentation for available models

---

**Error**: `Timeout` or `Request took too long`

**Solution**:
1. Use a faster model (GPT-3.5 instead of GPT-4)
2. Reduce commit limit:
   ```json
   {
     "commit_limit": 20  // Instead of 50
   }
   ```
3. Increase timeout in `llm_client.py`:
   ```python
   async with httpx.AsyncClient(timeout=60.0) as client:
   ```

## Response Issues

**Error**: `Mock Response` warning appears

**Solution**: This means `LLM_API_KEY` is not set. The system works but uses mock data.

To fix:
```bash
export LLM_API_KEY="sk-your-key-here"
# Restart backend
python main.py
```

---

**Error**: Response is empty or incomplete

**Solution**:
1. Check backend logs for LLM errors
2. LLM might have returned invalid JSON
3. Try with a different file
4. Check if file is too large (> 10,000 lines)

---

**Error**: "Limited commit context available"

**Solution**: This is expected when:
- File has < 5 commits
- Commit messages are very brief
- This is not an error, just a limitation

## UI Issues

**Error**: Sidebar shows blank page

**Solution**:
1. Open Developer Tools in Extension Development Host:
   - Help > Toggle Developer Tools
2. Check Console for JavaScript errors
3. Check if HTML is valid in `sidebarProvider.ts`

---

**Error**: Related files don't open when clicked

**Solution**:
1. Check file path is correct (relative to repo root)
2. File might not exist
3. Check browser console for errors
4. Verify message passing is working:
   ```typescript
   vscode.postMessage({ type: 'openFile', path: '...' });
   ```

---

**Error**: Styling looks wrong

**Solution**:
1. VS Code theme variables might not be available
2. Check CSS in `_getStyles()` method
3. Try a different VS Code theme

## Performance Issues

**Error**: Analysis takes > 30 seconds

**Solution**:
1. File might be very large - check file size
2. Too many commits - reduce `commit_limit`
3. LLM is slow - try GPT-3.5 instead of GPT-4
4. Network is slow - check internet connection

---

**Error**: Extension feels sluggish

**Solution**:
1. Check CPU usage (LLM calls are CPU-intensive)
2. Close other VS Code windows
3. Restart VS Code
4. Check for memory leaks in extension

## Development Issues

**Error**: Changes to TypeScript not reflected

**Solution**:
```bash
# Recompile
npm run compile

# Or use watch mode
npm run watch

# Then reload Extension Development Host (Ctrl+R or Cmd+R)
```

---

**Error**: Changes to Python not reflected

**Solution**:
Backend runs with auto-reload, but sometimes you need to restart:
```bash
# Stop backend (Ctrl+C)
# Start again
python main.py
```

---

**Error**: Breakpoints not hitting

**Solution**:
1. Make sure you compiled TypeScript: `npm run compile`
2. Check `outFiles` in `launch.json` is correct
3. Try setting breakpoint in a different location
4. Check Debug Console for errors

## Platform-Specific Issues

### Windows

**Error**: `'python' is not recognized`

**Solution**:
```bash
# Try python3 or py
python3 --version
py --version

# Or add Python to PATH
```

---

**Error**: Virtual environment activation fails

**Solution**:
```powershell
# Use PowerShell instead of CMD
venv\Scripts\Activate.ps1

# If execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### macOS/Linux

**Error**: Permission denied

**Solution**:
```bash
# Make sure you have write permissions
chmod +x venv/bin/activate
source venv/bin/activate
```

---

**Error**: `xcrun: error: invalid active developer path`

**Solution**:
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

## Still Having Issues?

### Check Logs

**Backend logs**:
- Look at terminal where backend is running
- Check for Python tracebacks
- Look for HTTP error codes

**Extension logs**:
- Open Debug Console in VS Code
- Check Developer Tools console
- Look for TypeScript errors

### Verify Setup

```bash
# Check Python version
python --version  # Should be 3.11+

# Check Node version
node --version  # Should be 18+

# Check Git
git --version

# Check dependencies
cd backend
pip list | grep fastapi
pip list | grep gitpython

cd ../vscode-extension
npm list axios
npm list typescript
```

### Test Components Separately

**Test backend**:
```bash
curl http://localhost:8000/health
```

**Test Git operations**:
```python
from git import Repo
repo = Repo("/path/to/repo")
print(len(list(repo.iter_commits(max_count=10))))
```

**Test LLM**:
```bash
# Set API key
export LLM_API_KEY="sk-..."

# Test with curl
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $LLM_API_KEY"
```

### Get Help

1. **Read documentation**:
   - [README.md](README.md)
   - [QUICKSTART.md](QUICKSTART.md)
   - [TESTING.md](TESTING.md)

2. **Check code comments**: Most functions have detailed docstrings

3. **Review error messages**: They usually contain helpful information

4. **Search issues**: Check if others had the same problem

5. **Create minimal reproduction**: Isolate the problem

### Common Gotchas

- ❌ Forgetting to activate virtual environment
- ❌ Using wrong Python version (< 3.11)
- ❌ Not compiling TypeScript after changes
- ❌ Backend not running when testing extension
- ❌ Wrong repo path (not the Git root)
- ❌ File not committed to Git
- ❌ API key not set or expired
- ❌ Firewall blocking port 8000

### Quick Checklist

Before asking for help, verify:

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Backend running (`http://localhost:8000/health` works)
- [ ] TypeScript compiled (`npm run compile`)
- [ ] Extension loaded (F5 pressed)
- [ ] File is in a Git repository
- [ ] File has commit history
- [ ] LLM API key set (if not using mock mode)

If all checked and still not working, review error messages carefully and check logs.
