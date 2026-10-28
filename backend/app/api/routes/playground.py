from typing import List, Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.privacy.engine import privacy_engine
from app.privacy.redaction import redaction_engine
from app.privacy.restoration import restoration_engine
from app.policies.engine import policy_engine
from app.models.db_models import PrivacyPolicyModel

router = APIRouter(prefix="/api/playground", tags=["Playground"])

class PlaygroundAnalyzeRequest(BaseModel):
    text: str = Field(..., max_length=100000)
    mode: str = Field(default="redact") # redact, block, allow, redact_and_restore, strict
    min_confidence: float = Field(default=0.70, ge=0.0, le=1.0)
    blocked_entities: List[str] = Field(default_factory=list)
    allowed_entities: List[str] = Field(default_factory=list)

class DetectedEntityItem(BaseModel):
    entity_type: str
    text: str
    start: int
    end: int
    confidence: float
    recognizer_id: str

class PlaygroundAnalyzeResponse(BaseModel):
    original_text: str
    redacted_text: str
    restored_preview: str
    detected_entities: List[DetectedEntityItem]
    policy_decision: str
    policy_reason: str
    redaction_count: int
    entity_summary: Dict[str, int]
    outbound_payload_preview: str

@router.post("/analyze", response_model=PlaygroundAnalyzeResponse)
def analyze_playground(req: PlaygroundAnalyzeRequest):
    # 1. Detect entities
    entities = privacy_engine.analyze(
        text=req.text,
        blocked_entities=req.blocked_entities,
        allowed_entities=req.allowed_entities,
        min_confidence=req.min_confidence
    )

    # 2. Build transient policy model
    transient_policy = PrivacyPolicyModel(
        name="Playground Dynamic Policy",
        mode=req.mode,
        blocked_entities=req.blocked_entities,
        allowed_entities=req.allowed_entities,
        min_confidence=req.min_confidence,
        request_size_limit=1048576
    )

    # 3. Policy evaluation
    eval_res = policy_engine.evaluate(
        policy=transient_policy,
        detected_entities=entities,
        body_size_bytes=len(req.text.encode("utf-8"))
    )

    # 4. Redaction execution
    redact_res = redaction_engine.redact_text(
        text=req.text,
        entities=eval_res.entities_to_redact
    )

    # 5. Restoration preview if mode allows
    restored_text = ""
    if eval_res.should_restore or req.mode == "redact_and_restore":
        restored_text = restoration_engine.restore_text(redact_res.redacted_text, redact_res.vault_map)
    else:
        restored_text = redact_res.redacted_text

    # Entity summary count
    summary: Dict[str, int] = {}
    for ent in entities:
        summary[ent.entity_type] = summary.get(ent.entity_type, 0) + 1

    outbound_preview = (
        redact_res.redacted_text if eval_res.allowed else "[BLOCKED BY POLICY - NOTHING SENT UPSTREAM]"
    )

    return PlaygroundAnalyzeResponse(
        original_text=req.text,
        redacted_text=redact_res.redacted_text,
        restored_preview=restored_text,
        detected_entities=[DetectedEntityItem(**e.to_dict()) for e in entities],
        policy_decision=eval_res.decision,
        policy_reason=eval_res.reason,
        redaction_count=len(eval_res.entities_to_redact),
        entity_summary=summary,
        outbound_payload_preview=outbound_preview
    )
