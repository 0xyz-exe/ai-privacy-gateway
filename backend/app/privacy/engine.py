from typing import List, Optional
from app.privacy.recognizers.base import BaseRecognizer, RecognizedEntity
from app.privacy.recognizers.international import (
    EmailRecognizer, PhoneRecognizer, IPAddressRecognizer,
    CreditCardRecognizer, DateOfBirthRecognizer, PassportRecognizer,
    IBANRecognizer, SensitiveURLRecognizer
)
from app.privacy.recognizers.indonesian import (
    NIKRecognizer, NPWPRecognizer, IndonesianPhoneRecognizer,
    IndonesianBankAccountRecognizer, IndonesianPostalCodeRecognizer
)
from app.privacy.recognizers.secrets import SecretRecognizer

class PrivacyEngine:
    def __init__(self):
        self.recognizers: List[BaseRecognizer] = [
            EmailRecognizer(),
            PhoneRecognizer(),
            IPAddressRecognizer(),
            CreditCardRecognizer(),
            DateOfBirthRecognizer(),
            PassportRecognizer(),
            IBANRecognizer(),
            SensitiveURLRecognizer(),
            NIKRecognizer(),
            NPWPRecognizer(),
            IndonesianPhoneRecognizer(),
            IndonesianBankAccountRecognizer(),
            IndonesianPostalCodeRecognizer(),
            SecretRecognizer()
        ]

    def register_recognizer(self, recognizer: BaseRecognizer):
        self.recognizers.append(recognizer)

    def analyze(
        self,
        text: str,
        blocked_entities: Optional[List[str]] = None,
        allowed_entities: Optional[List[str]] = None,
        min_confidence: float = 0.70
    ) -> List[RecognizedEntity]:
        if not text:
            return []

        all_matches: List[RecognizedEntity] = []
        for recognizer in self.recognizers:
            try:
                results = recognizer.analyze(text)
                for res in results:
                    # Filter confidence
                    if res.confidence < min_confidence:
                        continue
                    # Filter allowed entities
                    if allowed_entities and res.entity_type in allowed_entities:
                        continue
                    all_matches.append(res)
            except Exception:
                # Isolate recognizer failure
                continue

        # Resolve overlapping spans deterministically:
        # Sort by start asc, length desc, confidence desc
        sorted_matches = sorted(
            all_matches,
            key=lambda m: (m.start, -(m.end - m.start), -m.confidence)
        )

        resolved: List[RecognizedEntity] = []
        last_end = -1
        for match in sorted_matches:
            if match.start >= last_end:
                resolved.append(match)
                last_end = match.end
            else:
                # Overlap: keep the one already selected (longer span or earlier)
                continue

        return resolved

privacy_engine = PrivacyEngine()
