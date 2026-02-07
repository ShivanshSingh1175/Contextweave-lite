# Getting Started with ContextWeave Lite

Welcome! This guide will help you get ContextWeave Lite running in just a few minutes.

## What is ContextWeave Lite?

ContextWeave Lite is an AI-powered VS Code extension that helps you understand code files by analyzing:
- **What the file does** (2-3 sentence summary)
- **Key design decisions** from Git history
- **Related files** you should read next

Perfect for new developers, students, and anyone exploring unfamiliar codebases!

## Prerequisites

Before you start, make sure you have:

- ✅ **Python 3.11+** - [Download](https://www.python.org/downloads/)
- ✅ **Node.js 18+** - [Download](https://nodejs.org/)
- ✅ **VS Code** - [Download](https://code.visualstudio.com/)
- ✅ **Git repository** to analyze
- ⚠️ **OpenAI API key** (optional, but recommended) - [Get one](https://platform.openai.com/api-keys)

## Quick Start (5 Minutes)

### Step 1: Clone or Download

If you received this as a zip file, extract it. Otherwise:

```bash
git clone <repository-url>
cd contextweave-lite
```

### Step 2: Start the Backend

Open a terminal and run:

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# On Windows (PowerShell):
venv\Scripts\activate
# On Windows (CMD):
venv\Scripts\activate.bat
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your API key (optional but recommended)
# On Windows (PowerShell):
$env:LLM_API_KEY="sk-your-openai-key-here"
# On macOS/Linux:
export LLM_API_KEY="sk-your-openai-key-here"

# Start the server
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ **Backend is running!** Keep this terminal open.

### Step 3: Install VS Code Extension

Open a **new terminal** (keep backend running) and run:

```bash
# Navigate to extension folder
cd vscode-extension

# Install dependencies
npm install

# Compile TypeScript
npm run compile
```

You should see:
```
Successfully compiled TypeScript
```

✅ **Extension is compiled!**

### Step 4: Run the Extension

1. **Open VS Code**
2. **Open the `vscode-extension` folder** in VS Code:
   ```bash
   code .
   ```
3. **Press F5** (or go to Run > Start Debugging)
4. A new VS Code window opens - this is the **Extension Development Host**

✅ **Extension is running!**

### Step 5: Try It Out!

In the **Extension Development Host** window:

1. **Open a Git repository** (File > Open Folder)
   - Use any project with Git history
   - Or use the ContextWeave Lite repo itself!

2. **Open a file** that has some commits
   - For example: `backend/main.py`

3. **Open Command Palette**:
   - Windows/Linux: `Ctrl+Shift+P`
   - macOS: `Cmd+Shift+P`

4. **Type**: `ContextWeave: Explain this file`

5. **Press Enter**

The ContextWeave sidebar will open showing:
- 📄 **What this file does**
- 🔍 **Key design decisions** (with commit hashes)
- 📚 **Related files** to read next

🎉 **Congratulations! You're using ContextWeave Lite!**

## What If I Don't Have an API Key?

No problem! ContextWeave works in "mock mode" without an API key:

- ✅ Git history extraction works
- ✅ Related files detection works
- ✅ UI works perfectly
- ⚠️ Summaries are generic (not AI-powered)
- ⚠️ Design decisions are raw commit messages

You'll see a warning: "Mock Response: LLM not configured"

This is great for:
- Testing the system
- Understanding how it works
- Developing without API costs

To get full AI-powered analysis, add your API key and restart the backend.

## Next Steps

### Explore Features

**Try with different files**:
- Files with lots of commits (rich history)
- Files with few commits (sparse history)
- Different programming languages

**Try selected code**:
1. Select 5-10 lines of code
2. Run the command again
3. Get an explanation of the selected code!

**Try related files**:
- Click on related file links
- They open in the editor automatically

### Configure Settings

1. Open VS Code Settings (`Ctrl+,` or `Cmd+,`)
2. Search for "ContextWeave"
3. Adjust:
   - `backendUrl` - Backend server URL
   - `commitLimit` - Number of commits to analyze

### Read Documentation

- **[README.md](README.md)** - Complete documentation
- **[TESTING.md](TESTING.md)** - Testing guide
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues
- **[LLM_PROVIDERS.md](backend/LLM_PROVIDERS.md)** - Alternative LLM providers

## Common Issues

### "Cannot connect to backend"

**Problem**: Backend isn't running or wrong URL

**Solution**:
1. Check backend is running: visit `http://localhost:8000/health`
2. Check VS Code settings for correct `backendUrl`

### "No commit history found"

**Problem**: File hasn't been committed to Git

**Solution**:
1. Make sure file is in a Git repository
2. Make sure file has been committed (not just added)
3. Try a different file with more commits

### "Module not found" errors

**Problem**: Dependencies not installed

**Solution**:
```bash
# Backend
cd backend
pip install -r requirements.txt

# Extension
cd vscode-extension
npm install
npm run compile
```

### Extension doesn't appear

**Problem**: Extension not loaded properly

**Solution**:
1. Make sure you pressed F5 in the `vscode-extension` folder
2. Check Debug Console for errors
3. Try reloading the Extension Development Host (`Ctrl+R` or `Cmd+R`)

For more issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Understanding the Output

### Summary Section
- 2-3 sentences explaining what the file does
- Written in simple, clear language
- Based on code analysis and Git history

### Design Decisions Section
- Key architectural choices from Git history
- Each decision has:
  - **Title**: Short description
  - **Description**: One-line explanation
  - **Commits**: Clickable commit hashes

### Related Files Section
- Files you should read next
- Based on:
  - Import statements
  - Files that change together
- Each file has a reason explaining the relationship

### Selected Code Explanation (Optional)
- Appears when you select code before running command
- Explains why the code might be unusual or noteworthy

## Tips for Best Results

### Choose Good Files
- ✅ Files with 10+ commits
- ✅ Files with descriptive commit messages
- ✅ Core application files (not config)
- ❌ Brand new files (no history)
- ❌ Generated files (migrations, builds)

### Write Good Commit Messages
ContextWeave learns from your commit messages!

- ✅ "Refactored authentication to use JWT tokens for better security"
- ✅ "Added caching layer to improve API response time"
- ❌ "fix"
- ❌ "update"
- ❌ "wip"

### Use Appropriate Models
- **GPT-3.5-turbo**: Fast, cheap, good quality
- **GPT-4**: Slower, expensive, excellent quality
- **Local models**: Free, private, lower quality

## Cost Considerations

If using OpenAI:
- **GPT-3.5-turbo**: ~$0.002-0.01 per analysis
- **GPT-4**: ~$0.06-0.30 per analysis

For 10 analyses per day:
- **GPT-3.5**: ~$0.10/day = $3/month
- **GPT-4**: ~$1.00/day = $30/month

Tips to reduce costs:
- Use GPT-3.5 for most files
- Use GPT-4 only for complex files
- Reduce `commit_limit` to 20-30
- Use caching (built-in 5-minute cache)

## Getting Help

### Documentation
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - This file
- [TESTING.md](TESTING.md) - Testing guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

### Check Logs
- **Backend**: Look at terminal where `python main.py` is running
- **Extension**: Open Debug Console in VS Code

### Verify Setup
```bash
# Check versions
python --version  # Should be 3.11+
node --version    # Should be 18+
git --version

# Test backend
curl http://localhost:8000/health

# Check dependencies
cd backend && pip list
cd vscode-extension && npm list
```

## What's Next?

Now that you have ContextWeave running:

1. **Try it on your projects** - See how it helps you understand code
2. **Customize prompts** - Edit `llm_client.py` to adjust AI behavior
3. **Try different LLM providers** - See [LLM_PROVIDERS.md](backend/LLM_PROVIDERS.md)
4. **Share feedback** - What works? What could be better?
5. **Extend it** - Add features you need!

## Project Structure

```
contextweave-lite/
├── backend/              # FastAPI server
│   ├── main.py          # API endpoints
│   ├── git_utils.py     # Git operations
│   ├── llm_client.py    # LLM integration
│   └── schemas.py       # Data models
│
├── vscode-extension/     # VS Code extension
│   └── src/
│       ├── extension.ts      # Main extension
│       ├── apiClient.ts      # Backend client
│       └── sidebarProvider.ts # UI
│
└── docs/                 # Documentation
    ├── README.md
    ├── QUICKSTART.md
    ├── TESTING.md
    └── TROUBLESHOOTING.md
```

## Contributing

Want to improve ContextWeave? Great!

1. Make your changes
2. Test thoroughly
3. Update documentation
4. Share your improvements!

## License

MIT License - Free to use, modify, and distribute

---

**Ready to explore code faster?** 🚀

Start with [Step 1](#step-1-clone-or-download) above, and you'll be analyzing code in 5 minutes!

Questions? Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or [README.md](README.md).
