"""
Groq LLM Provider - Cloud-based LLM using Groq API
"""
import os
import logging
from typing import List, Dict, Optional
import instructor
from openai import AsyncOpenAI
import tiktoken

from .base_provider import LLMProvider
from schemas import ContextResponse, DesignDecision, RelatedFile

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    """Groq cloud LLM provider"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get('api_key') or os.getenv("LLM_API_KEY", "")
        self.api_base = config.get('api_base') or os.getenv("LLM_API_BASE", "https://api.groq.com/openai/v1")
        self.model = config.get('model') or os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        
        # Initialize Instructor client
        if self.api_key:
            self.client = instructor.patch(AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.api_base,
                timeout=30.0
            ))
        else:
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Groq provider is configured"""
        return bool(self.api_key and self.client)
    
    def get_provider_name(self) -> str:
        return "groq"
    
    async def generate(
        self,
        file_path: str,
        file_content: str,
        commits: List[Dict],
        related_files_data: Dict,
        selected_code: Optional[str] = None
    ) -> ContextResponse:
        """Generate analysis using Groq API"""
        
        if not self.is_available():
            logger.warning("Groq API key not configured")
            return self._create_mock_response(file_path, commits, related_files_data, selected_code)
        
        try:
            # Truncate content using tiktoken
            truncated_content = self._truncate_content_tokens(file_content, self.model)
            
            # Build messages
            messages = self._build_messages(
                file_path=file_path,
                file_content=truncated_content,
                commits=commits,
                related_files_data=related_files_data,
                selected_code=selected_code
            )
            
            # Call LLM with structured output
            logger.info(f"Calling Groq API: {self.api_base} with model {self.model}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                response_model=ContextResponse,
                messages=messages,
                temperature=0.3,
                max_retries=2,
            )
            
            # Add metadata
            response.metadata = {
                "commits_analyzed": len(commits),
                "llm_model": self.model,
                "llm_provider": "groq",
                "has_commit_history": len(commits) > 0,
            }
            
            logger.info("Groq API response received successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}", exc_info=True)
            return self._create_mock_response(file_path, commits, related_files_data, selected_code)
    
    def _truncate_content_tokens(self, content: str, model: str, max_tokens: int = 6000) -> str:
        """Truncate content to a specific number of tokens"""
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
    
    def _build_messages(
        self,
        file_path: str,
        file_content: str,
        commits: List[Dict],
        related_files_data: Dict,
        selected_code: Optional[str] = None
    ) -> List[Dict]:
        """Build messages for the chat completion"""
        
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

        system_prompt = """You are a senior developer assistant helping a junior engineer understand code.
Analyze the provided file, commit history, and context.
Provide clear, educational insights in simple language.
Focus on helping developers learn and understand design decisions.
Output must be valid JSON matching the schema."""

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

Analyze this file and provide:
1. A 2-3 sentence summary of what the file does
2. Key design decisions from commit history (0-3 items)
3. Related files developers should read next (0-3 items)
4. Explanation of selected code if provided
"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def _create_mock_response(
        self,
        file_path: str,
        commits: List[Dict],
        related_files_data: Dict,
        selected_code: Optional[str] = None
    ) -> ContextResponse:
        """Create a mock response when LLM is not available"""
        logger.info("Creating mock response (Groq not configured)")
        
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
        for imp in related_files_data.get('imports', [])[:3]:
            related_files.append(RelatedFile(
                path=imp,
                reason="Imported by this file"
            ))
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
                "llm_provider": "groq",
                "llm_configured": False,
                "mock_response": True
            }
        )
