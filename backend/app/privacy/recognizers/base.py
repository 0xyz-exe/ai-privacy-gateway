from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

@dataclass
class RecognizedEntity:
    entity_type: str
    text: str
    start: int
    end: int
    confidence: float
    recognizer_id: str

    def to_dict(self):
        return {
            "entity_type": self.entity_type,
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
            "recognizer_id": self.recognizer_id,
        }

class BaseRecognizer(ABC):
    name: str = "base_recognizer"
    entity_types: List[str] = []

    @abstractmethod
    def analyze(self, text: str) -> List[RecognizedEntity]:
        pass
