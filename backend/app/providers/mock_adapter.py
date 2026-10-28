import json
import time
import uuid
import asyncio
from typing import Dict, Any, AsyncGenerator
from app.providers.base import AIProviderAdapter

class MockProviderAdapter(AIProviderAdapter):
    """
    Deterministic zero-cost mock AI provider for testing, playgrounds,
    and safe offline evaluation without paid APIs.
    """
    def __init__(self, model_name: str = "mock-gpt-4o"):
        self.model_name = model_name

    async def chat_completion(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        messages = request_payload.get("messages", [])
        last_msg = messages[-1].get("content", "") if messages else ""
        
        # Detect placeholders received by the provider
        received_placeholders = [w for w in last_msg.split() if w.startswith("[") and w.endswith("]")]
        
        if received_placeholders:
            reply_text = f"Gateway Mock Engine: Successfully received privacy-protected payload with placeholders {', '.join(received_placeholders)}. Your data remains redacted."
        else:
            reply_text = f"Gateway Mock Engine: Received prompt: '{last_msg[:60]}...'. All privacy checks passed."

        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request_payload.get("model", self.model_name),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": reply_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(last_msg.split()) * 2,
                "completion_tokens": len(reply_text.split()) * 2,
                "total_tokens": (len(last_msg.split()) + len(reply_text.split())) * 2
            }
        }

    async def stream_chat_completion(self, request_payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        full_res = await self.chat_completion(request_payload)
        content = full_res["choices"][0]["message"]["content"]
        words = content.split(" ")
        req_id = full_res["id"]
        model = full_res["model"]

        for i, word in enumerate(words):
            chunk = {
                "id": req_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": word + (" " if i < len(words) - 1 else "")},
                        "finish_reason": None
                    }
                ]
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            await asyncio.sleep(0.01)

        final_chunk = {
            "id": req_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"
