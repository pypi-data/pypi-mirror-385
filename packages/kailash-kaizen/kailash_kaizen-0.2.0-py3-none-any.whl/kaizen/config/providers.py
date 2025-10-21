"""
Model Provider Configuration System for Kaizen

Provides unified configuration and auto-detection for:
- OpenAI (gpt-4o-mini - fast, cost-effective)
- Ollama (llama3.2 and other local models)

Implements smart provider detection based on environment and supports
explicit configuration when needed.
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

logger = logging.getLogger(__name__)


ProviderType = Literal["openai", "ollama", "anthropic"]


@dataclass
class ProviderConfig:
    """Configuration for a specific LLM provider."""

    provider: ProviderType
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3


class ConfigurationError(Exception):
    """Raised when provider configuration is invalid or unavailable."""

    pass


def check_ollama_available() -> bool:
    """
    Check if Ollama is available locally.

    Returns:
        bool: True if Ollama is accessible, False otherwise
    """
    try:
        import requests

        # Check if Ollama is running on default port
        response = requests.get("http://localhost:11434/api/tags", timeout=1)
        return response.status_code == 200
    except Exception:
        return False


def get_openai_config(model: Optional[str] = None) -> ProviderConfig:
    """
    Get OpenAI provider configuration.

    Args:
        model: Optional model override (default: gpt-4o-mini)

    Returns:
        ProviderConfig for OpenAI

    Raises:
        ConfigurationError: If API key is not available
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ConfigurationError(
            "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
        )

    default_model = "gpt-4o-mini"  # Fast, cost-effective model
    return ProviderConfig(
        provider="openai",
        model=model or os.getenv("KAIZEN_OPENAI_MODEL", default_model),
        api_key=api_key,
        timeout=int(os.getenv("KAIZEN_TIMEOUT", "30")),
        max_retries=int(os.getenv("KAIZEN_MAX_RETRIES", "3")),
    )


def get_ollama_config(model: Optional[str] = None) -> ProviderConfig:
    """
    Get Ollama provider configuration.

    Args:
        model: Optional model override (default: llama3.2)

    Returns:
        ProviderConfig for Ollama

    Raises:
        ConfigurationError: If Ollama is not available
    """
    if not check_ollama_available():
        raise ConfigurationError(
            "Ollama is not available. Install and start Ollama: https://ollama.ai"
        )

    default_model = "llama3.2"  # Using llama3.2 as it's more commonly available
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    return ProviderConfig(
        provider="ollama",
        model=model or os.getenv("KAIZEN_OLLAMA_MODEL", default_model),
        base_url=base_url,
        timeout=int(os.getenv("KAIZEN_TIMEOUT", "60")),  # Ollama may need more time
        max_retries=int(os.getenv("KAIZEN_MAX_RETRIES", "3")),
    )


def auto_detect_provider(preferred: Optional[ProviderType] = None) -> ProviderConfig:
    """
    Auto-detect available LLM provider.

    Detection order (if preferred not specified):
    1. OpenAI (if OPENAI_API_KEY is set)
    2. Ollama (if running locally)

    Args:
        preferred: Optional preferred provider to try first

    Returns:
        ProviderConfig for first available provider

    Raises:
        ConfigurationError: If no provider is available
    """
    # Check for explicit override
    explicit_provider = os.getenv("KAIZEN_DEFAULT_PROVIDER")
    if explicit_provider:
        preferred = explicit_provider.lower()

    # Try preferred provider first
    if preferred == "openai":
        try:
            return get_openai_config()
        except ConfigurationError:
            logger.warning(
                "Preferred provider OpenAI not available, trying alternatives"
            )

    elif preferred == "ollama":
        try:
            return get_ollama_config()
        except ConfigurationError:
            logger.warning(
                "Preferred provider Ollama not available, trying alternatives"
            )

    # Auto-detect in order of preference
    # 1. Try OpenAI first (production-ready)
    try:
        config = get_openai_config()
        logger.info(f"Auto-detected provider: OpenAI (model: {config.model})")
        return config
    except ConfigurationError:
        logger.debug("OpenAI not available, trying Ollama")

    # 2. Try Ollama (local development)
    try:
        config = get_ollama_config()
        logger.info(f"Auto-detected provider: Ollama (model: {config.model})")
        return config
    except ConfigurationError:
        logger.debug("Ollama not available")

    # No provider available
    raise ConfigurationError(
        "No LLM provider available. Please either:\n"
        "  1. Set OPENAI_API_KEY environment variable for OpenAI, or\n"
        "  2. Install and start Ollama (https://ollama.ai) for local models"
    )


def get_provider_config(
    provider: Optional[ProviderType] = None, model: Optional[str] = None
) -> ProviderConfig:
    """
    Get provider configuration with auto-detection support.

    Args:
        provider: Optional explicit provider selection
        model: Optional model override

    Returns:
        ProviderConfig for requested or auto-detected provider

    Examples:
        >>> # Auto-detect provider
        >>> config = get_provider_config()

        >>> # Explicit provider
        >>> config = get_provider_config(provider="openai")

        >>> # Custom model
        >>> config = get_provider_config(provider="ollama", model="llama3.2")
    """
    if provider == "openai":
        return get_openai_config(model)
    elif provider == "ollama":
        return get_ollama_config(model)
    else:
        # Auto-detect
        return auto_detect_provider(preferred=provider)


def provider_config_to_dict(config: ProviderConfig) -> Dict[str, Any]:
    """
    Convert ProviderConfig to dictionary suitable for Kaizen agent configuration.

    Args:
        config: ProviderConfig object

    Returns:
        Dict with provider configuration suitable for agent creation
    """
    config_dict = {
        "provider": config.provider,
        "model": config.model,
        "timeout": config.timeout,
    }

    # Add provider-specific fields
    if config.api_key:
        config_dict["api_key"] = config.api_key
    if config.base_url:
        config_dict["base_url"] = config.base_url

    # Add generation config
    config_dict["generation_config"] = {
        "max_retries": config.max_retries,
    }

    return config_dict


# Convenience function for examples
def get_default_model_config() -> Dict[str, Any]:
    """
    Get default model configuration for Kaizen examples.

    Auto-detects available provider and returns configuration dict
    ready for use with kaizen.create_agent().

    Returns:
        Dict with model configuration

    Examples:
        >>> import kaizen
        >>> from kaizen.config.providers import get_default_model_config
        >>>
        >>> config = get_default_model_config()
        >>> agent = kaizen.create_agent("my_agent", config=config)
    """
    provider_config = auto_detect_provider()
    return provider_config_to_dict(provider_config)
