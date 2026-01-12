"""Zhipu AI provider implementation (Chat + Embedding)."""
import json
from typing import List, AsyncGenerator

import httpx

from config import settings
from providers.base import ChatProvider, EmbeddingProvider


class ZhipuChatProvider(ChatProvider):
    """Zhipu AI chat provider (GLM models)."""
    
    def __init__(self):
        self.api_key = settings.zhipu_api_key
        self.base_url = settings.zhipu_base_url
        self.model = settings.zhipu_chat_model
        
        if not self.api_key:
            raise ValueError("ZHIPU_API_KEY not configured")
    
    async def stream_chat(
        self, 
        messages: List[dict],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion from Zhipu API."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(data)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
    
    async def chat(self, messages: List[dict], **kwargs) -> str:
        """Non-streaming chat completion."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class ZhipuEmbeddingProvider(EmbeddingProvider):
    """Zhipu AI embedding provider (embedding-3 model)."""
    
    def __init__(self):
        self.api_key = settings.zhipu_api_key
        self.base_url = settings.zhipu_base_url
        self.model = settings.zhipu_embedding_model
        self._dimension = settings.embedding_dimension
        
        if not self.api_key:
            raise ValueError("ZHIPU_API_KEY not configured")
    
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Zhipu embedding-3 model."""
        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        embeddings = []
        
        # Process in batches to avoid API limits
        batch_size = 25
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            payload = {
                "model": self.model,
                "input": batch,
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Extract embeddings from response
                for item in data.get("data", []):
                    embeddings.append(item["embedding"])
        
        return embeddings
    
    @property
    def dimension(self) -> int:
        """Return embedding dimension (1024 for embedding-3)."""
        return self._dimension
