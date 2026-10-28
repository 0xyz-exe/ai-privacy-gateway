import json
import httpx
from typing import Dict, Any, AsyncGenerator
from fastapi import HTTPException
from app.providers.base import AIProviderAdapter
from app.core.security import validate_upstream_url

class OpenAIProviderAdapter(AIProviderAdapter):
    def __init__(self, base_url: str, api_key: str, timeout_seconds: int = 60):
        # Enforce SSRF validation on remote providers
        if not validate_upstream_url(base_url, allow_local=False):
            raise ValueError(f"Invalid or prohibited upstream URL for OpenAI provider: {base_url}")
            
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout_seconds

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def chat_completion(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        target_url = f"{self.base_url}/chat/completions"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(
                    target_url,
                    json=request_payload,
                    headers=self._get_headers()
                )
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Upstream AI provider timed out.")
            except httpx.RequestError as exc:
                raise HTTPException(status_code=502, detail="Failed to connect to upstream AI provider.")

            if resp.status_code >= 400:
                # Sanitize response without exposing credentials
                detail_msg = f"Upstream provider returned status {resp.status_code}"
                try:
                    err_json = resp.json()
                    if "error" in err_json and isinstance(err_json["error"], dict):
                        detail_msg = err_json["error"].get("message", detail_msg)
                except Exception:
                    pass
                raise HTTPException(status_code=resp.status_code, detail=detail_msg)

            return resp.json()

    async def stream_chat_completion(self, request_payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        target_url = f"{self.base_url}/chat/completions"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                async with client.stream(
                    "POST",
                    target_url,
                    json=request_payload,
                    headers=self._get_headers()
                ) as resp:
                    if resp.status_code >= 400:
                        raise HTTPException(
                            status_code=resp.status_code,
                            detail=f"Upstream provider streaming returned error {resp.status_code}"
                        )
                    async for line in resp.aiter_lines():
                        if line:
                            yield f"{line}\n\n"
            except httpx.TimeoutException:
                yield "data: {\"error\": \"Upstream provider timed out during stream\"}\n\n"
            except httpx.RequestError:
                yield "data: {\"error\": \"Connection interrupted during stream\"}\n\n"
