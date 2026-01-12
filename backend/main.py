"""
FastAPI application entry point.
Registers all routers and configures middleware.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import traceback
import logging

from config import settings
from database import init_db
from routers import auth, kb, documents, chat

# Import models to register them with SQLAlchemy Base.metadata
# This is required for init_db to create tables
from models import User, KnowledgeBase, Document, Chunk, Conversation, Message

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup: Initialize database and create upload directory
    await init_db()
    os.makedirs(settings.upload_dir, exist_ok=True)
    logger.info("Application started successfully")
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="RAG Knowledge Base API",
    description="RAG Knowledge Base Q&A System with Citation Tracing",
    version="0.1.0",
    lifespan=lifespan,
)


# Exception handler to log detailed errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to log errors with full traceback."""
    tb = traceback.format_exc()
    logger.error(f"Unhandled exception: {exc}\n{tb}")
    print(f"ERROR: {exc}")
    print(tb)
    return JSONResponse(
        status_code=500,
        content={"error_code": "INTERNAL_ERROR", "message": str(exc)},
    )


# CORS middleware - allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers with /api prefix
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(kb.router, prefix="/api/kb", tags=["Knowledge Base"])
app.include_router(documents.router, prefix="/api/kb", tags=["Documents"])
app.include_router(chat.router, prefix="/api/kb", tags=["Chat"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api")
async def api_root():
    """API root endpoint."""
    return {
        "message": "RAG Knowledge Base API",
        "version": "0.1.0",
        "docs": "/docs",
    }

