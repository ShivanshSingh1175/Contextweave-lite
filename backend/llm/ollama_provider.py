"""
Ollama LLM Provider - Local LLM using Ollama
"""
import os
import logging
import json
from typing import List, Dict, Optional
import httpx

from .base_provider import LLMProvider
from schemas import ContextResponse, DesignDecision, RelatedFile

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_base = config.get('api_base', 'http://localhost:11434')
        self.model = config.get('model', 'llama3')
        self.timeout = config.get('timeout', 60.0)
    
    def is_available(self) -> bool:
        """Check if Ollama server is running"""
        try:
            import asyncio
            # Try to connect to Ollama server
            async def check():
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{self.api_base}/api/tags")
                    return response.status_code == 200
            
            # Run async check
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(check())
            loop.close()
            return result
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            return False
    
    def get_provider_name(self) -> str:
        return "ollama"
    
    async def generate(
        self,
        file_path: str,
        file_content: str,
        commits: List[Dict],
        related_files_data: Dict,
        selected_code: Optional[str] = None
    ) -> ContextResponse:
        """Generate analysis using Ollama API"""
        
        try:
            # Build prompt
            prompt = self._build_prompt(
                file_path=file_path,
                file_content=file_content[:8000],  # Truncate to reasonable size
                commits=commits,
                related_files_data=related_files_data,
                selected_code=selected_code
            )
            
            # Call Ollama API
            logger.info(f"Calling Ollama API: {self.api_base} with model {self.model}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_base}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"Ollama API returned status {response.status_code}: {response.text}")
                
                result = response.json()
                llm_response = result.get('response', '')
                
                # Parse JSON response
                try:
                    parsed = json.loads(llm_response)
                    return self._parse_response(parsed, commits, file_path)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse Ollama JSON response, using fallback")
                    return self._create_fallback_response(file_path, commits, related_files_data, selected_code)
            
        except httpx.ConnectError:
            logger.error("Cannot connect to Ollama server. Is it running?")
            raise Exception("Local LLM server not running. Please start Ollama with: ollama serve")
        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            raise Exception("Local LLM server timed out. Try a smaller file or faster model.")
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}", exc_info=True)
            raise Exception(f"Ollama error: {str(e)}")
    
    def _build_prompt(
        self,
        file_path: str,
        file_content: str,
        commits: List[Dict],
        related_files_data: Dict,
        selected_code: Optional[str] = None
    ) -> str:
        """Build prompt for Ollama"""
        
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
            selected_section = f"\n\nUSER SELECTED CODE:\n{selected_code}\n\nExplain this code in 'weird_code_explanation'."
        
        prompt = f"""You are a code analysis assistant. Analyze this file and respond with ONLY valid JSON.

FILE: {file_path}

CONTENT:
{file_content}

COMMITS:
{commits_text}

RELATED:
{related_text}
{selected_section}

Respond with JSON in this exact format:
{{
  "summary": "2-3 sentence summary of what this file does",
  "decisions": [
    {{"title": "Decision name", "description": "One sentence", "commits": ["hash1"]}}
  ],
  "related_files": [
    {{"path": "file.py", "reason": "Why it's related"}}
  ],
  "weird_code_explanation": "Explanation if code was selected, otherwise null"
}}

Respond with ONLY the JSON, no other text."""
        
        return prompt
    
    def _parse_response(self, parsed: Dict, commits: List[Dict], file_path: str) -> ContextResponse:
        """Parse Ollama JSON response into ContextResponse"""
        
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
                "llm_provider": "ollama",
                "has_commit_history": len(commits) > 0,
            }
        )
    
    def _create_fallback_response(
        self,
        file_path: str,
        commits: List[Dict],
        related_files_data: Dict,
        selected_code: Optional[str] = None
    ) -> ContextResponse:
        """Create fallback response when parsing fails"""
        
        file_name = os.path.basename(file_path)
        summary = f"This file ({file_name}) contains code. Ollama response could not be parsed properly."
        
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
            summary=summary,
            decisions=decisions,
            related_files=related_files,
            weird_code_explanation=None,
            metadata={
                "commits_analyzed": len(commits),
                "llm_provider": "ollama",
                "llm_model": self.model,
                "parse_error": True
            }
        )
