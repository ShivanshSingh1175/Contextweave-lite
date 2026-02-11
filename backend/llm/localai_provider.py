"""
LocalAI LLM Provider - Local LLM using LocalAI (OpenAI-compatible)
"""
import os
import logging
from typing import List, Dict, Optional
import httpx
from openai import AsyncOpenAI

from .base_provider import LLMProvider
from schemas import ContextResponse, DesignDecision, RelatedFile

logger = logging.getLogger(__name__)


class LocalAIProvider(LLMProvider):
    """LocalAI provider (OpenAI-compatible local server)"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_base = config.get('api_base', 'http://localhost:8080/v1')
        self.model = config.get('model', 'gpt-3.5-turbo')  # LocalAI model name
        self.timeout = config.get('timeout', 60.0)
        
        # Initialize OpenAI client (LocalAI is compatible)
        self.client = AsyncOpenAI(
            api_key="not-needed",  # LocalAI doesn't require API key
            base_url=self.api_base,
            timeout=self.timeout
        )
    
    def is_available(self) -> bool:
        """Check if LocalAI server is running"""
        try:
            import asyncio
            async def check():
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{self.api_base}/models")
                    return response.status_code == 200
            
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(check())
            loop.close()
            return result
        except Exception as e:
            logger.debug(f"LocalAI not available: {e}")
            return False
    
    def get_provider_name(self) -> str:
        return "localai"
    
    async def generate(
        self,
        file_path: str,
        file_content: str,
        commits: List[Dict],
        related_files_data: Dict,
        selected_code: Optional[str] = None
    ) -> ContextResponse:
        """Generate analysis using LocalAI API"""
        
        try:
            # Build messages
            messages = self._build_messages(
                file_path=file_path,
                file_content=file_content[:8000],  # Truncate to reasonable size
                commits=commits,
                related_files_data=related_files_data,
                selected_code=selected_code
            )
            
            # Call LocalAI API
            logger.info(f"Calling LocalAI API: {self.api_base} with model {self.model}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Try to parse as structured response
            import json
            try:
                parsed = json.loads(content)
                return self._parse_response(parsed, commits, file_path)
            except json.JSONDecodeError:
                # If not JSON, treat as summary
                logger.warning("LocalAI response not JSON, using as summary")
                return self._create_text_response(content, file_path, commits, related_files_data)
            
        except httpx.ConnectError:
            logger.error("Cannot connect to LocalAI server. Is it running?")
            raise Exception("Local LLM server not running. Please start LocalAI with: docker run -p 8080:8080 localai/localai")
        except httpx.TimeoutException:
            logger.error("LocalAI request timed out")
            raise Exception("Local LLM server timed out. Try a smaller file or faster model.")
        except Exception as e:
            logger.error(f"Error calling LocalAI API: {e}", exc_info=True)
            raise Exception(f"LocalAI error: {str(e)}")
    
    def _build_messages(
        self,
        file_path: str,
        file_content: str,
        commits: List[Dict],
        related_files_data: Dict,
        selected_code: Optional[str] = None
    ) -> List[Dict]:
        """Build messages for LocalAI chat completion"""
        
        # Format commits
        commits_text = "No commit history available."
        if commits:
            commits_text = "\n".join([
                f"- {c['hash'][:8]} ({c['date'][:10]}): {c['message'][:80]}"
                for c in commits[:15]
            ])
        
        # Format related files
        related_text = ""
        if related_files_data.get('imports'):
            related_text += "Imports: " + ", ".join(related_files_data['imports'][:5])
        if related_files_data.get('co_changed'):
            related_text += "\nCo-changed: " + ", ".join([
                f"{item['path']} ({item['frequency']}x)"
                for item in related_files_data['co_changed'][:3]
            ])
        
        selected_section = ""
        if selected_code:
            selected_section = f"\n\nUSER SELECTED CODE:\n{selected_code}\n\nExplain this code."
        
        system_prompt = """You are a code analysis assistant. Analyze files and provide insights.
Respond with JSON in this format:
{
  "summary": "2-3 sentence summary",
  "decisions": [{"title": "...", "description": "...", "commits": ["..."]}],
  "related_files": [{"path": "...", "reason": "..."}],
  "weird_code_explanation": "... or null"
}"""
        
        user_prompt = f"""FILE: {file_path}

CONTENT:
{file_content}

COMMITS:
{commits_text}

RELATED:
{related_text}
{selected_section}

Analyze and respond with JSON only."""
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def _parse_response(self, parsed: Dict, commits: List[Dict], file_path: str) -> ContextResponse:
        """Parse LocalAI JSON response into ContextResponse"""
        
        decisions = []
        for d in parsed.get('decisions', [])[:3]:
            decisions.append(DesignDecision(
                title=d.get('title', 'Design Decision'),
                description=d.get('description', ''),
                commits=d.get('commits', [])
            ))
        
        related_files = []
        for r in parsed.get('related_files', [])[:3]:
            related_files.append(RelatedFile(
                path=r.get('path', ''),
                reason=r.get('reason', '')
            ))
        
        return ContextResponse(
            summary=parsed.get('summary', 'Analysis completed.'),
            decisions=decisions,
            related_files=related_files,
            weird_code_explanation=parsed.get('weird_code_explanation'),
            metadata={
                "commits_analyzed": len(commits),
                "llm_model": self.model,
                "llm_provider": "localai",
                "has_commit_history": len(commits) > 0,
            }
        )
    
    def _create_text_response(
        self,
        content: str,
        file_path: str,
        commits: List[Dict],
        related_files_data: Dict
    ) -> ContextResponse:
        """Create response from plain text (non-JSON) response"""
        
        decisions = []
        if commits:
            decisions.append(DesignDecision(
                title="Recent Changes",
                description=commits[0]['message'][:80],
                commits=[commits[0]['hash']]
            ))
        
        related_files = []
        for imp in related_files_data.get('imports', [])[:3]:
            related_files.append(RelatedFile(
                path=imp,
                reason="Imported by this file"
            ))
        
        return ContextResponse(
            summary=content[:300] if content else "Analysis completed.",
            decisions=decisions,
            related_files=related_files,
            weird_code_explanation=None,
            metadata={
                "commits_analyzed": len(commits),
                "llm_provider": "localai",
                "llm_model": self.model,
                "text_response": True
            }
        )
