# API Reference

The AI Privacy Gateway exposes standard OpenAI-compatible endpoints alongside administration APIs.

## 1. Chat Completions (OpenAI Compatible)

### `POST /v1/chat/completions`

Proxies request through privacy inspection, applies policy redaction or blocking, forwards to configured provider, and returns response.

#### Headers
- `Authorization: Bearer <GATEWAY_API_KEY>` (Optional for local playground)
- `Content-Type: application/json`

#### Request Body
```json
{
  "model": "mock-gpt-4o",
  "messages": [
    {
      "role": "user",
      "content": "Please send the invoice to alice@example.com and contact me at +62 812-3456-7890."
    }
  ],
  "temperature": 0.7,
  "stream": false
}
```

#### Response (200 OK)
```json
{
  "id": "chatcmpl-a1b2c3d4",
  "object": "chat.completion",
  "created": 1729000000,
  "model": "mock-gpt-4o",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Gateway Mock Engine: Successfully received privacy-protected payload with placeholders [EMAIL_ADDRESS_1], [INDONESIAN_PHONE_1]. Your data remains redacted."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 24,
    "completion_tokens": 30,
    "total_tokens": 54
  }
}
```

#### Policy Violation Response (403 Forbidden)
```json
{
  "detail": "Policy 'Strict Financial Block' blocked request due to prohibited entities: CREDIT_CARD"
}
```

---

## 2. Privacy Playground API

### `POST /api/playground/analyze`
Evaluates text against detection and policy engine without external provider forwarding or persistence.

#### Request Body
```json
{
  "text": "Email: bob@corp.com, NIK: 3201011508900001",
  "mode": "redact",
  "min_confidence": 0.70,
  "blocked_entities": [],
  "allowed_entities": []
}
```

#### Response
```json
{
  "original_text": "Email: bob@corp.com, NIK: 3201011508900001",
  "redacted_text": "Email: [EMAIL_ADDRESS_1], NIK: [NIK_1]",
  "restored_preview": "Email: bob@corp.com, NIK: 3201011508900001",
  "detected_entities": [
    {
      "entity_type": "EMAIL_ADDRESS",
      "text": "bob@corp.com",
      "start": 7,
      "end": 19,
      "confidence": 0.98,
      "recognizer_id": "email_recognizer"
    },
    {
      "entity_type": "NIK",
      "text": "3201011508900001",
      "start": 26,
      "end": 42,
      "confidence": 0.88,
      "recognizer_id": "indonesian_nik_recognizer"
    }
  ],
  "policy_decision": "redacted",
  "policy_reason": "Redacted 2 PII occurrences before forwarding upstream.",
  "redaction_count": 2,
  "entity_summary": {
    "EMAIL_ADDRESS": 1,
    "NIK": 1
  },
  "outbound_payload_preview": "Email: [EMAIL_ADDRESS_1], NIK: [NIK_1]"
}
```

---

## 3. Administrative Management Endpoints

Requires `X-Admin-Token: <GATEWAY_ADMIN_TOKEN>` or Bearer token.

- `GET /api/policies`: List all privacy policies.
- `POST /api/policies`: Create a new privacy policy.
- `PUT /api/policies/{id}`: Update an existing policy.
- `DELETE /api/policies/{id}`: Delete a policy.
- `GET /api/providers`: List registered AI providers (keys masked).
- `POST /api/providers`: Add AI provider.
- `POST /api/providers/{id}/test`: Test provider health.
- `GET /api/keys`: List gateway API keys.
- `POST /api/keys`: Generate new API key (returns raw key once).
- `DELETE /api/keys/{id}`: Revoke an API key.
- `GET /api/audit-logs`: Query sanitized audit events (supports `limit`, `offset`, `decision`).
- `GET /api/usage/summary`: Query traffic, redaction volume, and cost estimates.
- `GET /api/settings`: Read gateway runtime status and recognizers.
