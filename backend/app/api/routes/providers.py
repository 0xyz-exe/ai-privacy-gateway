from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import httpx
from app.database.session import get_db
from app.models.db_models import ProviderModel
from app.middleware.auth import require_admin
from app.core.security import validate_upstream_url

router = APIRouter(prefix="/api/providers", tags=["Providers"])

class ProviderCreateSchema(BaseModel):
    name: str = Field(..., max_length=100)
    provider_type: str = Field(default="openai") # openai, ollama, mock
    base_url: str = Field(..., max_length=255)
    api_key: Optional[str] = None
    is_active: bool = Field(default=True)
    is_default: bool = Field(default=False)
    timeout_seconds: int = Field(default=60)
    models: List[str] = Field(default_factory=list)

class ProviderResponseSchema(BaseModel):
    id: int
    name: str
    provider_type: str
    base_url: str
    api_key_masked: str
    is_active: bool
    is_default: bool
    timeout_seconds: int
    models: List[str]
    created_at: str

@router.get("", response_model=List[ProviderResponseSchema])
def list_providers(db: Session = Depends(get_db)):
    providers = db.query(ProviderModel).all()
    return [
        ProviderResponseSchema(
            id=p.id,
            name=p.name,
            provider_type=p.provider_type,
            base_url=p.base_url,
            api_key_masked=p.api_key_masked,
            is_active=p.is_active,
            is_default=p.is_default,
            timeout_seconds=p.timeout_seconds,
            models=p.models or [],
            created_at=p.created_at.isoformat()
        )
        for p in providers
    ]

@router.post("", response_model=ProviderResponseSchema)
def create_provider(payload: ProviderCreateSchema, db: Session = Depends(get_db), admin: bool = Depends(require_admin)):
    # SSRF Check
    allow_local = (payload.provider_type in ("ollama", "mock"))
    if payload.provider_type != "mock" and not validate_upstream_url(payload.base_url, allow_local=allow_local):
        raise HTTPException(
            status_code=400,
            detail=f"Base URL rejected by SSRF guard: '{payload.base_url}' resolves to private/internal/invalid address."
        )

    # Mask key
    masked = ""
    secret = ""
    if payload.api_key:
        secret = payload.api_key
        masked = f"{payload.api_key[:6]}...{payload.api_key[-4:]}" if len(payload.api_key) > 10 else "******"

    provider = ProviderModel(
        name=payload.name,
        provider_type=payload.provider_type,
        base_url=payload.base_url,
        api_key_masked=masked,
        api_key_secret=secret,
        is_active=payload.is_active,
        is_default=payload.is_default,
        timeout_seconds=payload.timeout_seconds,
        models=payload.models
    )
    if payload.is_default:
        db.query(ProviderModel).update({ProviderModel.is_default: False})
        
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return ProviderResponseSchema(
        id=provider.id,
        name=provider.name,
        provider_type=provider.provider_type,
        base_url=provider.base_url,
        api_key_masked=provider.api_key_masked,
        is_active=provider.is_active,
        is_default=provider.is_default,
        timeout_seconds=provider.timeout_seconds,
        models=provider.models or [],
        created_at=provider.created_at.isoformat()
    )

@router.post("/{provider_id}/test")
async def test_provider(provider_id: int, db: Session = Depends(get_db), admin: bool = Depends(require_admin)):
    provider = db.query(ProviderModel).filter_by(id=provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found.")

    if provider.provider_type == "mock":
        return {"status": "success", "message": "Local mock engine is active and ready."}

    # Ping provider
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            headers = {}
            if provider.api_key_secret:
                headers["Authorization"] = f"Bearer {provider.api_key_secret}"
            resp = await client.get(f"{provider.base_url.rstrip('/')}/models", headers=headers)
            return {
                "status": "success" if resp.status_code < 400 else "warning",
                "http_status": resp.status_code,
                "message": f"Connected to {provider.name} (HTTP {resp.status_code})"
            }
    except Exception as e:
        return {"status": "error", "message": f"Connection check failed: {str(e)}"}

@router.delete("/{provider_id}")
def delete_provider(provider_id: int, db: Session = Depends(get_db), admin: bool = Depends(require_admin)):
    provider = db.query(ProviderModel).filter_by(id=provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found.")
    db.delete(provider)
    db.commit()
    return {"message": f"Provider {provider_id} deleted."}
