# ContextWeave Lite

AI-powered code context assistant for VS Code that helps developers understand files by analyzing code and Git history.

## Features

For any file in a Git repository, ContextWeave Lite provides:

1. **Summary** - What the file does in 2-3 sentences
2. **Design Decisions** - Key decisions extracted from Git commit history
3. **Related Files** - Files you should read next (based on imports and co-changes)
4. **Code Explanations** - Optional explanations for selected code snippets

## Architecture

- **Backend**: FastAPI (Python 3.11) - Analyzes Git history and calls LLM APIs
- **Frontend**: VS Code Extension (TypeScript) - Provides UI and commands
- **LLM**: OpenAI-compatible API for AI-powered analysis

## Project Structure

```
contextweave-lite/
├── backend/
│   ├── main.py              # FastAPI app and endpoints
│   ├── git_utils.py         # Git operations with GitPython
│   ├── llm_client.py        # LLM API client and prompts
│   ├── schemas.py           # Pydantic models
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
├── vscode-extension/
│   ├── src/
│   │   ├── extension.ts     # Extension entry point
│   │   ├── apiClient.ts     # Backend API client
│   │   └── sidebarProvider.ts  # Sidebar webview UI
│   ├── package.json         # Extension manifest
│   └── tsconfig.json        # TypeScript config
├── requirements.md          # Product requirements
├── design.md                # Technical design
└── README.md                # This file
```

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- VS Code 1.85 or higher
- Git repository to analyze
- OpenAI API key (or compatible LLM API)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy example file
   cp .env.example .env
   
   # Edit .env and add your API key:
   # LLM_API_KEY=sk-your-openai-api-key-here
   # LLM_API_BASE=https://api.openai.com/v1
   # LLM_MODEL=gpt-3.5-turbo
   ```

   Or set environment variables directly:
   ```bash
   # On Windows (PowerShell):
   $env:LLM_API_KEY="sk-your-key-here"
   $env:LLM_API_BASE="https://api.openai.com/v1"
   $env:LLM_MODEL="gpt-3.5-turbo"
   
   # On macOS/Linux:
   export LLM_API_KEY="sk-your-key-here"
   export LLM_API_BASE="https://api.openai.com/v1"
   export LLM_MODEL="gpt-3.5-turbo"
   ```

5. **Run the backend**
   ```bash
   python main.py
   ```

   The backend will start on `http://localhost:8000`

   You can test it by visiting: `http://localhost:8000/health`

### VS Code Extension Setup

1. **Navigate to extension directory**
   ```bash
   cd vscode-extension
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Compile TypeScript**
   ```bash
   npm run compile
   ```

4. **Run extension in development mode**
   - Open the `vscode-extension` folder in VS Code
   - Press `F5` to launch Extension Development Host
   - A new VS Code window will open with the extension loaded

### Using the Extension

1. **Open a Git repository** in VS Code

2. **Open any file** in the repository

3. **Run the command**:
   - Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
   - Type: `ContextWeave: Explain this file`
   - Press Enter

4. **View results** in the ContextWeave sidebar

5. **Optional**: Select code and run the command to get explanations for specific code snippets

## Configuration

### Backend Configuration

Edit `.env` file or set environment variables:

- `LLM_API_KEY` - Your LLM API key (required for AI analysis)
- `LLM_API_BASE` - API endpoint (default: `https://api.openai.com/v1`)
- `LLM_MODEL` - Model to use (default: `gpt-3.5-turbo`)
- `PORT` - Backend port (default: `8000`)

### VS Code Extension Configuration

Open VS Code Settings and search for "ContextWeave":

- `contextweave.backendUrl` - Backend URL (default: `http://localhost:8000`)
- `contextweave.commitLimit` - Max commits to analyze (default: `50`)

## Testing Without LLM API Key

The backend will work without an LLM API key, but will return mock responses:

- Summary will be generic
- Design decisions will be raw commit messages
- Related files will be based on imports and co-changes only

This is useful for testing the integration without API costs.

## API Endpoints

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "llm_configured": true,
  "version": "0.1.0"
}
```

### `POST /context/file`
Analyze a file and return context

**Request:**
```json
{
  "repo_path": "/absolute/path/to/repo",
  "file_path": "/absolute/path/to/file.py",
  "selected_code": "optional code snippet",
  "commit_limit": 50
}
```

**Response:**
```json
{
  "summary": "This file handles...",
  "decisions": [
    {
      "title": "Migrated to async",
      "description": "Refactored to use async/await for better performance",
      "commits": ["abc123", "def456"]
    }
  ],
  "related_files": [
    {
      "path": "src/utils/helper.py",
      "reason": "Imported by this file"
    }
  ],
  "weird_code_explanation": "This code handles edge case X...",
  "metadata": {
    "commits_analyzed": 47,
    "llm_configured": true
  }
}
```

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (should be 3.11+)
- Verify virtual environment is activated
- Check if port 8000 is already in use

### Extension can't connect to backend
- Ensure backend is running: visit `http://localhost:8000/health`
- Check `contextweave.backendUrl` setting in VS Code
- Look for CORS errors in browser console (F12 in webview)

### No commit history found
- Ensure file is in a Git repository
- Check if file has been committed (not just added)
- Try with a file that has multiple commits

### LLM API errors
- Verify `LLM_API_KEY` is set correctly
- Check API quota/rate limits
- Review backend logs for detailed error messages

## Development

### Backend Development

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run with auto-reload
python main.py

# Run tests (if added)
pytest
```

### Extension Development

```bash
cd vscode-extension

# Watch mode (auto-compile on changes)
npm run watch

# Then press F5 in VS Code to launch Extension Development Host
```

## Future Enhancements

- Multi-language UI (Hindi, Tamil, Telugu)
- Chat interface for follow-up questions
- Architecture visualization
- Team collaboration features
- Custom prompt templates
- Offline mode with caching

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.

## Acknowledgments

- Built with FastAPI, GitPython, and VS Code Extension API
- Requirements and design generated with Kiro AI Assistant
- Part of the "AI for Bharat - Learning & Developer Productivity" initiative
