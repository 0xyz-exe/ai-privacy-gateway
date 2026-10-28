import json
import httpx
from typing import Dict, Any, AsyncGenerator
from fastapi import HTTPException
from app.providers.base import AIProviderAdapter
from app.core.security import validate_upstream_url

class OllamaProviderAdapter(AIProviderAdapter):
    """
    Adapter for local Ollama instances (e.g. http://localhost:11434).
    Local addresses are permitted with SSRF validation.
    """
    def __init__(self, base_url: str = "http://localhost:11434", timeout_seconds: int = 120):
        if not validate_upstream_url(base_url, allow_local=True):
            raise ValueError(f"Prohibited destination for Ollama provider: {base_url}")
            
        self.base_url = base_url.rstrip("/")
        # Ollama supports OpenAI v1 compatibility endpoint at /v1
        self.compat_url = f"{self.base_url}/v1" if not self.base_url.endswith("/v1") else self.base_url
        self.timeout = timeout_seconds

    async def chat_completion(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        target_url = f"{self.compat_url}/chat/completions"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(
                    target_url,
                    json=request_payload,
                    headers={"Content-Type": "application/json"}
                )
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Local Ollama instance timed out.")
            except httpx.RequestError:
                raise HTTPException(
                    status_code=502,
                    detail="Cannot reach Ollama at configured local endpoint. Ensure Ollama service is running."
                )

            if resp.status_code >= 400:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)

            return resp.json()

    async def stream_chat_completion(self, request_payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        target_url = f"{self.compat_url}/chat/completions"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                async with client.stream(
                    "POST",
                    target_url,
                    json=request_payload,
                    headers={"Content-Type": "application/json"}
                ) as resp:
                    if resp.status_code >= 400:
                        yield f"data: {{\"error\": \"Ollama error {resp.status_code}\"}}\n\n"
                        return
                    async for line in resp.aiter_lines():
                        if line:
                            yield f"{line}\n\n"
            except Exception as e:
                yield f"data: {{\"error\": \"Ollama stream failed: {str(e)}\"}}\n\n"
