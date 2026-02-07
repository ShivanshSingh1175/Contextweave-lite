"""
LLM API client and prompt builder
Handles communication with OpenAI-compatible LLM APIs
"""
import os
import json
import logging
from typing import List, Dict, Optional
import httpx

from schemas import ContextResponse, DesignDecision, RelatedFile

logger = logging.getLogger(__name__)

# TODO: Set these environment variables before running:
# export LLM_API_KEY="your-api-key-here"
# export LLM_API_BASE="https://api.openai.com/v1"  # or compatible endpoint
# export LLM_MODEL="gpt-3.5-turbo"  # or gpt-4, claude-3-sonnet, etc.

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_API_BASE = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")


async def analyze_file_with_llm(
    file_path: str,
    file_content: str,
    commits: List[Dict],
    related_files_data: Dict,
    selected_code: Optional[str] = None
) -> ContextResponse:
    """
    Call LLM to analyze file and generate summary, design decisions, and related files
    
    Args:
        file_path: Path to the file being analyzed
        file_content: Content of the file
        commits: List of commit dictionaries
        related_files_data: Dict with 'imports' and 'co_changed' lists
        selected_code: Optional selected code snippet to explain
        
    Returns:
        ContextResponse with analysis results
    """
    if not LLM_API_KEY:
        logger.warning("LLM_API_KEY not set, returning mock response")
        return create_mock_response(file_path, commits, related_files_data, selected_code)
    
    # Build the prompt
    prompt = build_analysis_prompt(
        file_path=file_path,
        file_content=file_content,
        commits=commits,
        related_files_data=related_files_data,
        selected_code=selected_code
    )
    
    # Call LLM
    try:
        llm_response = await call_llm(prompt)
        
        # Parse LLM response into structured format
        response = parse_llm_response(llm_response, commits, related_files_data)
        
        return response
        
    except Exception as e:
        logger.error(f"Error calling LLM: {e}", exc_info=True)
        # Fallback to mock response on error
        return create_mock_response(file_path, commits, related_files_data, selected_code)


def build_analysis_prompt(
    file_path: str,
    file_content: str,
    commits: List[Dict],
    related_files_data: Dict,
    selected_code: Optional[str] = None
) -> str:
    """
    Build a structured prompt for the LLM
    
    Returns:
        Formatted prompt string
    """
    # Truncate file content if too long (keep first 6000 chars)
    if len(file_content) > 6000:
        file_content = file_content[:6000] + "\n\n... [File truncated for analysis] ..."
    
    # Format commits for prompt
    commits_text = ""
    if commits:
        commits_text = "\n".join([
            f"- {c['hash']} ({c['date'][:10]}, {c['author']}): {c['message'][:100]}"
            f" [{c['lines_changed']} lines changed]"
            for c in commits[:20]  # Use top 20 commits
        ])
    else:
        commits_text = "No commit history available for this file."
    
    # Format related files
    related_text = ""
    if related_files_data.get('imports'):
        related_text += "Imported files:\n"
        related_text += "\n".join([f"- {imp}" for imp in related_files_data['imports'][:5]])
    if related_files_data.get('co_changed'):
        related_text += "\n\nFrequently co-changed files:\n"
        related_text += "\n".join([
            f"- {item['path']} (changed together {item['frequency']} times)"
            for item in related_files_data['co_changed'][:5]
        ])
    
    # Determine weird_code_explanation value
    weird_code_value = '"Explanation of selected code"' if selected_code else 'null'
    
    # Build selected code section
    selected_code_section = ""
    if selected_code:
        selected_code_section = f"""4. Explain why this selected code might be unusual or noteworthy:
SELECTED CODE:
```
{selected_code}
```
"""
    
    # Build the main prompt
    prompt = f"""You are helping a junior developer understand a codebase.
Analyze this file and provide clear, concise insights.

FILE: {file_path}

FILE CONTENT:
```
{file_content}
```

RECENT COMMITS (last 20):
{commits_text}

RELATED FILES:
{related_text}

TASKS:
1. Summarize what this file does in 2-3 sentences (simple, clear language).

2. Extract 2-3 key design decisions from the commit history.
   For each decision:
   - Provide a short title (3-5 words)
   - Write a one-line description
   - Reference relevant commit hashes (use the short 7-char hashes shown above)
   
   If commit messages are too brief or unclear, say "Limited commit context available" instead of guessing.

3. Suggest 2-3 related files that a new developer should read next.
   Use the imports and co-changed files listed above.
   For each file, explain in one sentence why it's related.

{selected_code_section}

IMPORTANT:
- Be concise and clear
- Admit uncertainty when evidence is weak
- Use simple language suitable for junior developers
- Reference actual commit hashes when discussing decisions

OUTPUT FORMAT (JSON only, no markdown):
{{
  "summary": "2-3 sentence summary here",
  "decisions": [
    {{
      "title": "Short title",
      "description": "One-line explanation",
      "commits": ["abc123", "def456"]
    }}
  ],
  "related_files": [
    {{
      "path": "relative/path/to/file.py",
      "reason": "One sentence explaining the relationship"
    }}
  ],
  "weird_code_explanation": {weird_code_value}
}}"""
    
    return prompt


