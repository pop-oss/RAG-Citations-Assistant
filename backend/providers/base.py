"""Base classes for LLM providers."""
from abc import ABC, abstractmethod
from typing import List, AsyncGenerator


class ChatProvider(ABC):
    """Abstract base class for chat/completion providers."""
    
    @abstractmethod
    async def stream_chat(
        self, 
        messages: List[dict],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion tokens.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Yields:
            Individual tokens as they are generated
        """
        pass
    
    @abstractmethod
    async def chat(self, messages: List[dict], **kwargs) -> str:
        """
        Non-streaming chat completion.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Complete response text
        """
        pass


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the embedding dimension."""
        pass
