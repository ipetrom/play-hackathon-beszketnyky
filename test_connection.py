from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, Boolean, Date, Time, JSON, text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

# 🔹 Данные для подключения
DB_USER = "root"
DB_PASS = "cXf2dtQlN8m6*{tef,]B"
DB_HOST = "151.115.13.23"
DB_PORT = "12061"
DB_NAME = "rdb"
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# === Инициализация ORM ===
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# === Smart Tracker Models ===
class User(Base):
    __tablename__ = "users"

    user_email = Column(String(255), primary_key=True)
    user_name = Column(String(255), nullable=False)
    report_time = Column(Time, default=text("'09:00:00'"))
    report_delay_days = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    is_active = Column(Boolean, default=True)

class Report(Base):
    __tablename__ = "reports"

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_email = Column(String(255), ForeignKey('users.user_email', ondelete='CASCADE'), nullable=False)
    report_date = Column(Date, nullable=False)
    report_status = Column(String(20), nullable=False, default='draft')
    report_domains = Column(JSONB, nullable=False, default=text("'[]'::jsonb"))
    report_alerts = Column(Integer, default=0)
    report_tips = Column(Integer, default=0)
    report_alerts_tips_json_path = Column(String(500))
    path_to_report = Column(String(500))
    path_to_report_vector = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp())

# === Создание схемы ===
def init_smart_tracker_db():
    print("🚀 Создаём схему Smart Tracker...")
    
    with engine.connect() as connection:
        # Создаем расширение UUID
        connection.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        
        # Удаляем старые таблицы если они существуют (для чистой установки)
        connection.execute(text('DROP TABLE IF EXISTS reports CASCADE'))
        connection.execute(text('DROP TABLE IF EXISTS users CASCADE'))
        
        connection.commit()
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    # Создаем индексы
    with engine.connect() as connection:
        # Users indexes
        connection.execute(text('CREATE INDEX IF NOT EXISTS idx_users_email ON users(user_email)'))
        connection.execute(text('CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)'))
        
        # Reports indexes
        connection.execute(text('CREATE INDEX IF NOT EXISTS idx_reports_user_email ON reports(user_email)'))
        connection.execute(text('CREATE INDEX IF NOT EXISTS idx_reports_date ON reports(report_date)'))
        connection.execute(text('CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(report_status)'))
        connection.execute(text('CREATE INDEX IF NOT EXISTS idx_reports_domains ON reports USING gin(report_domains)'))
        connection.execute(text('CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at)'))
        connection.execute(text('CREATE INDEX IF NOT EXISTS idx_reports_user_status ON reports(user_email, report_status)'))
        connection.execute(text('CREATE INDEX IF NOT EXISTS idx_reports_user_date ON reports(user_email, report_date)'))
        
        # Добавляем constraints
        connection.execute(text("""
            ALTER TABLE reports 
            ADD CONSTRAINT chk_report_status 
            CHECK (report_status IN ('draft', 'published', 'archived'))
        """))
        
        connection.commit()
    
    print("✅ Схема Smart Tracker успешно создана!")

# === Вставка демо данных ===
def insert_demo_data():
    session = SessionLocal()
    
    # Демо пользователь
    demo_user = User(
        user_email="demo@play.pl",
        user_name="Play Demo User",
        report_delay_days=1
    )
    
    # Проверяем, существует ли пользователь
    existing_user = session.query(User).filter_by(user_email="demo@play.pl").first()
    if not existing_user:
        session.add(demo_user)
        session.commit()
        print("✅ Демо пользователь создан!")
    else:
        print("ℹ️  Демо пользователь уже существует")
    
    # Демо отчет
    from datetime import date
    demo_report = Report(
        user_email="demo@play.pl",
        report_date=date.today(),
        report_status="published",
        report_domains=["prawo", "polityka", "financial"],
        report_alerts=3,
        report_tips=5,
        report_alerts_tips_json_path="demo@play.pl/reports/2025-01-25/tips_alerts.json",
        path_to_report="demo@play.pl/reports/2025-01-25/report.txt",
        path_to_report_vector="demo@play.pl/reports/2025-01-25/vectors/"
    )
    
    # Проверяем, существует ли отчет
    existing_report = session.query(Report).filter_by(
        user_email="demo@play.pl", 
        report_date=date.today()
    ).first()
    
    if not existing_report:
        session.add(demo_report)
        session.commit()
        print("✅ Демо отчет создан!")
    else:
        print("ℹ️  Демо отчет уже существует")
    
    session.close()

# === Тестирование ===
def test_smart_tracker():
    session = SessionLocal()
    
    # Получаем всех пользователей
    users = session.query(User).all()
    print(f"\n👥 Всего пользователей: {len(users)}")
    for user in users:
        print(f"  📧 {user.user_email} - {user.user_name}")
    
    # Получаем все отчеты
    reports = session.query(Report).all()
    print(f"\n📊 Всего отчетов: {len(reports)}")
    for report in reports:
        print(f"  📄 {report.report_id} - {report.user_email} - {report.report_date}")
    
    session.close()

if __name__ == "__main__":
    init_smart_tracker_db()
    insert_demo_data()
    test_smart_tracker()