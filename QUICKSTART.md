# ContextWeave Lite - Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Start the Backend (2 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key (or skip for mock mode)
# Windows PowerShell:
$env:LLM_API_KEY="sk-your-key-here"
# macOS/Linux:
export LLM_API_KEY="sk-your-key-here"

# Start the server
python main.py
```

✅ Backend should now be running at `http://localhost:8000`

Test it: Open `http://localhost:8000/health` in your browser

## Step 2: Install VS Code Extension (2 minutes)

```bash
# Open a new terminal (keep backend running)
cd vscode-extension

# Install dependencies
npm install

# Compile TypeScript
npm run compile
```

## Step 3: Run the Extension (1 minute)

1. Open the `vscode-extension` folder in VS Code
2. Press `F5` (or Run > Start Debugging)
3. A new VS Code window opens with the extension loaded

## Step 4: Try It Out!

In the Extension Development Host window:

1. **Open a Git repository** (any project with Git history)
2. **Open a file** that has some commits
3. **Open Command Palette**: `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
4. **Type**: `ContextWeave: Explain this file`
5. **Press Enter**

The ContextWeave sidebar will open showing:
- 📄 What this file does
- 🔍 Key design decisions
- 📚 Related files to read

## Optional: Test with Selected Code

1. Select a few lines of code in the editor
2. Run `ContextWeave: Explain this file` again
3. You'll get an additional explanation of the selected code

## Troubleshooting

**"Cannot connect to backend"**
- Make sure backend is running: `http://localhost:8000/health`
- Check terminal for errors

**"No commit history found"**
- Make sure the file has been committed to Git
- Try a different file with more commits

**"Mock response" warning**
- You haven't set `LLM_API_KEY`
- The extension works but uses mock data
- Set the API key to get real AI analysis

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Configure settings in VS Code (search "ContextWeave")
- Try different files and repositories
- Check [design.md](design.md) for architecture details

## Getting an OpenAI API Key

1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and set as `LLM_API_KEY`

**Note**: OpenAI charges per API call. GPT-3.5-turbo is cheaper than GPT-4.

## Alternative: Use Compatible APIs

ContextWeave works with any OpenAI-compatible API:

```bash
# Azure OpenAI
export LLM_API_KEY="your-azure-key"
export LLM_API_BASE="https://your-resource.openai.azure.com/openai/deployments/your-deployment"
export LLM_MODEL="gpt-35-turbo"

# Local models (e.g., LM Studio, Ollama with OpenAI compatibility)
export LLM_API_KEY="not-needed"
export LLM_API_BASE="http://localhost:1234/v1"
export LLM_MODEL="local-model"
```

Happy coding! 🚀
