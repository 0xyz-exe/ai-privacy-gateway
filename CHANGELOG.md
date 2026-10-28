# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-28

### Added
- OpenAI-compatible chat completions proxy endpoint (`POST /v1/chat/completions`).
- Modular PII Detection Engine supporting international identifiers and Indonesian identifiers (NIK, NPWP, Phone, Bank Account).
- Secret and API key credential recognizers (OpenAI `sk-`, AWS `AKIA`, Bearer tokens).
- Collision-resistant Redaction Engine with unique placeholders (`[EMAIL_1]`, `[NIK_1]`).
- Request-scoped, isolated in-memory restoration engine for authorized roundtrip restoration.
- Declarative Privacy Policy Engine with 5 modes: Redact, Block, Allow, Redact & Restore, Strict.
- Provider adapters for OpenAI, Ollama (local), and internal mock engine for testing.
- SSRF protection rejecting loopback, link-local, private, and cloud metadata targets on remote endpoints.
- Rate limiting middleware with sliding window algorithms.
- Full React + TypeScript + Vite + Tailwind CSS dashboard with interactive Playground, Policy manager, Provider settings, API Keys, and Audit Logs.
- Docker Compose configuration for containerized deployment.
- Complete unit, integration, and security test suites with 100% pass rate.
