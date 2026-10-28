from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.database.session import init_db
from app.api.routes import (
    health, chat, playground, policies, providers, api_keys, audit_logs, usage, settings as settings_route
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables and seeds on startup
    init_db()
    yield

app = FastAPI(
    title="AI Privacy Gateway",
    description="Production-grade intelligent privacy proxy layer between applications and AI providers with PII redaction, DLP, and privacy controls.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    # Enforce request body size limit
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.max_request_body_bytes:
        return JSONResponse(
            status_code=413,
            content={"detail": f"Request body too large. Maximum {settings.max_request_body_bytes} bytes allowed."}
        )
        
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    return response

# Include Routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(playground.router)
app.include_router(policies.router)
app.include_router(providers.router)
app.include_router(api_keys.router)
app.include_router(audit_logs.router)
app.include_router(usage.router)
app.include_router(settings_route.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
