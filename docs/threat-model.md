# Threat Model & Security Controls

## 1. Assets & Boundaries

1. **User Data & Prompts:** Sensitive text containing Personally Identifiable Information (PII), customer identifiers, or proprietary data.
2. **Gateway API Keys:** Client credentials used to authenticate to `/v1/chat/completions`.
3. **Upstream AI Credentials:** Third-party provider API keys (OpenAI, Anthropic, etc.).
4. **Audit Logs & Metrics:** Telemetry records stored in the gateway database.

---

## 2. Threat Analysis & Mitigations

| Threat Vector | Risk Description | Architectural Mitigation |
| :--- | :--- | :--- |
| **Prompt & PII Leakage** | Raw prompts containing PII are leaked to third-party AI providers or logged to disk. | Prompts are analyzed and redacted prior to upstream forwarding. Raw prompts and PII values are never stored in databases, logs, or metrics. |
| **Server-Side Request Forgery (SSRF)** | Attacker configures a malicious provider base URL targeting internal cloud metadata (e.g. `169.254.169.254`) or internal network services. | Strict URL validator resolves hostnames and blocks private, loopback, link-local, and cloud metadata IP ranges for remote providers. |
| **Cross-Request Restoration Leakage** | A request accesses another request's redaction mappings or restores placeholders across users. | Redaction vaults are strictly request-scoped in memory, never shared between concurrent requests, and destroyed immediately when the request concludes. |
| **Upstream Credential Exposure** | Provider API keys are leaked to the browser frontend or via error traces. | Provider keys are stored server-side only. All frontend API responses return masked keys (`sk-...abcd`). Exceptions are sanitized before HTTP serialization. |
| **Gateway API Key Compromise** | Database breach reveals raw client API keys. | API keys are generated with 32-character high-entropy random bytes, displayed only once upon creation, and stored in the database exclusively as SHA-256 hashes. |
| **DoS / Resource Exhaustion** | Flooding endpoint with oversized payloads or abusive request bursts. | In-memory sliding window rate limiter per API key/IP, coupled with a strict maximum request body size limit (default 1MB). |
