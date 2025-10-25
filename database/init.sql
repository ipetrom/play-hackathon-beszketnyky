-- Smart Tracker Database Schema
-- =============================
-- Clean, production-ready database for Smart Tracker system

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ====== USERS TABLE ======
CREATE TABLE users (
    user_email VARCHAR(255) PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    report_time TIME DEFAULT '09:00:00', -- Default 9:00 AM
    report_delay_days INTEGER DEFAULT 1, -- Default 1 day delay
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- ====== REPORTS TABLE ======
CREATE TABLE reports (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_email VARCHAR(255) NOT NULL REFERENCES users(user_email) ON DELETE CASCADE,
    report_date DATE NOT NULL,
    report_status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (report_status IN ('draft', 'published', 'archived')),
    report_domains JSONB NOT NULL DEFAULT '[]'::jsonb, -- ["prawo", "polityka", "financial"]
    report_alerts INTEGER DEFAULT 0,
    report_tips INTEGER DEFAULT 0,
    report_alerts_tips_json_path VARCHAR(500), -- Path to object storage JSON
    path_to_report VARCHAR(500), -- Path to TXT report in object storage
    path_to_report_vector VARCHAR(500), -- Path to vector DB for RAG
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ====== INDEXES ======
-- Users indexes
CREATE INDEX idx_users_email ON users(user_email);
CREATE INDEX idx_users_active ON users(is_active);

-- Reports indexes
CREATE INDEX idx_reports_user_email ON reports(user_email);
CREATE INDEX idx_reports_date ON reports(report_date);
CREATE INDEX idx_reports_status ON reports(report_status);
CREATE INDEX idx_reports_domains ON reports USING gin(report_domains);
CREATE INDEX idx_reports_created_at ON reports(created_at);

-- Composite indexes for common queries
CREATE INDEX idx_reports_user_status ON reports(user_email, report_status);
CREATE INDEX idx_reports_user_date ON reports(user_email, report_date);

-- ====== TRIGGERS ======
-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reports_updated_at 
    BEFORE UPDATE ON reports 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ====== VIEWS ======
-- Active reports view
CREATE OR REPLACE VIEW active_reports AS
SELECT 
    r.report_id,
    r.user_email,
    u.user_name,
    r.report_date,
    r.report_status,
    r.report_domains,
    r.report_alerts,
    r.report_tips,
    r.created_at,
    r.updated_at
FROM reports r
JOIN users u ON r.user_email = u.user_email
WHERE u.is_active = TRUE
ORDER BY r.report_date DESC, r.created_at DESC;

-- User report statistics
CREATE OR REPLACE VIEW user_report_stats AS
SELECT 
    u.user_email,
    u.user_name,
    COUNT(r.report_id) as total_reports,
    COUNT(CASE WHEN r.report_status = 'published' THEN 1 END) as published_reports,
    COUNT(CASE WHEN r.report_status = 'draft' THEN 1 END) as draft_reports,
    COUNT(CASE WHEN r.report_status = 'archived' THEN 1 END) as archived_reports,
    MAX(r.report_date) as latest_report_date,
    MIN(r.report_date) as first_report_date
FROM users u
LEFT JOIN reports r ON u.user_email = r.user_email
WHERE u.is_active = TRUE
GROUP BY u.user_email, u.user_name;

-- ====== SAMPLE DATA ======
-- Insert demo user
INSERT INTO users (user_email, user_name, report_time, report_delay_days) VALUES
('demo@play.pl', 'Play Demo User', '09:00:00', 1)
ON CONFLICT (user_email) DO NOTHING;

-- Insert sample report
INSERT INTO reports (
    user_email, 
    report_date, 
    report_status, 
    report_domains, 
    report_alerts, 
    report_tips,
    report_alerts_tips_json_path,
    path_to_report,
    path_to_report_vector
) VALUES (
    'demo@play.pl',
    CURRENT_DATE,
    'published',
    '["prawo", "polityka", "financial"]'::jsonb,
    3,
    5,
    'demo@play.pl/reports/2025-01-25/tips_alerts.json',
    'demo@play.pl/reports/2025-01-25/report.txt',
    'demo@play.pl/reports/2025-01-25/vectors/'
) ON CONFLICT DO NOTHING;

-- ====== COMMENTS ======
COMMENT ON TABLE users IS 'Smart Tracker users - identified by email';
COMMENT ON TABLE reports IS 'User reports with paths to object storage files';
COMMENT ON COLUMN reports.report_domains IS 'JSON array of domains: prawo, polityka, financial';
COMMENT ON COLUMN reports.report_status IS 'Report status: draft, published, or archived';
COMMENT ON COLUMN reports.report_alerts IS 'Number of alerts in the report';
COMMENT ON COLUMN reports.report_tips IS 'Number of tips in the report';
COMMENT ON COLUMN reports.report_alerts_tips_json_path IS 'Path to JSON file in object storage';
COMMENT ON COLUMN reports.path_to_report IS 'Path to TXT report in object storage';
COMMENT ON COLUMN reports.path_to_report_vector IS 'Path to vector database for RAG';