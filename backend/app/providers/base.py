from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator

class AIProviderAdapter(ABC):
    @abstractmethod
    async def chat_completion(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes non-streaming completion and returns OpenAI-compatible JSON dict.
        """
        pass

    @abstractmethod
    def stream_chat_completion(self, request_payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        Yields Server-Sent Events strings formatted as 'data: {...}\n\n'.
        """
        pass
