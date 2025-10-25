"""
New Database service for Smart Tracker
Clean implementation with PostgreSQL
"""

import asyncio
import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, date, time
import asyncpg
from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime, Text, JSON, Integer, Boolean, Date, UUID, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .config import settings

logger = logging.getLogger(__name__)

# Database connection
engine = None
async_session = None

async def init_db():
    """Initialize database connections"""
    global engine, async_session
    
    try:
        # Database URL configuration
        database_url = settings.database_url or "postgresql://smart_tracker_user:smart_tracker_password@localhost:5432/smart_tracker"
        
        # Convert to async format
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
        
        logger.info("Database-only mode initialized")
        
        # Test connections
        await test_connections()
        
        logger.info("Database connections initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def test_connections():
    """Test database connections"""
    try:
        # Test database
        if engine:
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                row = result.fetchone()
                logger.info(f"Database test result: {row}")
            logger.info("Database connection tested successfully")
        
        logger.info("Database connection test completed")
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        raise

async def get_db_session():
    """Get database session"""
    if not async_session:
        await init_db()
    
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# ====== USER OPERATIONS ======

async def create_user(user_email: str, user_name: str, report_time: str = "09:00:00", report_delay_days: int = 1) -> Dict[str, Any]:
    """Create a new user"""
    try:
        async with async_session() as session:
            # Check if user already exists
            result = await session.execute(
                text("SELECT user_email FROM users WHERE user_email = :user_email"),
                {"user_email": user_email}
            )
            if result.fetchone():
                return {"status": "error", "message": "User already exists"}
            
            # Convert string time to time object
            time_obj = time.fromisoformat(report_time)
            
            # Create user
            await session.execute(
                text("INSERT INTO users (user_email, user_name, report_time, report_delay_days) VALUES (:user_email, :user_name, :report_time, :report_delay_days)"),
                {
                    "user_email": user_email, 
                    "user_name": user_name, 
                    "report_time": time_obj, 
                    "report_delay_days": report_delay_days
                }
            )
            await session.commit()
            
            logger.info(f"Created user: {user_email}")
            return {"status": "success", "user_email": user_email}
            
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        return {"status": "error", "message": str(e)}

async def get_user(user_email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    try:
        async with async_session() as session:
            result = await session.execute(
                text("SELECT user_email, user_name, report_time, report_delay_days, created_at, is_active FROM users WHERE user_email = :user_email"),
                {"user_email": user_email}
            )
            row = result.fetchone()
            if row:
                return {
                    "user_email": row[0],
                    "user_name": row[1],
                    "report_time": str(row[2]),
                    "report_delay_days": row[3],
                    "created_at": row[4],
                    "is_active": row[5]
                }
            return None
            
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        return None

async def update_user_settings(user_email: str, report_time: str = None, report_delay_days: int = None) -> Dict[str, Any]:
    """Update user settings"""
    try:
        async with async_session() as session:
            # Build update query dynamically
            updates = []
            params = {"user_email": user_email}
            
            if report_time is not None:
                updates.append("report_time = :report_time")
                params["report_time"] = time.fromisoformat(report_time)
                
            if report_delay_days is not None:
                updates.append("report_delay_days = :report_delay_days")
                params["report_delay_days"] = report_delay_days
            
            if not updates:
                return {"status": "error", "message": "No updates provided"}
            
            query = f"UPDATE users SET {', '.join(updates)} WHERE user_email = :user_email"
            await session.execute(text(query), params)
            await session.commit()
            
            logger.info(f"Updated user settings for: {user_email}")
            return {"status": "success", "user_email": user_email}
            
    except Exception as e:
        logger.error(f"Failed to update user settings: {e}")
        return {"status": "error", "message": str(e)}

# ====== REPORT OPERATIONS ======

async def create_report(
    user_email: str,
    report_date: date,
    report_domains: List[str],
    report_alerts: int = 0,
    report_tips: int = 0,
    report_alerts_tips_json_path: Optional[str] = None,
    path_to_report: Optional[str] = None,
    path_to_report_vector: Optional[str] = None,
    report_status: str = "draft"
) -> Dict[str, Any]:
    """Create a new report"""
    try:
        async with async_session() as session:
            # Create report
            result = await session.execute(
                text("""INSERT INTO reports (
                    user_email, report_date, report_status, report_domains,
                    report_alerts, report_tips, report_alerts_tips_json_path,
                    path_to_report, path_to_report_vector
                ) VALUES (:user_email, :report_date, :report_status, :report_domains,
                         :report_alerts, :report_tips, :report_alerts_tips_json_path,
                         :path_to_report, :path_to_report_vector)
                RETURNING report_id"""),
                {
                    "user_email": user_email,
                    "report_date": report_date,
                    "report_status": report_status,
                    "report_domains": json.dumps(report_domains),  # Convert list to JSON string
                    "report_alerts": report_alerts,
                    "report_tips": report_tips,
                    "report_alerts_tips_json_path": report_alerts_tips_json_path,
                    "path_to_report": path_to_report,
                    "path_to_report_vector": path_to_report_vector
                }
            )
            
            report_id = result.fetchone()
            await session.commit()
            
            logger.info(f"Created report {report_id[0]} for user {user_email}")
            return {
                "status": "success",
                "report_id": str(report_id[0]),
                "user_email": user_email
            }
            
    except Exception as e:
        logger.error(f"Failed to create report: {e}")
        return {"status": "error", "message": str(e)}

async def get_user_reports(user_email: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all reports for a user"""
    try:
        async with async_session() as session:
            if status:
                result = await session.execute(
                    text("""SELECT report_id, report_date, report_status, report_domains,
                              report_alerts, report_tips, created_at
                       FROM reports 
                       WHERE user_email = :user_email AND report_status = :status
                       ORDER BY report_date DESC"""),
                    {"user_email": user_email, "status": status}
                )
            else:
                result = await session.execute(
                    text("""SELECT report_id, report_date, report_status, report_domains,
                              report_alerts, report_tips, created_at
                       FROM reports 
                       WHERE user_email = :user_email
                       ORDER BY report_date DESC"""),
                    {"user_email": user_email}
                )
            
            rows = result.fetchall()
            return [
                {
                    "report_id": str(row[0]),
                    "report_date": row[1],
                    "report_status": row[2],
                    "report_domains": row[3],
                    "report_alerts": row[4],
                    "report_tips": row[5],
                    "created_at": row[6]
                }
                for row in rows
            ]
            
    except Exception as e:
        logger.error(f"Failed to get user reports: {e}")
        return []

async def get_report(report_id: str) -> Optional[Dict[str, Any]]:
    """Get specific report by ID"""
    try:
        async with async_session() as session:
            result = await session.execute(
                text("""SELECT r.report_id, r.user_email, u.user_name, r.report_date,
                              r.report_status, r.report_domains, r.report_alerts,
                              r.report_tips, r.report_alerts_tips_json_path,
                              r.path_to_report, r.path_to_report_vector, r.created_at
                       FROM reports r
                       JOIN users u ON r.user_email = u.user_email
                       WHERE r.report_id = :report_id"""),
                {"report_id": report_id}
            )
            
            row = result.fetchone()
            if row:
                return {
                    "report_id": str(row[0]),
                    "user_email": row[1],
                    "user_name": row[2],
                    "report_date": row[3],
                    "report_status": row[4],
                    "report_domains": row[5],
                    "report_alerts": row[6],
                    "report_tips": row[7],
                    "report_alerts_tips_json_path": row[8],
                    "path_to_report": row[9],
                    "path_to_report_vector": row[10],
                    "created_at": row[11]
                }
            return None
            
    except Exception as e:
        logger.error(f"Failed to get report: {e}")
        return None

async def update_report_status(report_id: str, status: str) -> Dict[str, Any]:
    """Update report status"""
    try:
        async with async_session() as session:
            await session.execute(
                text("UPDATE reports SET report_status = :status WHERE report_id = :report_id"),
                {"status": status, "report_id": report_id}
            )
            await session.commit()
            
            logger.info(f"Updated report {report_id} status to {status}")
            return {"status": "success", "report_id": report_id}
            
    except Exception as e:
        logger.error(f"Failed to update report status: {e}")
        return {"status": "error", "message": str(e)}

# ====== CACHE OPERATIONS (Database-only) ======
# Note: All data is stored directly in PostgreSQL database
# No external caching layer needed
