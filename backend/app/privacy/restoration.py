import re
from typing import Dict

class RestorationEngine:
    """
    Safely restores authorized placeholders in AI responses back to the original values,
    strictly bounded to the current request's in-memory vault.
    """

    def restore_text(self, text: str, vault_map: Dict[str, str]) -> str:
        if not text or not vault_map:
            return text

        restored = text
        # Only replace exact matching placeholders found in this request's vault
        for placeholder, original in vault_map.items():
            if placeholder in restored:
                restored = restored.replace(placeholder, original)

        return restored

restoration_engine = RestorationEngine()
