import asyncio
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

# Symbols to stream on startup
DEFAULT_STREAM_SYMBOLS = []

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
    "version": "999.999.999",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── Middleware ─────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dn-frontend-production-43b8.up.railway.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    return {"message": "Double N Trading API", "docs": "/api/docs"}

@app.get("/cors-test")
async def cors_test():
    return {"cors": "new_version"}
