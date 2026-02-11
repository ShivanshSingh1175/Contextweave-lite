"""
Base abstract class for LLM providers
All LLM providers must implement this interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict
from schemas import ContextResponse


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, config: Dict):
        """
        Initialize provider with configuration
        
        Args:
            config: Dictionary containing provider-specific configuration
        """
        self.config = config
    
    @abstractmethod
    async def generate(
        self,
        file_path: str,
        file_content: str,
        commits: List[Dict],
        related_files_data: Dict,
        selected_code: str = None
    ) -> ContextResponse:
        """
        Generate analysis for a file
        
        Args:
            file_path: Path to the file being analyzed
            file_content: Content of the file
            commits: List of commit history
            related_files_data: Dictionary with imports and co-changed files
            selected_code: Optional selected code snippet
            
        Returns:
            ContextResponse with analysis results
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is available and configured
        
        Returns:
            True if provider can be used, False otherwise
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this provider
        
        Returns:
            Provider name as string
        """
        pass
