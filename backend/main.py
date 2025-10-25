"""
Telecom News Multi-Agent System
FastAPI backend for tracking Poland's telecommunications market
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
from typing import Dict, List, Optional
import json
from datetime import datetime

from api.routes import router as api_router
from services.config import settings
from services.database_simple import init_db
from agents.workflow import TelecomWorkflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Telecom News Multi-Agent System...")
    init_db()  # Remove await since it's synchronous
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Telecom News Multi-Agent System...")

# Create FastAPI app
app = FastAPI(
    title="Telecom News Multi-Agent System",
    description="Automated system for tracking Poland's telecommunications market",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Global workflow instance
workflow = None

@app.on_event("startup")
async def startup_event():
    """Initialize the workflow on startup"""
    global workflow
    workflow = TelecomWorkflow()
    logger.info("Telecom workflow initialized")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Telecom News Multi-Agent System",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "workflow_initialized": workflow is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
