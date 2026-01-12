"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from src.api.middleware import setup_middleware
from src.api.v1 import api_router
from src.core.config import settings
from src.core.logging import configure_logging, get_logger
from src.db.session import engine

# Configure logging first
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events.

    Args:
        app: FastAPI application

    Yields:
        None during application lifetime
    """
    # Startup
    logger.info(
        "application_starting",
        environment=settings.api_env,
        version="0.1.0",
    )

    # Verify database connection
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("database_connected")
    except Exception as e:
        logger.error("database_connection_failed", error=str(e))

    yield

    # Shutdown
    logger.info("application_shutting_down")
    await engine.dispose()
    logger.info("database_connections_closed")


# Create FastAPI app
app = FastAPI(
    title="Decision Calm Engine API",
    description="Multi-agent decision support system for calmer, better decisions",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Setup middleware
setup_middleware(app)

# Include API routes
app.include_router(api_router, prefix="/v1")


@app.get("/", include_in_schema=False)
async def root() -> JSONResponse:
    """Root endpoint with API information.

    Returns:
        API info and links
    """
    return JSONResponse(
        content={
            "service": "Decision Calm Engine API",
            "version": "0.1.0",
            "status": "running",
            "docs": "/docs",
            "health": "/v1/health",
        }
    )


@app.get("/health", include_in_schema=False)
async def health_check() -> JSONResponse:
    """Health check endpoint (Docker healthcheck compatible).

    Returns:
        Health status
    """
    return JSONResponse(content={"status": "healthy"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower(),
    )
