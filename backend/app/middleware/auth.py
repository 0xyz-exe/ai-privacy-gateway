from typing import Optional
import secrets
from fastapi import Request, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import hash_api_key
from app.database.session import get_db
from app.models.db_models import APIKeyModel

security_bearer = HTTPBearer(auto_error=False)

def get_authenticated_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
    db: Session = Depends(get_db)
) -> Optional[APIKeyModel]:
    """
    Validates Gateway API key for OpenAI-compatible endpoints.
    Allows demo/unauthenticated access to mock if configured, but validates key if provided.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        # Check if query param or header
        raw_token = request.headers.get("X-API-Key")
    else:
        parts = auth_header.split(" ")
        raw_token = parts[1] if len(parts) == 2 else None

    if not raw_token:
        # Allow default fallback for local playground / tests if configured
        request.state.key_prefix = "anonymous"
        request.state.api_key_model = None
        return None

    # Check hash
    token_hash = hash_api_key(raw_token)
    key_record = db.query(APIKeyModel).filter_by(key_hash=token_hash, is_active=True).first()
    
    if not key_record:
        # Check if token matches gateway_admin_token for admin testing
        if secrets.compare_digest(raw_token, settings.gateway_admin_token):
            request.state.key_prefix = "admin_master"
            request.state.api_key_model = None
            return None
            
        raise HTTPException(status_code=401, detail="Invalid or revoked Gateway API key.")

    request.state.key_prefix = key_record.prefix
    request.state.api_key_model = key_record
    return key_record

def require_admin(request: Request):
    """
    Protects administrative CRUD endpoints.
    Accepts X-Admin-Token or Bearer matching settings.gateway_admin_token.
    """
    admin_token = request.headers.get("X-Admin-Token")
    if not admin_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            admin_token = auth_header.replace("Bearer ", "").strip()

    if not admin_token or not secrets.compare_digest(admin_token, settings.gateway_admin_token):
        raise HTTPException(status_code=403, detail="Unauthorized. Valid Admin Token required.")
    return True
