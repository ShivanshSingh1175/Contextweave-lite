# ContextWeave Lite - Quick Start Guide

Get ContextWeave Lite running in 5 minutes.

---

## Prerequisites

- **Python 3.11+** installed
- **Node.js 16+** and npm installed
- **VS Code** installed
- **Git** repository to analyze (or use this project itself)

---

## Step 1: Backend Setup (2 minutes)

### 1.1 Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 1.2 Configure LLM API Key

Create a `.env` file in the `backend/` directory:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
# For Groq (free tier available):
LLM_API_KEY=your-groq-api-key-here
LLM_API_BASE=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-8b-instant
```

**Get a free Groq API key:** https://console.groq.com/keys

**Note:** The system works in "mock mode" without an API key, but you won't get AI-powered analysis.

### 1.3 Start the Backend

```bash
# From the backend/ directory
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Test it:** Open http://localhost:8000 in your browser. You should see:
```json
{
  "status": "healthy",
  "service": "ContextWeave Lite API",
  "version": "0.1.0"
}
```

---

## Step 2: VS Code Extension Setup (2 minutes)

### 2.1 Install Extension Dependencies

```bash
cd vscode-extension
npm install
```

### 2.2 Compile the Extension

```bash
npm run compile
```

You should see output like:
```
> contextweave@0.1.0 compile
> tsc -p ./
```

### 2.3 Run the Extension

1. Open the `vscode-extension` folder in VS Code
2. Press **F5** to launch the Extension Development Host
3. A new VS Code window will open with the extension loaded

---

## Step 3: Try It Out (1 minute)

### 3.1 Open a Git Repository

In the Extension Development Host window:
1. Open a folder that is a Git repository
2. Open any code file (e.g., `backend/main.py` from this project)

### 3.2 Run the Command

**Option 1:** Command Palette
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "ContextWeave: Explain this file"
3. Press Enter

**Option 2:** Right-Click Menu
1. Right-click in the editor
2. Select "ContextWeave: Explain this file"

### 3.3 View Results

The ContextWeave sidebar will open and show:
- 📄 **What this file does** - 2-3 sentence summary
- 🔍 **Key design decisions** - Extracted from Git history
- 📚 **You should also read** - Related files

---

## Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:** Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

---

### Extension won't load

**Error:** `Cannot find module './sidebarProvider'`

**Solution:** Compile the TypeScript code:
```bash
cd vscode-extension
npm run compile
```

---

### "Cannot connect to backend"

**Error in VS Code:** `Cannot connect to backend server at http://localhost:8000`

**Solution:**
1. Make sure the backend is running: `cd backend && python main.py`
2. Check that port 8000 is not blocked by firewall
3. Verify backend URL in VS Code settings: `File > Preferences > Settings > Search "contextweave"`

---

### "Not a valid Git repository"

**Error:** `Backend error: Not a valid Git repository`

**Solution:**
1. Make sure the folder you opened in VS Code is a Git repository
2. Run `git status` in the terminal to verify
3. If not a Git repo, run `git init` to initialize one

---

### Mock Response (No AI Analysis)

**Warning:** `⚠️ Mock Response: LLM not configured`

**Solution:**
1. Add your LLM API key to `backend/.env`
2. Restart the backend: `Ctrl+C` then `python main.py`
3. Get a free Groq API key: https://console.groq.com/keys

---

## Configuration

### Backend Configuration

Edit `backend/.env`:

```bash
# LLM API Configuration
LLM_API_KEY=your-api-key-here
LLM_API_BASE=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-8b-instant

# Server Configuration
PORT=8000
```

### VS Code Extension Configuration

1. Open VS Code Settings: `File > Preferences > Settings`
2. Search for "contextweave"
3. Configure:
   - **Backend URL:** Default `http://localhost:8000`
   - **Commit Limit:** Default `50` (max commits to analyze)

---

## Next Steps

- **Read the full documentation:** See `README.md` for detailed information
- **Understand the architecture:** See `ARCHITECTURE.md` for technical details
- **Learn about testing:** See `TESTING.md` for test instructions
- **Troubleshoot issues:** See `TROUBLESHOOTING.md` for common problems

---

## Quick Reference

### Start Backend
```bash
cd backend
python main.py
```

### Compile Extension
```bash
cd vscode-extension
npm run compile
```

### Run Extension
1. Open `vscode-extension` in VS Code
2. Press **F5**

### Use Extension
1. Open a Git repository
2. Open a file
3. Run "ContextWeave: Explain this file"

---

**Need help?** Check `TROUBLESHOOTING.md` or open an issue on GitHub.
