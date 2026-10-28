from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.db_models import APIKeyModel
from app.middleware.auth import require_admin
from app.core.security import generate_api_key

router = APIRouter(prefix="/api/keys", tags=["API Keys"])

class KeyCreateSchema(BaseModel):
    name: str = Field(..., max_length=100)
    policy_id: Optional[int] = None
    rate_limit: int = Field(default=60)

class KeyCreatedResponseSchema(BaseModel):
    id: int
    name: str
    prefix: str
    raw_key: str # Returned ONLY ONCE
    policy_id: Optional[int]
    rate_limit: int
    created_at: str

class KeyListResponseSchema(BaseModel):
    id: int
    name: str
    prefix: str
    is_active: bool
    policy_id: Optional[int]
    rate_limit: int
    created_at: str
    last_used_at: Optional[str]

@router.get("", response_model=List[KeyListResponseSchema])
def list_keys(db: Session = Depends(get_db), admin: bool = Depends(require_admin)):
    keys = db.query(APIKeyModel).order_by(APIKeyModel.created_at.desc()).all()
    return [
        KeyListResponseSchema(
            id=k.id,
            name=k.name,
            prefix=k.prefix,
            is_active=k.is_active,
            policy_id=k.policy_id,
            rate_limit=k.rate_limit,
            created_at=k.created_at.isoformat(),
            last_used_at=k.last_used_at.isoformat() if k.last_used_at else None
        )
        for k in keys
    ]

@router.post("", response_model=KeyCreatedResponseSchema)
def create_key(payload: KeyCreateSchema, db: Session = Depends(get_db), admin: bool = Depends(require_admin)):
    raw_key, key_hash, prefix = generate_api_key()

    record = APIKeyModel(
        name=payload.name,
        key_hash=key_hash,
        prefix=prefix,
        policy_id=payload.policy_id,
        rate_limit=payload.rate_limit,
        is_active=True
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return KeyCreatedResponseSchema(
        id=record.id,
        name=record.name,
        prefix=record.prefix,
        raw_key=raw_key,
        policy_id=record.policy_id,
        rate_limit=record.rate_limit,
        created_at=record.created_at.isoformat()
    )

@router.delete("/{key_id}")
def revoke_key(key_id: int, db: Session = Depends(get_db), admin: bool = Depends(require_admin)):
    record = db.query(APIKeyModel).filter_by(id=key_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="API key not found.")
    record.is_active = False
    db.commit()
    return {"message": f"API key {key_id} revoked."}
