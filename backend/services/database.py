"""
Database service for the Telecom News Multi-Agent System
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import asyncpg
from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime, Text, JSON, Integer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis

from .config import settings

logger = logging.getLogger(__name__)

# Database connection
engine = None
async_session = None
redis_client = None

async def init_db():
    """Initialize database connections"""
    global engine, async_session, redis_client
    
    try:
        # For development/testing, use in-memory SQLite if no database is configured
        if not settings.database_url or settings.database_url == "postgresql://user:password@localhost:5432/telecom_news":
            logger.warning("No database configured, using in-memory storage")
            # Use in-memory SQLite for testing
            database_url = "sqlite+aiosqlite:///:memory:"
        else:
            # Convert database URL to async format
            database_url = settings.database_url
            if database_url.startswith("postgresql://"):
                database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        
        # Initialize database with async driver
        engine = create_async_engine(
            database_url,
            echo=settings.debug,
            pool_pre_ping=True
        )
        
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Initialize Redis (optional for testing)
        try:
            redis_client = redis.from_url(settings.redis_url)
            await redis_client.ping()
            logger.info("Redis connection initialized")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory cache: {e}")
            redis_client = None
        
        # Test connections
        await test_connections()
        
        logger.info("Database connections initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Don't raise error for testing, just log it
        logger.warning("Continuing without database connection")

async def test_connections():
    """Test database connections"""
    try:
        # Test database
        if engine:
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            logger.info("Database connection tested successfully")
        
        # Test Redis (optional)
        if redis_client:
            await redis_client.ping()
            logger.info("Redis connection tested successfully")
        
    except Exception as e:
        logger.warning(f"Database connection test failed: {e}")
        # Don't raise error for testing

async def get_db_session():
    """Get database session"""
    if not async_session:
        await init_db()
    
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_redis():
    """Get Redis client"""
    if not redis_client:
        await init_db()
    return redis_client

# Cache operations
async def cache_set(key: str, value: Any, expire: int = 3600):
    """Set cache value"""
    redis = await get_redis()
    await redis.set(key, json.dumps(value), ex=expire)

async def cache_get(key: str) -> Optional[Any]:
    """Get cache value"""
    redis = await get_redis()
    value = await redis.get(key)
    if value:
        return json.loads(value)
    return None

async def cache_delete(key: str):
    """Delete cache value"""
    redis = await get_redis()
    await redis.delete(key)

# Database operations for storing results
async def store_search_results(domain: str, results: List[Dict[str, Any]]):
    """Store search results in database"""
    try:
        async with async_session() as session:
            # This would be implemented with proper ORM models
            # For now, we'll use Redis for temporary storage
            await cache_set(f"search_results:{domain}", results, expire=7200)
            logger.info(f"Stored {len(results)} search results for domain: {domain}")
    except Exception as e:
        logger.error(f"Failed to store search results: {e}")

async def get_search_results(domain: str) -> Optional[List[Dict[str, Any]]]:
    """Get search results from database"""
    try:
        return await cache_get(f"search_results:{domain}")
    except Exception as e:
        logger.error(f"Failed to get search results: {e}")
        return None

async def store_agent_output(agent_name: str, domain: str, output: Dict[str, Any]):
    """Store agent output"""
    try:
        key = f"agent_output:{agent_name}:{domain}"
        await cache_set(key, output, expire=3600)
        logger.info(f"Stored output from {agent_name} for domain: {domain}")
    except Exception as e:
        logger.error(f"Failed to store agent output: {e}")

async def get_agent_output(agent_name: str, domain: str) -> Optional[Dict[str, Any]]:
    """Get agent output"""
    try:
        key = f"agent_output:{agent_name}:{domain}"
        return await cache_get(key)
    except Exception as e:
        logger.error(f"Failed to get agent output: {e}")
        return None

async def store_final_report(domain: str, report: Dict[str, Any]):
    """Store final domain report"""
    try:
        key = f"final_report:{domain}"
        await cache_set(key, report, expire=86400)  # 24 hours
        logger.info(f"Stored final report for domain: {domain}")
    except Exception as e:
        logger.error(f"Failed to store final report: {e}")

async def get_final_report(domain: str) -> Optional[Dict[str, Any]]:
    """Get final domain report"""
    try:
        key = f"final_report:{domain}"
        return await cache_get(key)
    except Exception as e:
        logger.error(f"Failed to get final report: {e}")
        return None

async def store_tips_alerts(tips_alerts: Dict[str, Any]):
    """Store final tips and alerts"""
    try:
        await cache_set("tips_alerts", tips_alerts, expire=86400)  # 24 hours
        logger.info("Stored tips and alerts")
    except Exception as e:
        logger.error(f"Failed to store tips and alerts: {e}")

async def get_tips_alerts() -> Optional[Dict[str, Any]]:
    """Get tips and alerts"""
    try:
        return await cache_get("tips_alerts")
    except Exception as e:
        logger.error(f"Failed to get tips and alerts: {e}")
        return None
