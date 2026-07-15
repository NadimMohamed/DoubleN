import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.core.config import settings
from app.api.v1.router import api_router
from app.schemas.health import HealthResponse
from app.db.session import engine, Base
from app.middleware.rate_limit import init_rate_limiter, rate_limit_middleware

log = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application startup and shutdown."""
    log.info("app.starting", env=settings.APP_ENV)

    # Create database tables (Alembic handles migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    init_rate_limiter()

    # NOTE: Binance stream workers are intentionally NOT started here.
    # Railway's hosting IPs are geo-blocked by Binance (HTTP 451), which
    # made the outbound `binance_stream_worker` connections fail on every
    # attempt and constantly retry with backoff for no benefit. Real-time
    # prices are now served via REST polling (see app/services/binance.py,
    # which caches responses for a couple of seconds), which is reliable
    # from this environment. The /ws/ticker/{symbol} endpoint still works
    # for any client that connects directly — it just won't receive
    # broadcasts unless something calls `manager.broadcast(...)`. If
    # Binance WebSocket connectivity is restored, `binance_stream_worker`
    # can be re-enabled here for lower-latency updates.

    yield  # Application runs here

    # Graceful shutdown
    log.info("app.shutting_down")
    await engine.dispose()
    log.info("app.stopped")


app = FastAPI(
    title="Double N Trading API",
    description="Real-time trading data API with Binance integration",
    version="999.999.999",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all for any unhandled exception so callers never see a raw
    traceback and we always have a request ID to correlate logs against."""
    import traceback
    request_id = getattr(request.state, "request_id", "unknown")
    error_str = traceback.format_exc()
    log.error(
        "api.unhandled_error",
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        error=str(exc),
        error_type=type(exc).__name__,
        traceback=error_str,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__,
            "request_id": request_id,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Log HTTPExceptions (4xx/5xx raised intentionally by endpoints) with
    request context so they're easy to trace, while preserving the
    standard FastAPI response shape."""
    request_id = getattr(request.state, "request_id", "unknown")
    log_fn = log.warning if exc.status_code < 500 else log.error
    log_fn(
        "api.http_exception",
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        status_code=exc.status_code,
        detail=exc.detail,
    )
    headers = getattr(exc, "headers", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "request_id": request_id},
        headers=headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return 400 (rather than FastAPI's default 422) with a clear,
    structured list of validation errors, and log them for debugging."""
    request_id = getattr(request.state, "request_id", "unknown")
    log.warning(
        "api.validation_error",
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        errors=exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Invalid request data",
            "errors": exc.errors(),
            "request_id": request_id,
        },
    )


# ── Middleware ─────────────────────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Structured request/response logging middleware.

    Attaches a unique request ID to every request (available to
    downstream handlers via `request.state.request_id`), and logs the
    method, path, query params, response status, and duration for every
    request. Unexpected exceptions are logged with a stack trace and
    re-raised so the exception handlers above can produce the response.
    """
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.time()

    try:
        response = await call_next(request)
    except Exception as exc:
        import traceback
        duration_ms = round((time.time() - start_time) * 1000)
        log.error(
            "http.request.failed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            duration_ms=duration_ms,
            error=str(exc),
            error_type=type(exc).__name__,
            traceback=traceback.format_exc(),
        )
        raise

    process_time = time.time() - start_time
    log_fn = log.info if response.status_code < 500 else log.error
    log_fn(
        "http.request",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        query_params=dict(request.query_params),
        status_code=response.status_code,
        duration_ms=round(process_time * 1000),
    )
    response.headers["X-Request-ID"] = request_id
    return response



# Get frontend URL from environment or use default
frontend_origins = [
    "https://dn-frontend-production-43b8.up.railway.app",
    "https://doublen-production.up.railway.app",
]

# Add localhost for development if not production
if settings.APP_ENV != "production":
    frontend_origins.extend([
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
    expose_headers=["X-Request-ID"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

app.middleware("http")(rate_limit_middleware)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(api_router)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"], response_model=HealthResponse)
async def health():
    from app.services.binance import binance_client

    try:
        binance_ok = await binance_client.ping()
    except Exception as e:
        log.error("health.binance_ping_failed", error=str(e))
        binance_ok = False

    return HealthResponse(
        status="ok",
        binance="connected" if binance_ok else "unavailable",
        version="999.999.999",
        env=settings.APP_ENV,
    )


@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "DoubleN Trading API",
        "docs": "/api/docs",
        "health": "/health",
        "version": "999.999.999",
    }

@app.get("/cors-test")
async def cors_test():
    return {"cors": "new_version"}
