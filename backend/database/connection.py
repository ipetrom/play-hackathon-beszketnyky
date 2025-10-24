"""
Konfiguracja połączenia z bazą danych PostgreSQL z rozszerzeniem pgvector
"""

import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
import structlog

from utils.config import get_settings

logger = structlog.get_logger(__name__)

# SQLAlchemy Base
Base = declarative_base()

# Globalne zmienne
engine = None
async_session_maker = None

async def init_database():
    """Inicjalizacja połączenia z bazą danych"""
    global engine, async_session_maker
    
    settings = get_settings()
    
    try:
        # Utworzenie engine
        engine = create_async_engine(
            settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
            echo=settings.DEBUG,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        # Utworzenie session maker
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Sprawdzenie połączenia i instalacja rozszerzenia pgvector
        await setup_pgvector()
        
        logger.info("Połączenie z bazą danych zainicjalizowane pomyślnie")
        
    except Exception as e:
        logger.error("Błąd inicjalizacji bazy danych", error=str(e))
        raise

async def setup_pgvector():
    """Instalacja i konfiguracja rozszerzenia pgvector"""
    try:
        async with get_database_session() as session:
            # Sprawdzenie czy rozszerzenie pgvector jest dostępne
            result = await session.execute(
                text("SELECT 1 FROM pg_available_extensions WHERE name = 'vector'")
            )
            
            if result.fetchone():
                # Instalacja rozszerzenia jeśli nie jest już zainstalowane
                await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                await session.commit()
                logger.info("Rozszerzenie pgvector skonfigurowane pomyślnie")
            else:
                logger.warning("Rozszerzenie pgvector nie jest dostępne w tej instalacji PostgreSQL")
                
    except Exception as e:
        logger.error("Błąd konfiguracji pgvector", error=str(e))
        # Nie rzucamy błędu, aplikacja może działać bez pgvector

@asynccontextmanager
async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager dla sesji bazy danych"""
    if async_session_maker is None:
        raise RuntimeError("Baza danych nie została zainicjalizowana. Wywołaj init_database() najpierw.")
    
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_raw_connection():
    """Pobieranie surowego połączenia asyncpg dla operacji low-level"""
    settings = get_settings()
    
    # Parse URL do komponentów
    url = settings.database_url
    # Proste parsowanie - można użyć urllib.parse dla bardziej robust rozwiązania
    if "postgresql://" in url:
        url = url.replace("postgresql://", "")
        user_pass, host_db = url.split("@")
        user, password = user_pass.split(":")
        host_port, database = host_db.split("/")
        host, port = host_port.split(":") if ":" in host_port else (host_port, "5432")
        
        return await asyncpg.connect(
            user=user,
            password=password,
            database=database,
            host=host,
            port=int(port)
        )
    else:
        raise ValueError("Nieprawidłowy format URL bazy danych")

async def close_database():
    """Zamknięcie połączenia z bazą danych"""
    global engine
    if engine:
        await engine.dispose()
        logger.info("Połączenie z bazą danych zamknięte")

# Dependency dla FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency dla FastAPI do iniekcji sesji bazy danych"""
    async with get_database_session() as session:
        yield session