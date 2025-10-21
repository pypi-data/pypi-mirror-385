"""
Main FastAPI application for code_developer control API.

This API provides endpoints for:
- Starting/stopping/monitoring the daemon
- File operations (ROADMAP.md, project files)
- Notification management
- Real-time log streaming via WebSocket
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting code_developer control API")
    logger.info(f"Environment: {os.getenv('COFFEE_MAKER_MODE', 'unknown')}")
    logger.info(f"Project: {os.getenv('GCP_PROJECT_ID', 'unknown')}")

    yield

    # Shutdown
    logger.info("Shutting down code_developer control API")


# Create FastAPI app
app = FastAPI(
    title="Code Developer Control API",
    description="REST API for controlling code_developer autonomous daemon",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


# Root endpoint
@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint with API information."""
    return {
        "service": "code_developer",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


# Health check endpoint
@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "service": "code_developer"}


# Import and include routers
from coffee_maker.api.routes import daemon, files, status

app.include_router(daemon.router, prefix="/api/daemon", tags=["daemon"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(status.router, prefix="/api/status", tags=["status"])


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "coffee_maker.api.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=os.getenv("COFFEE_MAKER_MODE") == "dev",
    )
