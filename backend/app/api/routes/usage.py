from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.models.db_models import AuditEventModel

router = APIRouter(prefix="/api/usage", tags=["Usage & Costs"])

class UsageSummarySchema(BaseModel):
    total_requests: int
    blocked_requests: int
    total_redactions: int
    total_tokens: int
    avg_latency_ms: float
    estimated_cost_usd: float
    provider_breakdown: Dict[str, int]
    entity_frequency: Dict[str, int]

@router.get("/summary", response_model=UsageSummarySchema)
def get_usage_summary(db: Session = Depends(get_db)):
    events = db.query(AuditEventModel).all()
    
    total_requests = len(events)
    blocked_requests = sum(1 for e in events if e.policy_decision == "blocked")
    total_redactions = sum(e.redaction_count for e in events)
    total_tokens = sum(e.tokens_used for e in events)
    latencies = [e.duration_ms for e in events if e.duration_ms > 0]
    avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0

    # Rough OpenAI blended cost estimation ($5 / 1M tokens)
    estimated_cost = round((total_tokens / 1_000_000) * 5.0, 4)

    provider_breakdown: Dict[str, int] = {}
    entity_frequency: Dict[str, int] = {}

    for e in events:
        p = e.provider or "unknown"
        provider_breakdown[p] = provider_breakdown.get(p, 0) + 1
        
        if e.detected_entities:
            for ent_type in e.detected_entities:
                entity_frequency[ent_type] = entity_frequency.get(ent_type, 0) + 1

    return UsageSummarySchema(
        total_requests=total_requests,
        blocked_requests=blocked_requests,
        total_redactions=total_redactions,
        total_tokens=total_tokens,
        avg_latency_ms=round(avg_latency, 2),
        estimated_cost_usd=estimated_cost,
        provider_breakdown=provider_breakdown,
        entity_frequency=entity_frequency
    )
