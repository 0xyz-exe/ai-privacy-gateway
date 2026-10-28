# Troubleshooting & FAQ

### 1. "Request failed with HTTP 403 Forbidden"
- **Cause:** Your request triggered a policy block (e.g. `mode="block"` or `mode="strict"` detected a prohibited entity category like `CREDIT_CARD` or `API_KEY`).
- **Fix:** Inspect the `detail` message in the JSON error response or adjust the active policy in the Privacy Policies dashboard tab.

### 2. "Invalid or revoked Gateway API key (HTTP 401)"
- **Cause:** The `Authorization: Bearer <token>` passed in the request header does not match any active API key record in the database.
- **Fix:** Generate a new key in the **API Keys** console tab or verify your header syntax.

### 3. "Base URL rejected by SSRF guard"
- **Cause:** Attempting to configure a remote provider endpoint that points to private IP space (`10.x`, `172.16.x`, `192.168.x`), loopback, or cloud metadata (`169.254.169.254`).
- **Fix:** If connecting to local Ollama, set `provider_type="ollama"`, which authorizes localhost. Remote providers must resolve to valid public IPs.

### 4. "Connection refused on Ollama adapter"
- **Cause:** The local Ollama server is not running on port 11434.
- **Fix:** Start Ollama with `ollama serve` or switch the default provider in **AI Providers** to `Local Mock Engine`.
