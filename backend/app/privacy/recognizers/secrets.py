import re
from typing import List
from app.privacy.recognizers.base import BaseRecognizer, RecognizedEntity

class SecretRecognizer(BaseRecognizer):
    name = "secret_credentials_recognizer"
    entity_types = ["API_KEY", "SECRET_KEY", "BEARER_TOKEN", "PRIVATE_KEY"]

    PATTERNS = [
        ("API_KEY", re.compile(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b')),
        ("API_KEY", re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
        ("API_KEY", re.compile(r'\bgh[pousr]_[A-Za-z0-9_]{36,}\b')),
        ("BEARER_TOKEN", re.compile(r'(?i)bearer\s+([A-Za-z0-9._~+/-]{20,})\b')),
        ("PRIVATE_KEY", re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[^\n]*')),
        ("SECRET_KEY", re.compile(r'(?i)(?:api_?key|secret_?key|auth_?token|client_?secret)[\s:="]+([A-Za-z0-9_-]{16,})["\s]')),
    ]

    def analyze(self, text: str) -> List[RecognizedEntity]:
        matches = []
        for ent_type, pattern in self.PATTERNS:
            for match in pattern.finditer(text):
                if match.groups():
                    val = match.group(1)
                    start = match.start(1)
                    end = match.end(1)
                else:
                    val = match.group(0)
                    start = match.start()
                    end = match.end()
                matches.append(RecognizedEntity(
                    entity_type=ent_type,
                    text=val,
                    start=start,
                    end=end,
                    confidence=0.99,
                    recognizer_id=self.name
                ))
        return matches
