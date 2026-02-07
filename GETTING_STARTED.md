# Getting Started with ContextWeave Lite

Complete guide to setting up and using ContextWeave Lite for the first time.

---

## What is ContextWeave Lite?

ContextWeave Lite is an AI-powered VS Code extension that helps you understand code files quickly by analyzing Git history and generating clear explanations. For any file, it provides:

- **Summary:** What the file does in 2-3 sentences
- **Design Decisions:** Key decisions extracted from commit history
- **Related Files:** Files you should read next to understand the context

**Target Users:** Students, new graduates, and junior developers learning unfamiliar codebases.

---

## Prerequisites

Before you begin, make sure you have:

- **Python 3.11 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16 or higher** - [Download Node.js](https://nodejs.org/)
- **VS Code** - [Download VS Code](https://code.visualstudio.com/)
- **Git** - [Download Git](https://git-scm.com/)
- **A Git repository** to analyze (or use this project itself)

**Check your versions:**
```bash
python --version  # Should be 3.11+
node --version    # Should be 16+
npm --version     # Should be 8+
git --version     # Any recent version
```

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/contextweave-lite.git
cd contextweave-lite
```

### Step 2: Set Up the Backend

#### 2.1 Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**What gets installed:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `gitpython` - Git operations
- `httpx` - HTTP client for LLM API
- `python-dotenv` - Environment variable management
- `pydantic` - Data validation

#### 2.2 Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Copy the example file
cp .env.example .env
```

Edit `backend/.env` and add your LLM API key:

```bash
# LLM API Configuration
LLM_API_KEY=your-api-key-here
LLM_API_BASE=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-8b-instant

# Server Configuration (optional)
PORT=8000
```

**Getting a Free Groq API Key:**
1. Go to https://console.groq.com/
2. Sign up for a free account
3. Navigate to "API Keys"
4. Create a new API key
5. Copy and paste it into your `.env` file

**Note:** The system works in "mock mode" without an API key, but you won't get AI-powered analysis.

#### 2.3 Start the Backend

```bash
# From the backend/ directory
python main.py
```

You should see:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Test the backend:**
Open http://localhost:8000 in your browser. You should see:
```json
{
  "status": "healthy",
  "service": "ContextWeave Lite API",
  "version": "0.1.0"
}
```

**Keep this terminal open** - the backend needs to stay running.

---

### Step 3: Set Up the VS Code Extension

Open a **new terminal** (keep the backend running in the first one).

#### 3.1 Install Extension Dependencies

```bash
cd vscode-extension
npm install
```

**What gets installed:**
- `vscode` - VS Code extension API types
- `axios` - HTTP client
- TypeScript and build tools

#### 3.2 Compile the Extension

```bash
npm run compile
```

You should see:
```
> contextweave@0.1.0 compile
> tsc -p ./
```

If there are no errors, compilation succeeded.

#### 3.3 Run the Extension

1. Open the `vscode-extension` folder in VS Code:
   ```bash
   code .
   ```

2. Press **F5** to launch the Extension Development Host

3. A new VS Code window will open with the extension loaded

**Tip:** You can also use the "Run and Debug" panel (Ctrl+Shift+D) and click "Run Extension".

---

## First Use

### Step 1: Open a Git Repository

In the **Extension Development Host** window (the new VS Code window that opened):

1. Click "File" > "Open Folder"
2. Select a folder that is a Git repository
3. Click "Select Folder"

**Don't have a Git repo?** Use the ContextWeave Lite project itself:
- Navigate to the `contextweave-lite` folder you cloned
- Open it in the Extension Development Host

### Step 2: Open a Code File

Open any code file in the repository. For example:
- `backend/main.py` (Python)
- `vscode-extension/src/extension.ts` (TypeScript)
- Any `.py`, `.js`, `.ts`, `.java` file

### Step 3: Run the Command

**Option 1: Command Palette**
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "ContextWeave"
3. Select "ContextWeave: Explain this file"
4. Press Enter

**Option 2: Right-Click Menu**
1. Right-click anywhere in the editor
2. Select "ContextWeave: Explain this file"

**Option 3: Keyboard Shortcut** (if configured)
- Press your configured shortcut (none by default)

### Step 4: View Results

The ContextWeave sidebar will open on the right side and show:

**📄 What this file does**
- 2-3 sentence summary of the file's purpose

**🔍 Key design decisions**
- Important decisions extracted from Git history
- Each decision shows commit hashes as evidence

**📚 You should also read**
- Related files to understand the context
- Click on file paths to open them

**🤔 Selected Code Explanation** (if you selected code)
- Explanation of why the selected code might be unusual

---

## Understanding the Results

### Summary Section

**Example:**
> "This file is the main entry point for the ContextWeave Lite API, which provides endpoints for analyzing code context and history. It uses FastAPI and relies on environment variables loaded from a .env file. The API has endpoints for health checks, file analysis, and LLM API connectivity."

**What it tells you:**
- High-level purpose of the file
- Key technologies used
- Main responsibilities

---

### Design Decisions Section

**Example:**
```
Added async/await for performance
Migrated from synchronous to asynchronous processing to improve API response time
Commits: abc123, def456
```

**What it tells you:**
- Important architectural or design choices
- Why those choices were made
- Which commits introduced the changes

**Click on commit hashes** to see the full commit in Git history (future feature).

---

### Related Files Section

**Example:**
```
📄 backend/git_utils.py
This service calls it for Git operations and commit history analysis

📄 backend/llm_client.py
Both handle the core analysis logic
```

**What it tells you:**
- Files that are conceptually related
- Why you should read them next
- How they connect to the current file

**Click on file paths** to open them in the editor.

---

## Configuration

### Backend Configuration

Edit `backend/.env` to configure:

```bash
# LLM API Configuration
LLM_API_KEY=your-api-key-here
LLM_API_BASE=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-8b-instant

# Server Configuration
PORT=8000
```

**Restart the backend** after changing `.env`:
1. Press `Ctrl+C` in the backend terminal
2. Run `python main.py` again

---

### VS Code Extension Configuration

1. Open VS Code Settings: `File` > `Preferences` > `Settings`
2. Search for "contextweave"
3. Configure:

**Backend URL**
- Default: `http://localhost:8000`
- Change if backend is running on a different port or remote server

**Commit Limit**
- Default: `50`
- Maximum number of commits to analyze
- Higher = more context, but slower

---

## Tips and Best Practices

### 1. Start with Small Files

For your first try, use a small file (< 500 lines) with good commit history. This will give you faster results and help you understand the output.

### 2. Use on Unfamiliar Code

ContextWeave is most useful when you're learning a new codebase. Use it to quickly understand files you've never seen before.

### 3. Read Related Files

After analyzing a file, click on the related files to build a mental model of how the system works.

### 4. Select Weird Code

If you see code that looks unusual, select it and run the command again. ContextWeave will explain why it might exist.

### 5. Check Commit History

If the analysis seems off, check the commit history manually. ContextWeave is only as good as the commit messages.

---

## Common Issues

### "Cannot connect to backend"

**Problem:** Extension can't reach the backend server.

**Solution:**
1. Make sure the backend is running: `cd backend && python main.py`
2. Check that it's running on port 8000
3. Verify the backend URL in VS Code settings

---

### "Not a valid Git repository"

**Problem:** The folder you opened is not a Git repository.

**Solution:**
1. Make sure you opened a Git repository in VS Code
2. Run `git status` in the terminal to verify
3. If not a Git repo, run `git init` to initialize one

---

### "Mock Response: LLM not configured"

**Problem:** No LLM API key configured.

**Solution:**
1. Add your API key to `backend/.env`
2. Restart the backend
3. Get a free Groq API key: https://console.groq.com/keys

---

### "No commit history found"

**Problem:** The file has no commits in Git history.

**Solution:**
1. Make sure the file is tracked by Git: `git add <file>`
2. Commit the file: `git commit -m "Initial commit"`
3. Try again

---

## Next Steps

Now that you have ContextWeave Lite running:

1. **Try it on different files** - See how it handles different languages and file types
2. **Read the documentation** - Check out `README.md` for more details
3. **Understand the architecture** - See `ARCHITECTURE.md` for technical details
4. **Learn about testing** - See `TESTING.md` for test instructions
5. **Troubleshoot issues** - See `TROUBLESHOOTING.md` for common problems

---

## Getting Help

If you run into issues:

1. **Check the logs:**
   - Backend logs: Terminal where you ran `python main.py`
   - Extension logs: VS Code Debug Console (View > Debug Console)

2. **Read the troubleshooting guide:** `TROUBLESHOOTING.md`

3. **Check the documentation:** `README.md`, `ARCHITECTURE.md`

4. **Open an issue:** GitHub Issues (if available)

---

**Welcome to ContextWeave Lite!** We hope it helps you understand code faster and become more productive.
