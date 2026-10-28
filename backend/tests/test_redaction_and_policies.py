import pytest
from app.privacy.engine import privacy_engine
from app.privacy.redaction import redaction_engine
from app.privacy.restoration import restoration_engine
from app.policies.engine import policy_engine
from app.models.db_models import PrivacyPolicyModel

def test_redaction_multiple_occurrences():
    text = "Contact alice@example.com. Again, send email to alice@example.com."
    entities = privacy_engine.analyze(text)
    res = redaction_engine.redact_text(text, entities)
    
    assert "[EMAIL_ADDRESS_1]" in res.redacted_text
    assert res.redacted_text.count("[EMAIL_ADDRESS_1]") == 2
    assert "alice@example.com" not in res.redacted_text
    assert res.vault_map["[EMAIL_ADDRESS_1]"] == "alice@example.com"

def test_unicode_preservation():
    text = "Halo dunia! Kirim email ke budi@test.id dan salam hangat 🎉 日本語テスト."
    entities = privacy_engine.analyze(text)
    res = redaction_engine.redact_text(text, entities)
    assert "[EMAIL_ADDRESS_1]" in res.redacted_text
    assert "🎉 日本語テスト" in res.redacted_text

def test_restoration_isolated():
    text = "Send credentials to bob@secret.org immediately."
    entities = privacy_engine.analyze(text)
    res = redaction_engine.redact_text(text, entities)
    
    placeholder = "[EMAIL_ADDRESS_1]"
    assert placeholder in res.redacted_text
    
    # Restore with matching vault
    restored = restoration_engine.restore_text(res.redacted_text, res.vault_map)
    assert "bob@secret.org" in restored

    # Empty/foreign vault does NOT restore
    unrelated_vault = {"[EMAIL_ADDRESS_2]": "charlie@other.org"}
    failed_restore = restoration_engine.restore_text(res.redacted_text, unrelated_vault)
    assert placeholder in failed_restore
    assert "bob@secret.org" not in failed_restore

def test_policy_block_mode():
    policy = PrivacyPolicyModel(
        name="Block Financials",
        mode="block",
        blocked_entities=["CREDIT_CARD"],
        min_confidence=0.70
    )
    # Valid CC: 4111-1111-1111-1111
    text = "Here is credit card 4111-1111-1111-1111 for payment."
    entities = privacy_engine.analyze(text)
    eval_res = policy_engine.evaluate(policy, entities)
    assert not eval_res.allowed
    assert eval_res.decision == "blocked"
    assert "CREDIT_CARD" in eval_res.reason

def test_policy_redact_mode():
    policy = PrivacyPolicyModel(
        name="Standard Redact",
        mode="redact",
        min_confidence=0.70
    )
    text = "My phone is +62 812-3456-7890."
    entities = privacy_engine.analyze(text)
    eval_res = policy_engine.evaluate(policy, entities)
    assert eval_res.allowed
    assert eval_res.decision == "redacted"
    assert len(eval_res.entities_to_redact) == 1
