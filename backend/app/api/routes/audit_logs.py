from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.db_models import AuditEventModel
from app.middleware.auth import require_admin

router = APIRouter(prefix="/api/audit-logs", tags=["Audit Logs"])

class AuditLogItemSchema(BaseModel):
    id: int
    request_id: str
    timestamp: str
    key_prefix: str
    provider: str
    model: str
    duration_ms: float
    tokens_used: int
    redaction_count: int
    detected_entities: List[str]
    policy_decision: str
    http_status: int
    error_code: Optional[str]

class AuditLogsResponseSchema(BaseModel):
    total: int
    items: List[AuditLogItemSchema]

@router.get("", response_model=AuditLogsResponseSchema)
def list_audit_logs(
    db: Session = Depends(get_db),
    admin: bool = Depends(require_admin),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    decision: Optional[str] = None,
    provider: Optional[str] = None
):
    query = db.query(AuditEventModel)
    if decision:
        query = query.filter(AuditEventModel.policy_decision == decision)
    if provider:
        query = query.filter(AuditEventModel.provider == provider)

    total = query.count()
    records = query.order_by(AuditEventModel.timestamp.desc()).offset(offset).limit(limit).all()

    items = [
        AuditLogItemSchema(
            id=r.id,
            request_id=r.request_id,
            timestamp=r.timestamp.isoformat(),
            key_prefix=r.key_prefix,
            provider=r.provider,
            model=r.model or "",
            duration_ms=r.duration_ms,
            tokens_used=r.tokens_used,
            redaction_count=r.redaction_count,
            detected_entities=r.detected_entities or [],
            policy_decision=r.policy_decision,
            http_status=r.http_status,
            error_code=r.error_code
        )
        for r in records
    ]
    return AuditLogsResponseSchema(total=total, items=items)
