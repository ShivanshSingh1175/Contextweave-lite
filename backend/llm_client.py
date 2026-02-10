"""
LLM API client and prompt builder using Instructor for structured output
Handles communication with OpenAI-compatible LLM APIs
"""
import os
import logging
from typing import List, Dict, Optional
import instructor
from openai import AsyncOpenAI
import tiktoken

from schemas import ContextResponse, DesignDecision, RelatedFile

logger = logging.getLogger(__name__)

# Environment variables
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_API_BASE = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

# Initialize Instructor client
if LLM_API_KEY:
    aclient = instructor.patch(AsyncOpenAI(
        api_key=LLM_API_KEY,
        base_url=LLM_API_BASE
    ))
else:
    aclient = None


async def analyze_file_with_llm(
    file_path: str,
    file_content: str,
    commits: List[Dict],
    related_files_data: Dict,
    selected_code: Optional[str] = None
) -> ContextResponse:
    """
    Call LLM to analyze file and generate summary, design decisions, and related files
    Uses Instructor for structured JSON output.
    """
    if not aclient:
        logger.warning("LLM_API_KEY not set, returning mock response")
        return create_mock_response(file_path, commits, related_files_data, selected_code)
    
    # 1. Truncate content using tiktoken
    truncated_content = truncate_content_tokens(file_content, LLM_MODEL)
    
    # 2. Build the system and user messages
    messages = build_messages(
        file_path=file_path,
        file_content=truncated_content,
        commits=commits,
        related_files_data=related_files_data,
        selected_code=selected_code
    )
    
    # 3. Call LLM with structured output
    try:
        logger.info(f"Calling LLM API: {LLM_API_BASE} with model {LLM_MODEL} (Instructor)")
        
        response = await aclient.chat.completions.create(
            model=LLM_MODEL,
            response_model=ContextResponse,
            messages=messages,
            temperature=0.3,
            max_retries=2,
        )
        
        # Add metadata manually since it's not part of LLM generation usually
        response.metadata = {
            "commits_analyzed": len(commits),
            "llm_model": LLM_MODEL,
            "has_commit_history": len(commits) > 0,
            "tokens_used": "unknown" # Instructor abstracts this, could get from raw response if needed
        }
        
        logger.info("LLM response received and parsed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error calling LLM: {e}", exc_info=True)
        # Fallback to mock response on error
        return create_mock_response(file_path, commits, related_files_data, selected_code)


def truncate_content_tokens(content: str, model: str, max_tokens: int = 6000) -> str:
    """
    Truncate content to a specific number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    tokens = encoding.encode(content)
    
    if len(tokens) <= max_tokens:
        return content
    
    logger.info(f"Truncating file content from {len(tokens)} to {max_tokens} tokens")
    truncated_tokens = tokens[:max_tokens]
    return encoding.decode(truncated_tokens) + "\n... [File truncated for analysis] ..."


def build_messages(
    file_path: str,
    file_content: str,
    commits: List[Dict],
    related_files_data: Dict,
    selected_code: Optional[str] = None
) -> List[Dict]:
    """
    Build messages for the chat completion
    """
    # Format commits
    commits_text = "No commit history available for this file."
    if commits:
        commits_text = "\n".join([
            f"- {c['hash']} ({c['date'][:10]}, {c['author']}): {c['message'][:100]}"
            f" [{c['lines_changed']} lines changed]"
            for c in commits[:20]
        ])
    
    # Format related files
    related_text = ""
    if related_files_data.get('imports'):
        related_text += "Imported files:\n" + "\n".join([f"- {imp}" for imp in related_files_data['imports'][:5]])
    if related_files_data.get('co_changed'):
        related_text += "\n\nFrequently co-changed files:\n" + "\n".join([
            f"- {item['path']} (changed together {item['frequency']} times)"
            for item in related_files_data['co_changed'][:5]
        ])
    
    # Selected code section
    selected_code_section = ""
    if selected_code:
        selected_code_section = f"""
USER SELECTED CODE:
The user has highlighted this specific code block for explanation:
```
{selected_code}
```
Please explain why this code might be unusual or noteworthy in the 'weird_code_explanation' field.
"""

    system_prompt = """You are a senior developer assistant helping a junior engineer. 
Analyze the provided file, commit history, and context. 
Provide clear, educational insights. 
Output must be a valid JSON matching the schema."""

    user_prompt = f"""
FILE: {file_path}

FILE CONTENT:
```
{file_content}
```

RECENT COMMITS:
{commits_text}

RELATED FILES:
{related_text}

{selected_code_section}

Please analyze this file and return the summary, design decisions, related files advice, and code explanation.
"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]


def create_mock_response(
    file_path: str,
    commits: List[Dict],
    related_files_data: Dict,
    selected_code: Optional[str] = None
) -> ContextResponse:
    """
    Create a mock response when LLM is not available
    """
    logger.info("Creating mock response (LLM not configured)")
    
    file_name = os.path.basename(file_path)
    
    summary = f"This file ({file_name}) is part of the codebase. "
    summary += "Configure LLM_API_KEY environment variable to get AI-powered analysis. "
    summary += f"Found {len(commits)} commits in history."
    
    decisions = []
    if commits:
        for commit in commits[:2]:
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
