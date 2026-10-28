from typing import List, Dict, Any, Optional
from app.privacy.recognizers.base import RecognizedEntity
from app.models.db_models import PrivacyPolicyModel

class PolicyEvaluationResult:
    def __init__(
        self,
        allowed: bool,
        decision: str, # "allowed", "redacted", "blocked"
        reason: str,
        entities_to_redact: List[RecognizedEntity],
        should_restore: bool = False
    ):
        self.allowed = allowed
        self.decision = decision
        self.reason = reason
        self.entities_to_redact = entities_to_redact
        self.should_restore = should_restore

class PolicyEngine:
    def evaluate(
        self,
        policy: PrivacyPolicyModel,
        detected_entities: List[RecognizedEntity],
        body_size_bytes: int = 0
    ) -> PolicyEvaluationResult:
        # Check request size limit
        if policy.request_size_limit and body_size_bytes > policy.request_size_limit:
            return PolicyEvaluationResult(
                allowed=False,
                decision="blocked",
                reason=f"Request size ({body_size_bytes} bytes) exceeds policy limit ({policy.request_size_limit} bytes)",
                entities_to_redact=[]
            )

        if not detected_entities:
            return PolicyEvaluationResult(
                allowed=True,
                decision="allowed",
                reason="No sensitive PII detected.",
                entities_to_redact=[],
                should_restore=False
            )

        # Mode B: Block
        if policy.mode == "block":
            blocked_set = set(policy.blocked_entities) if policy.blocked_entities else set()
            # If no specific blocked entities configured, mode="block" blocks ANY detected entity
            violating = [
                e for e in detected_entities
                if not blocked_set or e.entity_type in blocked_set
            ]
            if violating:
                entity_names = ", ".join(sorted(list({e.entity_type for e in violating})))
                return PolicyEvaluationResult(
                    allowed=False,
                    decision="blocked",
                    reason=f"Policy '{policy.name}' blocked request due to prohibited entities: {entity_names}",
                    entities_to_redact=[]
                )
            return PolicyEvaluationResult(
                allowed=True,
                decision="allowed",
                reason="Detected entities permitted under block-list exceptions.",
                entities_to_redact=[]
            )

        # Mode C: Allow
        if policy.mode == "allow":
            # Pass through without redaction unless entity is explicitly in blocked_entities
            blocked_set = set(policy.blocked_entities) if policy.blocked_entities else set()
            violating = [e for e in detected_entities if e.entity_type in blocked_set]
            if violating:
                entity_names = ", ".join(sorted(list({e.entity_type for e in violating})))
                return PolicyEvaluationResult(
                    allowed=False,
                    decision="blocked",
                    reason=f"Policy '{policy.name}' explicitly blocked prohibited entities: {entity_names}",
                    entities_to_redact=[]
                )
            return PolicyEvaluationResult(
                allowed=True,
                decision="allowed",
                reason="Allowed by policy.",
                entities_to_redact=[]
            )

        # Mode D: Redact and Restore
        if policy.mode == "redact_and_restore":
            allowed_set = set(policy.allowed_entities) if policy.allowed_entities else set()
            to_redact = [e for e in detected_entities if e.entity_type not in allowed_set]
            return PolicyEvaluationResult(
                allowed=True,
                decision="redacted",
                reason="Entities redacted with authorized response restoration enabled.",
                entities_to_redact=to_redact,
                should_restore=True
            )

        # Mode E: Strict Privacy
        if policy.mode == "strict":
            # In strict mode, any sensitive identifier or credentials block the request immediately
            high_risk = {"API_KEY", "SECRET_KEY", "BEARER_TOKEN", "PRIVATE_KEY", "CREDIT_CARD", "NIK", "PASSPORT"}
            for e in detected_entities:
                if e.entity_type in high_risk or e.confidence >= 0.85:
                    return PolicyEvaluationResult(
                        allowed=False,
                        decision="blocked",
                        reason=f"Strict privacy mode rejected request with entity: {e.entity_type}",
                        entities_to_redact=[]
                    )
            # Remaining are redacted
            return PolicyEvaluationResult(
                allowed=True,
                decision="redacted",
                reason="Strict privacy policy redacted detected entities.",
                entities_to_redact=detected_entities,
                should_restore=False
            )

        # Mode A: Redact (Default)
        allowed_set = set(policy.allowed_entities) if policy.allowed_entities else set()
        to_redact = [e for e in detected_entities if e.entity_type not in allowed_set]
        return PolicyEvaluationResult(
            allowed=True,
            decision="redacted" if to_redact else "allowed",
            reason=f"Redacted {len(to_redact)} PII occurrences before forwarding upstream." if to_redact else "No redaction required.",
            entities_to_redact=to_redact,
            should_restore=False
        )

policy_engine = PolicyEngine()