async def call_llm(prompt: str) -> dict:
    """
    Call OpenAI-compatible LLM API
    
    Args:
        prompt: The prompt to send to the LLM
        
    Returns:
        Parsed JSON response from LLM
    """
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a code analysis assistant. Always respond with valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,  # Low temperature for consistency
        "max_tokens": 1500
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{LLM_API_BASE}/chat/completions",
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Extract content from response
        content = result["choices"][0]["message"]["content"]
        
        # Parse JSON from content
        # Remove markdown code blocks if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        return json.loads(content)


def parse_llm_response(llm_response: dict, commits: List[Dict], related_files_data: Dict) -> ContextResponse:
    """
    Parse LLM JSON response into ContextResponse model
    
    Args:
        llm_response: Raw JSON response from LLM
        commits: Original commit data (for metadata)
        related_files_data: Original related files data (for metadata)
        
    Returns:
        ContextResponse object
    """
    # Extract fields with defaults
    summary = llm_response.get("summary", "No summary available")
    
    decisions = []
    for d in llm_response.get("decisions", []):
        decisions.append(DesignDecision(
            title=d.get("title", "Unknown decision"),
            description=d.get("description", "No description"),
            commits=d.get("commits", [])
        ))
    
    related_files = []
    for rf in llm_response.get("related_files", []):
        related_files.append(RelatedFile(
            path=rf.get("path", ""),
            reason=rf.get("reason", "Related file")
        ))
    
    weird_code_explanation = llm_response.get("weird_code_explanation")
    
    # Add metadata
    metadata = {
        "commits_analyzed": len(commits),
        "llm_model": LLM_MODEL,
        "has_commit_history": len(commits) > 0
    }
    
    return ContextResponse(
        summary=summary,
        decisions=decisions,
        related_files=related_files,
        weird_code_explanation=weird_code_explanation,
        metadata=metadata
    )


def create_mock_response(
    file_path: str,
    commits: List[Dict],
    related_files_data: Dict,
    selected_code: Optional[str] = None
) -> ContextResponse:
    """
    Create a mock response when LLM is not available
    Useful for testing without API key
    
    Returns:
        ContextResponse with mock data
    """
    logger.info("Creating mock response (LLM not configured)")
    
    file_name = os.path.basename(file_path)
    
    summary = f"This file ({file_name}) is part of the codebase. "
    summary += "Configure LLM_API_KEY environment variable to get AI-powered analysis. "
    summary += f"Found {len(commits)} commits in history."
    
    decisions = []
    if commits:
        # Create mock decisions from first few commits
        for i, commit in enumerate(commits[:2]):
            decisions.append(DesignDecision(
                title=f"Change in {commit['date'][:10]}",
                description=commit['message'][:80],
                commits=[commit['hash']]
            ))
    
    related_files = []
    # Add imports as related files
    for imp in related_files_data.get('imports', [])[:3]:
        related_files.append(RelatedFile(
            path=imp,
            reason="Imported by this file"
        ))
    # Add co-changed files
    for co in related_files_data.get('co_changed', [])[:2]:
        if len(related_files) < 3:
            related_files.append(RelatedFile(
                path=co['path'],
                reason=f"Changed together {co['frequency']} times"
            ))
    
    weird_explanation = None
    if selected_code:
        weird_explanation = "Configure LLM_API_KEY to get AI-powered code explanations."
    
    return ContextResponse(
        summary=summary,
        decisions=decisions,
        related_files=related_files,
        weird_code_explanation=weird_explanation,
        metadata={
            "commits_analyzed": len(commits),
            "llm_configured": False,
            "mock_response": True
        }
    )
