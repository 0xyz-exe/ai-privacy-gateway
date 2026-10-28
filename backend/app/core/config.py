import os
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field

class Settings(BaseModel):
    app_env: str = Field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    app_host: str = Field(default_factory=lambda: os.getenv("APP_HOST", "0.0.0.0"))
    app_port: int = Field(default_factory=lambda: int(os.getenv("APP_PORT", "8000")))
    
    # Database
    database_url: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", 
            f"sqlite:///{Path(__file__).resolve().parent.parent.parent}/privacy_gateway.db"
        )
    )
    
    # Security
    gateway_secret_key: str = Field(
        default_factory=lambda: os.getenv("GATEWAY_SECRET_KEY", "dev-secret-key-change-in-production-32chars")
    )
    gateway_admin_token: str = Field(
        default_factory=lambda: os.getenv("GATEWAY_ADMIN_TOKEN", "admin-secret-token-demo")
    )
    
    # Privacy Defaults
    pii_detection_enabled: bool = Field(
        default_factory=lambda: os.getenv("PII_DETECTION_ENABLED", "true").lower() == "true"
    )
    pii_default_mode: str = Field(
        default_factory=lambda: os.getenv("PII_DEFAULT_MODE", "redact")
    )
    pii_min_confidence: float = Field(
        default_factory=lambda: float(os.getenv("PII_MIN_CONFIDENCE", "0.70"))
    )
    pii_restore_enabled: bool = Field(
        default_factory=lambda: os.getenv("PII_RESTORE_ENABLED", "false").lower() == "true"
    )
    pii_response_scan_enabled: bool = Field(
        default_factory=lambda: os.getenv("PII_RESPONSE_SCAN_ENABLED", "true").lower() == "true"
    )
    
    # Audit & Observability
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    audit_log_enabled: bool = Field(
        default_factory=lambda: os.getenv("AUDIT_LOG_ENABLED", "true").lower() == "true"
    )
    audit_log_content: bool = Field(
        default_factory=lambda: os.getenv("AUDIT_LOG_CONTENT", "false").lower() == "true"
    )
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(
        default_factory=lambda: os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    )
    rate_limit_requests: int = Field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
    )
    rate_limit_window_seconds: int = Field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    )
    
    # Upstream defaults
    upstream_timeout_seconds: int = Field(
        default_factory=lambda: int(os.getenv("UPSTREAM_TIMEOUT_SECONDS", "60"))
    )
    max_request_body_bytes: int = Field(
        default_factory=lambda: int(os.getenv("MAX_REQUEST_BODY_BYTES", "1048576")) # 1MB
    )
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_base_url: str = Field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    ollama_base_url: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))

    # CORS
    cors_origins: List[str] = ["*"]

settings = Settings()
