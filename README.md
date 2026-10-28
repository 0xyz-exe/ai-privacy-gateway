# AI Privacy Gateway

<p align="center">
  <strong>Your AI requests. Your privacy rules. Your control.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License" />
  <img src="https://img.shields.io/badge/python-3.12%20%7C%203.13-blue.svg" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688.svg" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-19-61dafb.svg" alt="React" />
  <img src="https://img.shields.io/badge/Docker-ready-2496ED.svg" alt="Docker" />
  <img src="https://img.shields.io/badge/coverage-100%25-brightgreen.svg" alt="Coverage" />
</p>

<p align="center">
  <img src="docs/screenshots/dashboard.png" width="100%" alt="AI Privacy Gateway Dashboard" />
</p>

## Visual Console Tour

<table width="100%">
  <tr>
    <td width="50%">
      <h4 align="center">Privacy Playground & Redaction Preview</h4>
      <img src="docs/screenshots/playground.png" width="100%" alt="Playground Preview" />
    </td>
    <td width="50%">
      <h4 align="center">Declarative Privacy Policies</h4>
      <img src="docs/screenshots/policies.png" width="100%" alt="Policies Manager" />
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h4 align="center">AI Providers & Adapters</h4>
      <img src="docs/screenshots/providers.png" width="100%" alt="AI Providers" />
    </td>
    <td width="50%">
      <h4 align="center">Gateway API Key Management</h4>
      <img src="docs/screenshots/api-keys.png" width="100%" alt="API Keys" />
    </td>
  </tr>
  <tr>
    <td colspan="2">
      <h4 align="center">Privacy-Preserving Audit Trail</h4>
      <img src="docs/screenshots/audit-logs.png" width="100%" alt="Audit Logs" />
    </td>
  </tr>
</table>

---

## Overview

**AI Privacy Gateway** is an open-source, self-hostable privacy proxy and Data Loss Prevention (DLP) layer situated between your applications and Large Language Model (LLM) providers. It provides:

- **Drop-in OpenAI Compatibility:** Intercepts requests at `POST /v1/chat/completions`.
- **Intelligent PII Redaction:** Sanitizes emails, phone numbers, credit cards (with Luhn validation), IP addresses, passports, IBANs, and localized identifiers.
- **Indonesian Identifiers:** Built-in recognizers for **NIK** (16-digit national ID with province & birthdate checksum), **NPWP** tax IDs, Indonesian mobile numbers, postal codes, and bank accounts.
- **Credentials & Secret Shield:** Prevents leakage of OpenAI keys (`sk-`), AWS access keys (`AKIA`), Bearer tokens, and private keys.
- **5 Enforcement Modes:** `Redact` (Mode A), `Block` (Mode B), `Allow` (Mode C), `Redact & Restore` (Mode D), and `Strict Privacy` (Mode E).
- **Request-Scoped Ephemeral Restoration:** Reversibly restores authorized placeholders in AI responses without storing mappings in database or exposing them across requests.
- **SSRF Defense:** Blocks access to private IP spaces, loopback addresses, and cloud metadata endpoints (`169.254.169.254`).
- **Privacy-Preserving Audit Logs:** Records request durations, token counts, and sanitized entity categories without logging raw prompts or user PII.
- **Developer Console & Playground:** Real-time visual redaction preview, policy management, provider routing, and key issuance.

---

## Repository Details

- **GitHub Repository:** [`https://github.com/0xyz-exe/ai-privacy-gateway`](https://github.com/0xyz-exe/ai-privacy-gateway)
- **Maintainer:** `0xyz-exe`
- **License:** Apache License 2.0
- **Default Branch:** `main`

---

## Request Processing Pipeline

```
Client Application
    │ (OpenAI-compatible request: POST /v1/chat/completions)
    ▼
Gateway Middleware
    ├── Bearer API Key Authentication (Constant-time SHA-256 hash check)
    ├── Sliding Window Rate Limiting (Per-key / Per-IP)
    └── Max Body Size & Security Headers Enforcement
    ▼
Privacy Engine & Policy Resolution
    ├── PII Detection (International, Indonesian, Credentials)
    └── Policy Mode Evaluation (Redact / Block / Allow / Restore / Strict)
    ▼
Redaction Engine
    └── Replaces PII with collision-resistant placeholders ([EMAIL_1], [NIK_1])
    ▼
Upstream AI Provider Adapter
    ├── OpenAI / OpenAI-compatible endpoint (with SSRF protection)
    ├── Ollama Local Inference (http://localhost:11434)
    └── Local Mock Provider (Zero-cost, offline deterministic testing)
    ▼
Response Processing & Restoration
    ├── Optional Response PII Scanning
    └── Request-scoped Authorized Placeholder Restoration
    ▼
Sanitized Audit Logging & Client Response
    └── Zero raw prompt persistence, zero PII storage
```

---

## Quickstart

### Option 1: Docker Compose (Recommended for Production)

```bash
# 1. Clone repository
git clone https://github.com/0xyz-exe/ai-privacy-gateway.git
cd ai-privacy-gateway

# 2. Configure environment
cp .env.example .env

# 3. Start stack (Backend, Frontend, PostgreSQL)
docker compose up -d

# Dashboard: http://localhost:3000
# Backend API: http://localhost:8000
# OpenAPI Docs: http://localhost:8000/docs
```

### Option 2: Local Development Setup

#### Backend (Python 3.12+)
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r backend/requirements.txt
pytest backend/tests -v

cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend (React + Vite + Tailwind)
```bash
cd frontend
npm install
npm run build
npm run dev
# Console accessible at http://localhost:5180
```

---

## API Usage Examples

### 1. cURL (Drop-in OpenAI Replacement)

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_GATEWAY_API_KEY" \
  -d '{
    "model": "mock-gpt-4o",
    "messages": [
      {
        "role": "user",
        "content": "Please send the agreement to alice@example.com and contact +62 812-3456-7890."
      }
    ]
  }'
