"""
Simple Database service for Smart Tracker
Uses external managed PostgreSQL database without complex config
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, date, time
from sqlalchemy import create_engine, text, Column, String, DateTime, Integer, Boolean, Date, Time, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import sessionmaker, declarative_base
import uuid
import json

logger = logging.getLogger(__name__)

# Database connection
engine = None
SessionLocal = None
Base = declarative_base()

# ====== DATABASE MODELS ======

class User(Base):
    __tablename__ = "users"
    
    user_email = Column(String(255), primary_key=True)
    user_name = Column(String(255), nullable=False)
    report_time = Column(Time, default=time(9, 0, 0))
    report_delay_days = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Report(Base):
    __tablename__ = "reports"
    
    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_email = Column(String(255), nullable=False)
    report_date = Column(Date, nullable=False)
    report_status = Column(String(20), nullable=False, default='draft')
    report_domains = Column(JSONB, nullable=False, default=text("'[]'::jsonb"))
    report_alerts = Column(Integer, default=0)
    report_tips = Column(Integer, default=0)
    report_alerts_tips_json_path = Column(String(500))
    path_to_report = Column(String(500))
    path_to_report_vector = Column(String(500))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db():
    """Initialize database connections"""
    global engine, SessionLocal
    
    try:
        # Direct database URL
        database_url = "postgresql://root:cXf2dtQlN8m6*{tef,]B@151.115.13.23:12061/rdb"
        
        # Initialize database with synchronous driver
        engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True
        )
        
        SessionLocal = sessionmaker(bind=engine)
        
        logger.info("Simple managed database initialized")
        
        # Test connection
        test_connection()
        
        logger.info("Database connections initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def test_connection():
    """Test database connection"""
    try:
        if engine:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                row = result.fetchone()
                logger.info(f"Database test result: {row}")
            logger.info("Database connection tested successfully")
        
        logger.info("Database connection test completed")
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        raise

# ====== USER OPERATIONS ======

def create_user(user_email: str, user_name: str, report_time: str = "09:00:00", report_delay_days: int = 1) -> Dict[str, Any]:
    """Create a new user"""
    try:
        session = SessionLocal()
        
        # Check if user already exists
        existing_user = session.query(User).filter_by(user_email=user_email).first()
        if existing_user:
            session.close()
            return {"status": "error", "message": "User already exists"}
        
        # Convert string time to time object
        time_obj = time.fromisoformat(report_time)
        
        # Create user
        user = User(
            user_email=user_email,
            user_name=user_name,
            report_time=time_obj,
            report_delay_days=report_delay_days
        )
        
        session.add(user)
        session.commit()
        session.close()
        
        logger.info(f"Created user: {user_email}")
        return {"status": "success", "user_email": user_email}
        
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        return {"status": "error", "message": str(e)}

def get_user(user_email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    try:
        session = SessionLocal()
        user = session.query(User).filter_by(user_email=user_email).first()
        session.close()
        
        if user:
            return {
                "user_email": user.user_email,
                "user_name": user.user_name,
                "report_time": str(user.report_time),
                "report_delay_days": user.report_delay_days,
                "created_at": user.created_at,
                "is_active": user.is_active
            }
        return None
        
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        return None

def update_user_settings(user_email: str, report_time: str = None, report_delay_days: int = None) -> Dict[str, Any]:
    """Update user settings"""
    try:
        session = SessionLocal()
        user = session.query(User).filter_by(user_email=user_email).first()
        
        if not user:
            session.close()
            return {"status": "error", "message": "User not found"}
        
        if report_time is not None:
            user.report_time = time.fromisoformat(report_time)
            
        if report_delay_days is not None:
            user.report_delay_days = report_delay_days
        
        session.commit()
        session.close()
        
        logger.info(f"Updated user settings for: {user_email}")
        return {"status": "success", "user_email": user_email}
        
    except Exception as e:
        logger.error(f"Failed to update user settings: {e}")
        return {"status": "error", "message": str(e)}

# ====== REPORT OPERATIONS ======

def create_report(
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
        session = SessionLocal()
        
        # Create report
        logger.info(f"Creating report with paths:")
        logger.info(f"  - report_alerts_tips_json_path: {report_alerts_tips_json_path}")
        logger.info(f"  - path_to_report: {path_to_report}")
        
        report = Report(
            user_email=user_email,
            report_date=report_date,
            report_status=report_status,
            report_domains=report_domains,  # SQLAlchemy will handle JSON conversion
            report_alerts=report_alerts,
            report_tips=report_tips,
            report_alerts_tips_json_path=report_alerts_tips_json_path,
            path_to_report=path_to_report,
            path_to_report_vector=path_to_report_vector
        )
        
        session.add(report)
        session.commit()
        
        # Debug: Check if the report was saved with the correct paths
        saved_report = session.query(Report).filter_by(report_id=report.report_id).first()
        if saved_report:
            logger.info(f"Saved report paths:")
            logger.info(f"  - report_alerts_tips_json_path: {saved_report.report_alerts_tips_json_path}")
            logger.info(f"  - path_to_report: {saved_report.path_to_report}")
        
        report_id = report.report_id
        session.close()
        
        logger.info(f"Created report {report_id} for user {user_email}")
        return {
            "status": "success",
            "report_id": str(report_id),
            "user_email": user_email
        }
        
    except Exception as e:
        logger.error(f"Failed to create report: {e}")
        return {"status": "error", "message": str(e)}

def get_user_reports(user_email: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all reports for a user"""
    try:
        session = SessionLocal()
        
        if status:
            reports = session.query(Report).filter_by(user_email=user_email, report_status=status).order_by(Report.report_date.desc()).all()
        else:
            reports = session.query(Report).filter_by(user_email=user_email).order_by(Report.report_date.desc()).all()
        
        session.close()
        
        return [
            {
                "report_id": str(report.report_id),
                "report_date": report.report_date,
                "report_status": report.report_status,
                "report_domains": report.report_domains,
                "report_alerts": report.report_alerts,
                "report_tips": report.report_tips,
                "created_at": report.created_at
            }
            for report in reports
        ]
        
    except Exception as e:
        logger.error(f"Failed to get user reports: {e}")
        return []

def get_report(report_id: str) -> Optional[Dict[str, Any]]:
    """Get specific report by ID"""
    try:
        session = SessionLocal()
        report = session.query(Report).filter_by(report_id=report_id).first()
        session.close()
        
        if report:
            return {
                "report_id": str(report.report_id),
                "user_email": report.user_email,
                "report_date": report.report_date,
                "report_status": report.report_status,
                "report_domains": report.report_domains,
                "report_alerts": report.report_alerts,
                "report_tips": report.report_tips,
                "report_alerts_tips_json_path": report.report_alerts_tips_json_path,
                "path_to_report": report.path_to_report,
                "path_to_report_vector": report.path_to_report_vector,
                "created_at": report.created_at
            }
        return None
        
    except Exception as e:
        logger.error(f"Failed to get report: {e}")
        return None

def update_report_status(report_id: str, status: str) -> Dict[str, Any]:
    """Update report status"""
    try:
        session = SessionLocal()
        report = session.query(Report).filter_by(report_id=report_id).first()
        
        if not report:
            session.close()
            return {"status": "error", "message": "Report not found"}
        
        report.report_status = status
        session.commit()
        session.close()
        
        logger.info(f"Updated report {report_id} status to {status}")
        return {"status": "success", "report_id": report_id}
        
    except Exception as e:
        logger.error(f"Failed to update report status: {e}")
        return {"status": "error", "message": str(e)}
