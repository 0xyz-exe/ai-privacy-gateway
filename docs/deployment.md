# Deployment Guide

AI Privacy Gateway can be deployed locally using Python or in production via Docker Compose.

## 1. Quickstart with Docker Compose

Ensure Docker and Docker Compose are installed:

```bash
# 1. Clone repository
git clone https://github.com/0xyz-exe/ai-privacy-gateway.git
cd ai-privacy-gateway

# 2. Copy and customize environment variables
cp .env.example .env

# 3. Launch stack
docker compose up -d

# 4. Access Gateway:
# Backend API:   http://localhost:8000
# OpenAPI Docs:  http://localhost:8000/docs
# Web Dashboard: http://localhost:3000
```

---

## 2. Local Development Setup

### Backend Setup
```bash
# In repository root
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run backend development server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Dashboard available at http://localhost:5173
```

---

## 3. Database & Persistence

- **Development:** Defaults to zero-config SQLite (`privacy_gateway.db`). Tables and initial standard policies & mock providers seed automatically on startup.
- **Production:** Configured for PostgreSQL (`postgresql://...`). Schema is initialized automatically via SQLAlchemy DeclarativeBase.
