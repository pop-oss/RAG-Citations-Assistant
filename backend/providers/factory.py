"""Provider factory with fallback chain support."""
from typing import Optional, List

from config import settings
from providers.base import ChatProvider, EmbeddingProvider
from providers.deepseek import DeepSeekProvider
from providers.qwen import QwenProvider
from providers.zhipu import ZhipuChatProvider, ZhipuEmbeddingProvider


# Singleton instances cache
_embedding_provider: Optional[EmbeddingProvider] = None


def get_chat_provider(provider_name: Optional[str] = None) -> ChatProvider:
    """
    Get a chat provider by name with fallback support.
    
    Args:
        provider_name: One of 'deepseek', 'qwen', 'zhipu', or None for default
        
    Returns:
        ChatProvider instance
        
    Raises:
        ValueError: If no provider could be initialized
    """
    if provider_name is None:
        provider_name = settings.default_chat_provider
    
    # Build fallback chain
    fallback_chain = settings.chat_fallback_chain.split(",")
    
    # Ensure requested provider is first
    if provider_name in fallback_chain:
        fallback_chain.remove(provider_name)
    fallback_chain.insert(0, provider_name)
    
    # Try each provider in the chain
    errors = []
    for name in fallback_chain:
        try:
            provider = _create_chat_provider(name.strip())
            if provider:
                return provider
        except Exception as e:
            errors.append(f"{name}: {e}")
            continue
    
    raise ValueError(f"No chat provider available. Errors: {'; '.join(errors)}")


def _create_chat_provider(name: str) -> Optional[ChatProvider]:
    """Create a chat provider instance by name."""
    name = name.lower().strip()
    
    if name == "deepseek":
        return DeepSeekProvider()
    elif name == "qwen":
        return QwenProvider()
    elif name == "zhipu":
        return ZhipuChatProvider()
    else:
        raise ValueError(f"Unknown chat provider: {name}")


def get_embedding_provider() -> EmbeddingProvider:
    """
    Get the embedding provider (fixed to Zhipu as per contract).
    
    Returns:
        EmbeddingProvider instance (singleton)
        
    Raises:
        ValueError: If Zhipu embedding is not configured
    """
    global _embedding_provider
    
    if _embedding_provider is None:
        _embedding_provider = ZhipuEmbeddingProvider()
    
    return _embedding_provider


class FallbackChatProvider(ChatProvider):
    """
    Chat provider with automatic fallback.
    Tries providers in order until one succeeds.
    """
    
    def __init__(self, primary: str, fallback_chain: List[str]):
        self.providers = []
        
        # Build provider list
        all_providers = [primary] + [p for p in fallback_chain if p != primary]
        
        for name in all_providers:
            try:
                provider = _create_chat_provider(name)
                if provider:
                    self.providers.append((name, provider))
            except Exception:
                continue
        
        if not self.providers:
            raise ValueError("No chat providers available")
    
    async def stream_chat(self, messages: list, **kwargs):
        """Stream with fallback on error."""
        last_error = None
        
        for name, provider in self.providers:
            try:
                async for token in provider.stream_chat(messages, **kwargs):
                    yield token
                return  # Success
            except Exception as e:
                last_error = e
                continue
        
        raise last_error or ValueError("All providers failed")
    
    async def chat(self, messages: list, **kwargs) -> str:
        """Chat with fallback on error."""
        last_error = None
        
        for name, provider in self.providers:
            try:
                return await provider.chat(messages, **kwargs)
            except Exception as e:
                last_error = e
                continue
        
        raise last_error or ValueError("All providers failed")
