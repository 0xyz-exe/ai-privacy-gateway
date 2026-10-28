from typing import List, Dict, Any
from fastapi import APIRouter
from app.core.config import settings
from app.privacy.engine import privacy_engine

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("")
def get_gateway_settings():
    recognizers_info = [
        {"name": r.name, "entity_types": r.entity_types}
        for r in privacy_engine.recognizers
    ]
    return {
        "app_env": settings.app_env,
        "pii_detection_enabled": settings.pii_detection_enabled,
        "pii_default_mode": settings.pii_default_mode,
        "pii_min_confidence": settings.pii_min_confidence,
        "pii_restore_enabled": settings.pii_restore_enabled,
        "pii_response_scan_enabled": settings.pii_response_scan_enabled,
        "rate_limit_enabled": settings.rate_limit_enabled,
        "rate_limit_requests": settings.rate_limit_requests,
        "rate_limit_window_seconds": settings.rate_limit_window_seconds,
        "upstream_timeout_seconds": settings.upstream_timeout_seconds,
        "max_request_body_bytes": settings.max_request_body_bytes,
        "active_recognizers": recognizers_info,
        "supported_modes": [
            {"mode": "redact", "label": "Mode A: Redact", "description": "Replace detected PII with unique collision-resistant placeholders before forwarding."},
            {"mode": "block", "label": "Mode B: Block", "description": "Reject request immediately if prohibited PII or policy violation is detected."},
            {"mode": "allow", "label": "Mode C: Allow", "description": "Permit configured categories through without modification unless explicitly forbidden."},
            {"mode": "redact_and_restore", "label": "Mode D: Redact & Restore", "description": "Redact upstream, and reversibly restore authorized placeholders in client response."},
            {"mode": "strict", "label": "Mode E: Strict Privacy", "description": "Maximum security: blocks credentials and high-risk PII; redacts all uncertain cases."}
        ]
    }
