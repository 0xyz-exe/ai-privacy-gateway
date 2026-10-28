import time
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.db_models import (
    APIKeyModel, PrivacyPolicyModel, ProviderModel, AuditEventModel
)
from app.middleware.auth import get_authenticated_key
from app.middleware.rate_limit import check_rate_limit
from app.privacy.engine import privacy_engine
from app.privacy.redaction import redaction_engine
from app.privacy.restoration import restoration_engine
from app.policies.engine import policy_engine
from app.providers.mock_adapter import MockProviderAdapter
from app.providers.openai_adapter import OpenAIProviderAdapter
from app.providers.ollama_adapter import OllamaProviderAdapter

router = APIRouter(prefix="/v1", tags=["OpenAI Chat Completions"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = Field(default="mock-gpt-4o")
    messages: List[ChatMessage]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    stream: Optional[bool] = False
    max_tokens: Optional[int] = None

@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    payload: ChatCompletionRequest,
    key_record: Optional[APIKeyModel] = Depends(get_authenticated_key),
    db: Session = Depends(get_db)
):
    start_time = time.time()
    req_id = f"req-{uuid.uuid4().hex[:16]}"
    raw_body = await request.body()
    body_size = len(raw_body)

    # 1. Rate limiting
    rate_limit = key_record.rate_limit if key_record else 60
    check_rate_limit(request, limit=rate_limit)

    # 2. Resolve Privacy Policy
    policy: Optional[PrivacyPolicyModel] = None
    if key_record and key_record.policy_id:
        policy = db.query(PrivacyPolicyModel).filter_by(id=key_record.policy_id, is_enabled=True).first()
    if not policy:
        policy = db.query(PrivacyPolicyModel).filter_by(is_enabled=True).order_by(PrivacyPolicyModel.priority.desc()).first()
    if not policy:
        # Fallback transient default
        policy = PrivacyPolicyModel(name="Default Fallback", mode="redact", min_confidence=0.70)

    # 3. Detect PII across incoming messages
    messages_dicts = [m.model_dump() for m in payload.messages]
    all_detected_entities = []
    for msg in messages_dicts:
        if isinstance(msg.get("content"), str):
            ents = privacy_engine.analyze(
                msg["content"],
                min_confidence=policy.min_confidence
            )
            all_detected_entities.extend(ents)

    # 4. Evaluate Policy
    eval_res = policy_engine.evaluate(
        policy=policy,
        detected_entities=all_detected_entities,
        body_size_bytes=body_size
    )

    detected_category_names = sorted(list({e.entity_type for e in all_detected_entities}))

    # 5. Handle Policy Blocks
    if not eval_res.allowed:
        duration_ms = (time.time() - start_time) * 1000
        # Audit event for blocked request
        audit = AuditEventModel(
            request_id=req_id,
            key_prefix=key_record.prefix if key_record else "anonymous",
            provider="blocked",
            model=payload.model,
            duration_ms=round(duration_ms, 2),
            tokens_used=0,
            redaction_count=0,
            detected_entities=detected_category_names,
            policy_decision="blocked",
            http_status=403,
            error_code="POLICY_VIOLATION"
        )
        db.add(audit)
        db.commit()
        raise HTTPException(status_code=403, detail=eval_res.reason)

    # 6. Redaction Execution
    redacted_messages, request_vault, redacted_entities = redaction_engine.redact_messages(
        messages=messages_dicts,
        privacy_engine_fn=privacy_engine.analyze,
        min_confidence=policy.min_confidence,
        blocked_entities=policy.blocked_entities,
        allowed_entities=policy.allowed_entities
    )

    # 7. Resolve Provider
    provider_record = db.query(ProviderModel).filter_by(is_active=True, is_default=True).first()
    if not provider_record:
        provider_record = db.query(ProviderModel).filter_by(is_active=True).first()

    provider_type = provider_record.provider_type if provider_record else "mock"
    
    # Initialize adapter
    if provider_type == "openai" and provider_record:
        adapter = OpenAIProviderAdapter(
            base_url=provider_record.base_url,
            api_key=provider_record.api_key_secret,
            timeout_seconds=provider_record.timeout_seconds
        )
    elif provider_type == "ollama" and provider_record:
        adapter = OllamaProviderAdapter(
            base_url=provider_record.base_url,
            timeout_seconds=provider_record.timeout_seconds
        )
    else:
        adapter = MockProviderAdapter(model_name=payload.model)

    # Build upstream payload with REDACTED content
    upstream_payload = payload.model_dump()
    upstream_payload["messages"] = redacted_messages

    # 8. Check Streaming Policy
    if payload.stream and not policy.streaming_allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Streaming is disabled by policy '{policy.name}' to enforce response privacy verification."
        )

    # 9. Execute Upstream Request
    if payload.stream:
        # Stream response
        duration_ms = (time.time() - start_time) * 1000
        audit = AuditEventModel(
            request_id=req_id,
            key_prefix=key_record.prefix if key_record else "anonymous",
            provider=provider_type,
            model=payload.model,
            duration_ms=round(duration_ms, 2),
            tokens_used=0,
            redaction_count=len(redacted_entities),
            detected_entities=detected_category_names,
            policy_decision=eval_res.decision,
            http_status=200
        )
        db.add(audit)
        db.commit()
        return StreamingResponse(
            adapter.stream_chat_completion(upstream_payload),
            media_type="text/event-stream"
        )

    # Non-streaming execution
    try:
        response_data = await adapter.chat_completion(upstream_payload)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Upstream provider communication error: {str(exc)}")

    # 10. Process Response (Restoration or Response Scanning)
    if eval_res.should_restore and request_vault:
        # Authorized restoration strictly scoped to this request's vault
        for choice in response_data.get("choices", []):
            content = choice.get("message", {}).get("content", "")
            if content:
                choice["message"]["content"] = restoration_engine.restore_text(content, request_vault)
    elif policy.response_scanning:
        # Ensure response doesn't leak sensitive data
        for choice in response_data.get("choices", []):
            content = choice.get("message", {}).get("content", "")
            if content:
                resp_entities = privacy_engine.analyze(content, min_confidence=policy.min_confidence)
                if resp_entities:
                    resp_redact = redaction_engine.redact_text(content, resp_entities)
                    choice["message"]["content"] = resp_redact.redacted_text

    duration_ms = (time.time() - start_time) * 1000
    tokens_used = response_data.get("usage", {}).get("total_tokens", 0)

    # 11. Sanitized Audit Logging
    audit = AuditEventModel(
        request_id=req_id,
        key_prefix=key_record.prefix if key_record else "anonymous",
        provider=provider_type,
        model=payload.model,
        duration_ms=round(duration_ms, 2),
        tokens_used=tokens_used,
        redaction_count=len(redacted_entities),
        detected_entities=detected_category_names,
        policy_decision=eval_res.decision,
        http_status=200
    )
    db.add(audit)
    
    # Update key last_used_at
    if key_record:
        key_record.last_used_at = audit.timestamp
        
    db.commit()

    return response_data
