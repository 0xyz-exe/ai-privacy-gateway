# Architecture & System Design

## 1. Overview

**AI Privacy Gateway** is an intelligent, high-throughput privacy proxy situated between client applications and AI model providers (OpenAI, Ollama, Anthropic, or OpenAI-compatible inference servers).

```
[ Client Application ]
         │ (OpenAI-compatible request: POST /v1/chat/completions)
         ▼
[ Gateway Middleware ]
   ├── Authentication & Rate Limiting (Token Hash & Sliding Window)
   └── Request Body Size & Security Headers Enforcement
         │
         ▼
[ Privacy Engine & Policy Engine ]
   ├── PII Detection (International, Indonesian, Credentials)
   ├── Policy Resolution (Redact, Block, Allow, Redact & Restore, Strict)
   └── Collision-Resistant Redaction Engine ([EMAIL_1], [NIK_1])
         │ (Redacted Payload with Zero Raw PII)
         ▼
[ Provider Adapter ]
   ├── OpenAI-compatible HTTP Adapter (with SSRF Guard)
   ├── Ollama Local Inference Adapter
   └── Mock Provider Engine (Offline / Deterministic Testing)
         │ (AI Response: choices/content)
         ▼
[ Response Processor ]
   ├── Optional Response PII Scanning & Redaction
   └── Authorized Roundtrip Restoration (Request-scoped Vault)
         │
         ▼
[ Sanitized Audit Logging ]
   └── Logs Request ID, latency, token count, detected categories (No Raw PII)
         │
         ▼
[ Client Application Receives Response ]
```

## 2. Key Subsystems

### 2.1 Privacy Engine (`app.privacy.engine`)
- Pluggable modular architecture with deterministic pattern matching and algorithmic checksum validators.
- Evaluates text across international identifiers (Email, E.164 Phones, IPv4/IPv6, Credit Cards with Luhn checksum, Passports, IBAN) and localized identifiers (Indonesian NIK with province & birthdate check, NPWP tax IDs, Indonesian mobile phones, Indonesian bank accounts).
- Secrets detector detects Bearer tokens, OpenAI keys (`sk-`), AWS access keys (`AKIA`), and private keys.
- Resolves overlapping and nested entity spans deterministically based on longest span and highest confidence.

### 2.2 Redaction Engine (`app.privacy.redaction`)
- Replaces detected values with unique, collision-resistant placeholders: `[EMAIL_1]`, `[PHONE_1]`, `[NIK_1]`.
- Generates a request-scoped in-memory vault (`placeholder -> original_value`) kept only for the duration of the request lifecycle.
- Handles multi-turn messages array in-place or copies without altering conversation structure.

### 2.3 Policy Engine (`app.policies.engine`)
Supports five declarative privacy modes:
- **Mode A (Redact):** Replaces detected PII with placeholders before upstream forwarding.
- **Mode B (Block):** Immediately rejects requests violating policy or containing prohibited categories (returns HTTP 403).
- **Mode C (Allow):** Permits configured entity categories without modification.
- **Mode D (Redact and Restore):** Redacts detected PII before forwarding, and safely restores authorized placeholders in the model response choices.
- **Mode E (Strict Privacy):** Blocks high-risk credentials and identity tokens; redacts all uncertain detections.

### 2.4 SSRF Protection & Upstream Providers
- Upstream URLs are validated against loopback (`127.0.0.1`, `localhost`), link-local (`169.254.0.0/16`), private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), and AWS/GCP cloud metadata endpoints (`169.254.169.254`).
- Localhost is permitted only when configuring local inference backends such as Ollama.
