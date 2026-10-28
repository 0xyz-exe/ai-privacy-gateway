from typing import Dict, List, Tuple, Any, Optional
from app.privacy.recognizers.base import RecognizedEntity

class RedactionResult:
    def __init__(self, redacted_text: str, vault_map: Dict[str, str], entities: List[RecognizedEntity]):
        self.redacted_text = redacted_text
        self.vault_map = vault_map  # placeholder -> original_value (in-memory only)
        self.entities = entities
        self.redaction_count = len(entities)

class RedactionEngine:
    def __init__(self):
        pass

    def redact_text(
        self,
        text: str,
        entities: List[RecognizedEntity],
        existing_vault: Optional[Dict[str, str]] = None,
        entity_counters: Optional[Dict[str, int]] = None
    ) -> RedactionResult:
        if not text or not entities:
            return RedactionResult(redacted_text=text, vault_map=existing_vault or {}, entities=[])

        vault = dict(existing_vault or {})
        counters = dict(entity_counters or {})
        
        # Reverse map to ensure same original value gets same placeholder within request
        rev_vault = {v: k for k, v in vault.items()}

        # Sort entities by start index ascending
        sorted_entities = sorted(entities, key=lambda e: e.start)

        pieces = []
        last_idx = 0

        for ent in sorted_entities:
            # Append unmodified text before entity
            pieces.append(text[last_idx:ent.start])

            original_val = text[ent.start:ent.end]
            
            # Check if this exact original value was already mapped to a placeholder
            if original_val in rev_vault:
                placeholder = rev_vault[original_val]
            else:
                ent_type = ent.entity_type
                counters[ent_type] = counters.get(ent_type, 0) + 1
                placeholder = f"[{ent_type}_{counters[ent_type]}]"
                
                # Check for accidental collision with text
                while placeholder in text and placeholder not in rev_vault.values():
                    counters[ent_type] += 1
                    placeholder = f"[{ent_type}_{counters[ent_type]}]"

                vault[placeholder] = original_val
                rev_vault[original_val] = placeholder

            pieces.append(placeholder)
            last_idx = ent.end

        # Append trailing text
        pieces.append(text[last_idx:])
        redacted = "".join(pieces)

        return RedactionResult(redacted_text=redacted, vault_map=vault, entities=sorted_entities)

    def redact_messages(
        self,
        messages: List[Dict[str, Any]],
        privacy_engine_fn,
        min_confidence: float = 0.70,
        blocked_entities: Optional[List[str]] = None,
        allowed_entities: Optional[List[str]] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, str], List[RecognizedEntity]]:
        """
        Redacts OpenAI messages list in-place/copy with single unified request-scoped vault.
        """
        redacted_messages = []
        unified_vault: Dict[str, str] = {}
        all_detected_entities: List[RecognizedEntity] = []
        entity_counters: Dict[str, int] = {}

        for msg in messages:
            content = msg.get("content")
            if isinstance(content, str):
                entities = privacy_engine_fn(
                    content,
                    blocked_entities=blocked_entities,
                    allowed_entities=allowed_entities,
                    min_confidence=min_confidence
                )
                res = self.redact_text(
                    content,
                    entities,
                    existing_vault=unified_vault,
                    entity_counters=entity_counters
                )
                unified_vault.update(res.vault_map)
                all_detected_entities.extend(entities)
                
                new_msg = dict(msg)
                new_msg["content"] = res.redacted_text
                redacted_messages.append(new_msg)
            else:
                redacted_messages.append(msg)

        return redacted_messages, unified_vault, all_detected_entities

redaction_engine = RedactionEngine()
