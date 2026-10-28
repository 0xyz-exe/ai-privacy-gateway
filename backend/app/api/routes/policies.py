from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.db_models import PrivacyPolicyModel
from app.middleware.auth import require_admin

router = APIRouter(prefix="/api/policies", tags=["Policies"])

class PolicyCreateSchema(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(default="")
    is_enabled: bool = Field(default=True)
    priority: int = Field(default=100)
    mode: str = Field(default="redact") # redact, block, allow, redact_and_restore, strict
    blocked_entities: List[str] = Field(default_factory=list)
    allowed_entities: List[str] = Field(default_factory=list)
    min_confidence: float = Field(default=0.70, ge=0.0, le=1.0)
    request_size_limit: int = Field(default=1048576)
    response_scanning: bool = Field(default=True)
    streaming_allowed: bool = Field(default=True)

class PolicyUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    priority: Optional[int] = None
    mode: Optional[str] = None
    blocked_entities: Optional[List[str]] = None
    allowed_entities: Optional[List[str]] = None
    min_confidence: Optional[float] = None
    request_size_limit: Optional[int] = None
    response_scanning: Optional[bool] = None
    streaming_allowed: Optional[bool] = None

class PolicyResponseSchema(PolicyCreateSchema):
    id: int
    created_at: str
    updated_at: str

@router.get("", response_model=List[PolicyResponseSchema])
def list_policies(db: Session = Depends(get_db)):
    records = db.query(PrivacyPolicyModel).order_by(PrivacyPolicyModel.priority.desc()).all()
    return [
        PolicyResponseSchema(
            id=r.id,
            name=r.name,
            description=r.description or "",
            is_enabled=r.is_enabled,
            priority=r.priority,
            mode=r.mode,
            blocked_entities=r.blocked_entities or [],
            allowed_entities=r.allowed_entities or [],
            min_confidence=r.min_confidence,
            request_size_limit=r.request_size_limit,
            response_scanning=r.response_scanning,
            streaming_allowed=r.streaming_allowed,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat()
        )
        for r in records
    ]

@router.post("", response_model=PolicyResponseSchema)
def create_policy(payload: PolicyCreateSchema, db: Session = Depends(get_db), admin: bool = Depends(require_admin)):
    existing = db.query(PrivacyPolicyModel).filter_by(name=payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Policy with this name already exists.")

    policy = PrivacyPolicyModel(
        name=payload.name,
        description=payload.description,
        is_enabled=payload.is_enabled,
        priority=payload.priority,
        mode=payload.mode,
        blocked_entities=payload.blocked_entities,
        allowed_entities=payload.allowed_entities,
        min_confidence=payload.min_confidence,
        request_size_limit=payload.request_size_limit,
        response_scanning=payload.response_scanning,
        streaming_allowed=payload.streaming_allowed
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return PolicyResponseSchema(
        id=policy.id,
        name=policy.name,
        description=policy.description,
        is_enabled=policy.is_enabled,
        priority=policy.priority,
        mode=policy.mode,
        blocked_entities=policy.blocked_entities,
        allowed_entities=policy.allowed_entities,
        min_confidence=policy.min_confidence,
        request_size_limit=policy.request_size_limit,
        response_scanning=policy.response_scanning,
        streaming_allowed=policy.streaming_allowed,
        created_at=policy.created_at.isoformat(),
        updated_at=policy.updated_at.isoformat()
    )

@router.put("/{policy_id}", response_model=PolicyResponseSchema)
def update_policy(policy_id: int, payload: PolicyUpdateSchema, db: Session = Depends(get_db), admin: bool = Depends(require_admin)):
    policy = db.query(PrivacyPolicyModel).filter_by(id=policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found.")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(policy, k, v)

    db.commit()
    db.refresh(policy)
    return PolicyResponseSchema(
        id=policy.id,
        name=policy.name,
        description=policy.description,
        is_enabled=policy.is_enabled,
        priority=policy.priority,
        mode=policy.mode,
        blocked_entities=policy.blocked_entities,
        allowed_entities=policy.allowed_entities,
        min_confidence=policy.min_confidence,
        request_size_limit=policy.request_size_limit,
        response_scanning=policy.response_scanning,
        streaming_allowed=policy.streaming_allowed,
        created_at=policy.created_at.isoformat(),
        updated_at=policy.updated_at.isoformat()
    )

@router.delete("/{policy_id}")
def delete_policy(policy_id: int, db: Session = Depends(get_db), admin: bool = Depends(require_admin)):
    policy = db.query(PrivacyPolicyModel).filter_by(id=policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found.")
    db.delete(policy)
    db.commit()
    return {"message": f"Policy {policy_id} deleted successfully."}
