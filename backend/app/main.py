import asyncio
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.core.config import settings
from app.api.v1.router import api_router
from app.websockets.routes import router as ws_router
from app.websockets.manager import binance_stream_worker
from app.db.session import engine, Base

log = structlog.get_logger(__name__)

# Symbols to stream on startup — must include the symbols shown on the
# dashboard so the /ws/ticker/{symbol} clients actually receive live
# price broadcasts instead of connecting to an idle stream.
DEFAULT_STREAM_SYMBOLS = ["BTCUSDT", "ETHUSDT", "LTCUSDT", "SOLUSDT"]

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application startup and shutdown."""
    log.info("app.starting", env=settings.APP_ENV)

    # Create database tables (Alembic handles migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Start Binance stream workers for default symbols
    stream_tasks = []
    for symbol in DEFAULT_STREAM_SYMBOLS:
        task = asyncio.create_task(
            binance_stream_worker(symbol),
            name=f"binance_stream_{symbol}",
        )
        stream_tasks.append(task)
        log.info("binance.stream.started", symbol=symbol)

    yield  # Application runs here

    # Graceful shutdown
    log.info("app.shutting_down")
    for task in stream_tasks:
        task.cancel()
    await asyncio.gather(*stream_tasks, return_exceptions=True)
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
async def global_exception_handler(request, exc):
    import traceback
    error_str = traceback.format_exc()
    log.error("api.error", path=request.url.path, method=request.method, error=error_str)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": str(type(exc).__name__)},
    )


# ── Middleware ─────────────────────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    log.info(
        "http.request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(process_time * 1000),
    )
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Required when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # Allow all hosts
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(api_router)
app.include_router(ws_router)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health():
    from app.services.binance import binance_client
    binance_ok = await binance_client.ping()
    return {
        "status": "ok",
        "binance": "connected" if binance_ok else "unavailable",
        "version": "999.999.999",
        "env": settings.APP_ENV,
    }


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
