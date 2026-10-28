from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Boolean, Float, Text, DateTime, JSON, ForeignKey
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class APIKeyModel(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    prefix: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    policy_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("privacy_policies.id"), nullable=True)
    rate_limit: Mapped[int] = mapped_column(Integer, default=60) # req per min
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    policy = relationship("PrivacyPolicyModel", back_populates="keys")

class PrivacyPolicyModel(Base):
    __tablename__ = "privacy_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=100)
    mode: Mapped[str] = mapped_column(String(30), default="redact") # redact, block, allow, redact_and_restore, strict
    blocked_entities: Mapped[list] = mapped_column(JSON, default=list)
    allowed_entities: Mapped[list] = mapped_column(JSON, default=list)
    min_confidence: Mapped[float] = mapped_column(Float, default=0.70)
    request_size_limit: Mapped[int] = mapped_column(Integer, default=1048576)
    response_scanning: Mapped[bool] = mapped_column(Boolean, default=True)
    streaming_allowed: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    keys = relationship("APIKeyModel", back_populates="policy")

class ProviderModel(Base):
    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    provider_type: Mapped[str] = mapped_column(String(50), default="openai") # openai, ollama, mock
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key_masked: Mapped[str] = mapped_column(String(100), default="")
    api_key_secret: Mapped[str] = mapped_column(String(255), default="") # Server-side only
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=60)
    models: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    key_prefix: Mapped[str] = mapped_column(String(20), default="anonymous")
    provider: Mapped[str] = mapped_column(String(50), default="mock")
    model: Mapped[str] = mapped_column(String(100), default="")
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    redaction_count: Mapped[int] = mapped_column(Integer, default=0)
    detected_entities: Mapped[list] = mapped_column(JSON, default=list) # List of category strings ONLY, never raw PII
    policy_decision: Mapped[str] = mapped_column(String(30), default="allowed") # allowed, redacted, blocked
    http_status: Mapped[int] = mapped_column(Integer, default=200)
    error_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

class UsageMetricModel(Base):
    __tablename__ = "usage_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column(String(10), index=True, nullable=False) # YYYY-MM-DD
    provider: Mapped[str] = mapped_column(String(50), default="openai")
    model: Mapped[str] = mapped_column(String(100), default="")
    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    blocked_requests: Mapped[int] = mapped_column(Integer, default=0)
    total_redactions: Mapped[int] = mapped_column(Integer, default=0)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