```

### 2. Python (`openai` SDK)

```python
from openai import OpenAI

# Direct standard OpenAI SDK to your self-hosted Privacy Gateway
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="aipg_live_your_gateway_key"
)

response = client.chat.completions.create(
    model="mock-gpt-4o",
    messages=[
        {"role": "user", "content": "Kirim faktur ke budi@perusahaan.co.id, NIK 3201011508900001."}
    ]
)

print(response.choices[0].message.content)
```

### 3. Node.js / TypeScript (`openai` SDK)

```typescript
import OpenAI from 'openai';

const openai = new OpenAI({
  baseURL: 'http://localhost:8000/v1',
  apiKey: 'aipg_live_your_gateway_key',
});

async function main() {
  const completion = await openai.chat.completions.create({
    model: 'mock-gpt-4o',
    messages: [
      { role: 'user', content: 'Customer email: support@test.id, phone: 081234567890.' }
    ],
  });

  console.log(completion.choices[0].message.content);
}

main();
```

---

## Supported Recognizers

| Category | Identifier | Recognizer Name | Verification Method |
| :--- | :--- | :--- | :--- |
| **International** | Email Address | `email_recognizer` | RFC 5322 regex validation |
| **International** | Phone Number | `international_phone_recognizer` | E.164 and localized telephone formats |
| **International** | Credit Card | `credit_card_recognizer` | 13-19 digits + Luhn checksum algorithm |
| **International** | IP Address | `ip_address_recognizer` | IPv4 / IPv6 validation via `ipaddress` |
| **International** | IBAN | `iban_recognizer` | MOD-97 ISO 7064 check |
| **International** | Passport | `passport_recognizer` | Standard passport format heuristics |
| **International** | Date of Birth | `dob_recognizer` | Contextual date parsing |
| **Indonesian** | NIK (National ID) | `indonesian_nik_recognizer` | 16-digit province + birthdate offset algorithm |
| **Indonesian** | NPWP (Tax ID) | `indonesian_npwp_recognizer` | Formatted and unformatted 15/16 digit pattern |
| **Indonesian** | Indonesian Phone | `indonesian_phone_recognizer` | `+628...`, `628...`, and `08...` mobile numbers |
| **Indonesian** | Indonesian Bank | `indonesian_bank_account_recognizer` | Account numbers contextualized by BCA, Mandiri, BRI, etc. |
| **Credentials** | API & Secret Keys | `secret_credentials_recognizer` | OpenAI `sk-`, AWS `AKIA`, Bearer tokens, private keys |

---

## Project Structure

```
ai-privacy-gateway/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # HTTP & OpenAI route handlers
│   │   ├── core/                # Config, security, SSRF guards
│   │   ├── database/            # SQLAlchemy session & seed bootstrap
│   │   ├── middleware/          # Auth, sliding-window rate limit, headers
│   │   ├── models/              # Database models (Keys, Policies, Providers, Audits)
│   │   ├── policies/            # Policy evaluation engine (5 modes)
│   │   ├── privacy/             # Detection & Redaction engines
│   │   │   └── recognizers/     # Modular International & Indonesian recognizers
│   │   ├── providers/           # Adapters for OpenAI, Ollama, and Mock engine
│   │   └── main.py              # Application entrypoint
│   ├── tests/                   # Pytest suite (Unit, Integration, Security)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # Views: Overview, Playground, Policies, Providers, etc.
│   │   ├── api.ts               # Gateway API client
│   │   ├── types.ts             # TypeScript definitions
│   │   └── App.tsx              # Main dashboard application
│   └── package.json
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── docker-compose.yml
├── docs/
│   ├── architecture.md
│   ├── threat-model.md
│   ├── privacy-model.md
│   ├── deployment.md
│   ├── configuration.md
│   ├── api-reference.md
│   ├── troubleshooting.md
│   └── screenshots/
├── .github/workflows/ci.yml
├── .env.example
├── .gitignore
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
└── CHANGELOG.md
```

---

## Documentation

- [Architecture & System Design](docs/architecture.md)
- [Threat Model & Security Safeguards](docs/threat-model.md)
- [Privacy Model & Data Guarantees](docs/privacy-model.md)
- [Deployment Guide](docs/deployment.md)
- [Configuration Reference](docs/configuration.md)
- [API Reference](docs/api-reference.md)
- [Troubleshooting & FAQ](docs/troubleshooting.md)

---

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
