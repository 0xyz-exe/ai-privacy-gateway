# Configuration Reference

All settings can be specified via environment variables or a `.env` file located in the project root.

| Environment Variable | Default Value | Description |
| :--- | :--- | :--- |
| `APP_ENV` | `development` | Deployment environment (`development` / `production`). |
| `APP_HOST` | `0.0.0.0` | Host IP interface to bind. |
| `APP_PORT` | `8000` | Port for the backend API. |
| `DATABASE_URL` | `sqlite:///...` | SQLAlchemy database connection URI (SQLite or PostgreSQL). |
| `GATEWAY_SECRET_KEY` | *(default dev key)* | High-entropy key used for cryptographic functions. |
| `GATEWAY_ADMIN_TOKEN` | `admin-secret-token-demo` | Secret token used to authenticate administrative operations. |
| `PII_DETECTION_ENABLED` | `true` | Global toggle for PII inspection. |
| `PII_DEFAULT_MODE` | `redact` | Default policy mode (`redact`, `block`, `allow`, `redact_and_restore`, `strict`). |
| `PII_MIN_CONFIDENCE` | `0.70` | Default minimum confidence score required for an entity detection. |
| `RATE_LIMIT_ENABLED` | `true` | Enables in-memory sliding-window request throttling. |
| `RATE_LIMIT_REQUESTS` | `60` | Maximum requests permitted per window. |
| `RATE_LIMIT_WINDOW_SECONDS`| `60` | Duration of rate-limiting window in seconds. |
| `MAX_REQUEST_BODY_BYTES` | `1048576` (1MB) | Maximum permitted incoming request body size. |
| `UPSTREAM_TIMEOUT_SECONDS`| `60` | Default timeout for upstream AI provider requests. |
| `OPENAI_API_KEY` | `""` | Optional server-side API key for official OpenAI provider. |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | Upstream endpoint for OpenAI-compatible providers. |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Endpoint for local Ollama instances. |
