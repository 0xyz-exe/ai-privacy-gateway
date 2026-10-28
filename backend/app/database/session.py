import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.models.db_models import Base, PrivacyPolicyModel, ProviderModel

# Connect args for SQLite if needed
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Seed default data if empty
    with SessionLocal() as db:
        # Check default policy
        if not db.query(PrivacyPolicyModel).filter_by(name="Default Standard Redaction").first():
            standard_policy = PrivacyPolicyModel(
                name="Default Standard Redaction",
                description="Redacts common identifiers (emails, phones, credentials, Indonesian NIK/NPWP) before sending to AI providers.",
                is_enabled=True,
                priority=100,
                mode="redact",
                blocked_entities=[],
                allowed_entities=[],
                min_confidence=0.70,
                response_scanning=True,
                streaming_allowed=True
            )
            strict_policy = PrivacyPolicyModel(
                name="Strict Financial & Identity Block",
                description="Blocks any request containing credit card, SSN, bank accounts, or National ID (NIK).",
                is_enabled=True,
                priority=200,
                mode="block",
                blocked_entities=["CREDIT_CARD", "NIK", "BANK_ACCOUNT", "INDONESIA_BANK_ACCOUNT", "PASSPORT"],
                allowed_entities=[],
                min_confidence=0.65,
                response_scanning=True,
                streaming_allowed=False
            )
            restore_policy = PrivacyPolicyModel(
                name="Redact & Authorized Restore",
                description="Reversibly redacts sensitive values and safely restores authorized placeholders in the model response.",
                is_enabled=True,
                priority=150,
                mode="redact_and_restore",
                blocked_entities=[],
                allowed_entities=[],
                min_confidence=0.70,
                response_scanning=True,
                streaming_allowed=True
            )
            db.add_all([standard_policy, strict_policy, restore_policy])

        # Check default provider
        if not db.query(ProviderModel).filter_by(name="Local Mock Engine").first():
            mock_provider = ProviderModel(
                name="Local Mock Engine",
                provider_type="mock",
                base_url="http://mock-internal/v1",
                is_active=True,
                is_default=True,
                timeout_seconds=30,
                models=["mock-gpt-4o", "mock-llama-3"]
            )
            ollama_provider = ProviderModel(
                name="Ollama Local Inference",
                provider_type="ollama",
                base_url=settings.ollama_base_url,
                is_active=True,
                is_default=False,
                timeout_seconds=120,
                models=["llama3.2:latest", "mistral:latest", "phi4:latest"]
            )
            openai_provider = ProviderModel(
                name="OpenAI Cloud",
                provider_type="openai",
                base_url=settings.openai_base_url,
                is_active=bool(settings.openai_api_key),
                is_default=False,
                api_key_masked="sk-...configured" if settings.openai_api_key else "",
                api_key_secret=settings.openai_api_key,
                timeout_seconds=settings.upstream_timeout_seconds,
                models=["gpt-4o", "gpt-4o-mini", "o1-mini"]
            )
            db.add_all([mock_provider, ollama_provider, openai_provider])
            
        db.commit()
