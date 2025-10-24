"""
Hackathon Beszketnyky - Main FastAPI Application
================================================

Backend API dla orkiestracji agentów AI z wykorzystaniem LangGraph.
Stack: Python + FastAPI + LangGraph + Scaleway + OpenAI
"""

from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import logging
import structlog
from contextlib import asynccontextmanager

from agents.langgraph_config import agent_graph
from database.connection import init_database
from services.scaleway_service import ScalewayService
from utils.config import get_settings

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
logger = structlog.get_logger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Zarządzanie cyklem życia aplikacji"""
    # Startup
    logger.info("Inicjalizacja aplikacji...")
    await init_database()
    logger.info("Aplikacja zainicjalizowana pomyślnie")
    
    yield
    
    # Shutdown
    logger.info("Zamykanie aplikacji...")

# Utworzenie instancji FastAPI
app = FastAPI(
    title="Hackathon Beszketnyky API",
    description="API dla orkiestracji agentów AI z wykorzystaniem LangGraph i Scaleway",
    version="1.0.0",
    lifespan=lifespan
)

# Konfiguracja CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== MODELE PYDANTIC ======

class AgentRequest(BaseModel):
    """Request model dla komunikacji z agentami"""
    message: str
    thread_id: Optional[str] = None
    user_id: Optional[str] = None
    agent_type: Optional[str] = "workforce"  # "workforce" lub "strategist"
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    """Response model od agentów"""
    response: str
    thread_id: str
    agent_used: str
    metadata: Optional[Dict[str, Any]] = None

class HealthCheck(BaseModel):
    """Model dla health check"""
    status: str
    version: str
    environment: str
    database_connected: bool
    scaleway_connected: bool

# ====== ENDPOINT GŁÓWNY ======

@app.post("/agent", response_model=AgentResponse)
async def run_agent(request: AgentRequest, background_tasks: BackgroundTasks):
    """
    Główny endpoint do komunikacji z agentami AI
    
    Orkiestruje wybór odpowiedniego agenta (Workforce/Strategist) 
    na podstawie kontekstu i typu żądania.
    """
    try:
        logger.info("Otrzymano request do agenta", 
                   message_length=len(request.message),
                   agent_type=request.agent_type,
                   thread_id=request.thread_id)
        
        # Konfiguracja dla LangGraph
        config = {
            "configurable": {
                "thread_id": request.thread_id or f"thread_{hash(request.message)}",
                "user_id": request.user_id,
                "agent_type": request.agent_type
            }
        }
        
        # Przygotowanie stanu początkowego
        initial_state = {
            "messages": [{"role": "human", "content": request.message}],
            "agent_type": request.agent_type,
            "context": request.context or {}
        }
        
        # Wywołanie LangGraph
        result = await agent_graph.ainvoke(initial_state, config)
        
        # Logowanie w tle
        background_tasks.add_task(
            log_interaction,
            request.message,
            result.get("messages", [])[-1].get("content", ""),
            request.thread_id,
            request.agent_type
        )
        
        return AgentResponse(
            response=result.get("messages", [])[-1].get("content", "Przepraszam, wystąpił błąd."),
            thread_id=config["configurable"]["thread_id"],
            agent_used=result.get("agent_used", request.agent_type),
            metadata=result.get("metadata", {})
        )
        
    except Exception as e:
        logger.error("Błąd podczas przetwarzania requestu", error=str(e))
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")

# ====== ENDPOINT STRUMIENIOWY ======

@app.post("/agent/stream")
async def stream_agent_response(request: AgentRequest):
    """
    Endpoint do strumieniowego otrzymywania odpowiedzi od agentów
    """
    try:
        config = {
            "configurable": {
                "thread_id": request.thread_id or f"thread_{hash(request.message)}",
                "user_id": request.user_id,
                "agent_type": request.agent_type
            }
        }
        
        initial_state = {
            "messages": [{"role": "human", "content": request.message}],
            "agent_type": request.agent_type,
            "context": request.context or {}
        }
        
        async def generate_response():
            async for chunk in agent_graph.astream(initial_state, config):
                if "messages" in chunk and chunk["messages"]:
                    yield f"data: {chunk['messages'][-1].get('content', '')}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/stream",
            headers={"Cache-Control": "no-cache"}
        )
        
    except Exception as e:
        logger.error("Błąd podczas streamingu", error=str(e))
        raise HTTPException(status_code=500, detail=f"Błąd streamingu: {str(e)}")

# ====== ENDPOINTY POMOCNICZE ======

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    try:
        # Sprawdzenie połączenia z bazą danych
        db_connected = await check_database_connection()
        
        # Sprawdzenie połączenia z Scaleway
        scaleway_service = ScalewayService()
        scaleway_connected = await scaleway_service.check_connection()
        
        return HealthCheck(
            status="healthy" if db_connected and scaleway_connected else "degraded",
            version="1.0.0",
            environment=settings.ENVIRONMENT,
            database_connected=db_connected,
            scaleway_connected=scaleway_connected
        )
    except Exception as e:
        logger.error("Błąd health check", error=str(e))
        return HealthCheck(
            status="unhealthy",
            version="1.0.0",
            environment=settings.ENVIRONMENT,
            database_connected=False,
            scaleway_connected=False
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Hackathon Beszketnyky API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# ====== FUNKCJE POMOCNICZE ======

async def log_interaction(user_message: str, ai_response: str, thread_id: str, agent_type: str):
    """Logowanie interakcji w tle"""
    try:
        logger.info("Interakcja z agentem",
                   thread_id=thread_id,
                   agent_type=agent_type,
                   user_message_length=len(user_message),
                   ai_response_length=len(ai_response))
        # Tutaj można dodać zapis do bazy danych
    except Exception as e:
        logger.warning("Błąd logowania interakcji", error=str(e))

async def check_database_connection() -> bool:
    """Sprawdzenie połączenia z bazą danych"""
    try:
        from database.connection import get_database_session
        async with get_database_session() as session:
            await session.execute("SELECT 1")
        return True
    except Exception:
        return False

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )