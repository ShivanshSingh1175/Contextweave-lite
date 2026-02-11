"""
LLM Provider Factory
Selects and instantiates the appropriate LLM provider based on configuration
"""
import os
import logging
from typing import Dict, Optional

from .base_provider import LLMProvider
from .groq_provider import GroqProvider
from .ollama_provider import OllamaProvider
from .localai_provider import LocalAIProvider

logger = logging.getLogger(__name__)


def get_llm_provider(provider_name: Optional[str] = None, config: Optional[Dict] = None) -> LLMProvider:
    """
    Get LLM provider instance based on configuration
    
    Args:
        provider_name: Name of provider ("groq", "ollama", "localai")
                      If None, reads from LLM_PROVIDER env var or defaults to "groq"
        config: Optional configuration dictionary for the provider
        
    Returns:
        LLMProvider instance
        
    Raises:
        ValueError: If provider name is invalid
    """
    if config is None:
        config = {}
    
    # Determine provider name
    if provider_name is None:
        provider_name = os.getenv("LLM_PROVIDER", "groq").lower()
    else:
        provider_name = provider_name.lower()
    
    logger.info(f"Initializing LLM provider: {provider_name}")
    
    # Instantiate provider
    if provider_name == "groq":
        return GroqProvider(config)
    elif provider_name == "ollama":
        return OllamaProvider(config)
    elif provider_name == "localai":
        return LocalAIProvider(config)
    else:
        logger.warning(f"Unknown provider '{provider_name}', falling back to Groq")
        return GroqProvider(config)


def get_available_providers() -> Dict[str, bool]:
    """
    Check which providers are available
    
    Returns:
        Dictionary mapping provider names to availability status
    """
    providers = {
        "groq": GroqProvider({}).is_available(),
        "ollama": OllamaProvider({}).is_available(),
        "localai": LocalAIProvider({}).is_available(),
    }
    
    logger.info(f"Provider availability: {providers}")
    return providers
