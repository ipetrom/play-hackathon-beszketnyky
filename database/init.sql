-- Hackathon Beszketnyky - Inicjalizacja bazy danych PostgreSQL z pgvector
-- =====================================================================

-- Instalacja rozszerzenia pgvector (jeśli jest dostępne)
CREATE EXTENSION IF NOT EXISTS vector;

-- ====== TABELE GŁÓWNE ======

-- Tabela użytkowników
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Tabela wątków konwersacji
CREATE TABLE IF NOT EXISTS conversation_threads (
    id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL DEFAULT 'Nowa rozmowa',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Tabela wiadomości
CREATE TABLE IF NOT EXISTS messages (
    id VARCHAR(255) PRIMARY KEY,
    thread_id VARCHAR(255) REFERENCES conversation_threads(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    agent_used VARCHAR(50), -- 'workforce', 'strategist', 'supervisor'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Indeksy
    INDEX idx_messages_thread_id (thread_id),
    INDEX idx_messages_created_at (created_at),
    INDEX idx_messages_agent_used (agent_used)
);

-- ====== TABELE RAG I DOKUMENTY ======

-- Tabela dokumentów
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- 'upload', 'url', 'api', 'manual'
    source_reference VARCHAR(1000),
    file_path VARCHAR(500),
    file_size INTEGER,
    mime_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Indeksy
    INDEX idx_documents_source_type (source_type),
    INDEX idx_documents_created_at (created_at),
    INDEX idx_documents_is_active (is_active)
);

-- Tabela embeddingów (jeśli pgvector jest dostępne)
CREATE TABLE IF NOT EXISTS document_embeddings (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL DEFAULT 0,
    chunk_text TEXT NOT NULL,
    embedding vector(1536), -- OpenAI embeddings dimension
    model_name VARCHAR(100) NOT NULL DEFAULT 'text-embedding-ada-002',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indeksy
    INDEX idx_embeddings_document_id (document_id),
    INDEX idx_embeddings_model (model_name)
);

-- Jeśli pgvector nie jest dostępne, stwórz alternatywną tabelę
CREATE TABLE IF NOT EXISTS document_embeddings_fallback (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL DEFAULT 0,
    chunk_text TEXT NOT NULL,
    embedding_json TEXT NOT NULL, -- JSON array jako string
    model_name VARCHAR(100) NOT NULL DEFAULT 'text-embedding-ada-002',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indeksy
    INDEX idx_embeddings_fallback_document_id (document_id),
    INDEX idx_embeddings_fallback_model (model_name)
);

-- ====== TABELE AGENTÓW I ANALITYKI ======

-- Tabela logów interakcji z agentami
CREATE TABLE IF NOT EXISTS agent_interactions (
    id SERIAL PRIMARY KEY,
    thread_id VARCHAR(255) REFERENCES conversation_threads(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    agent_type VARCHAR(50) NOT NULL, -- 'workforce', 'strategist', 'supervisor'
    input_message TEXT NOT NULL,
    output_message TEXT NOT NULL,
    processing_time_ms INTEGER,
    token_usage JSONB DEFAULT '{}'::jsonb,
    model_used VARCHAR(100),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Indeksy
    INDEX idx_interactions_agent_type (agent_type),
    INDEX idx_interactions_created_at (created_at),
    INDEX idx_interactions_user_id (user_id),
    INDEX idx_interactions_success (success)
);

-- Tabela decyzji routingu supervisora
CREATE TABLE IF NOT EXISTS routing_decisions (
    id SERIAL PRIMARY KEY,
    thread_id VARCHAR(255) REFERENCES conversation_threads(id) ON DELETE CASCADE,
    user_message TEXT NOT NULL,
    target_agent VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(3,2),
    reasoning TEXT,
    context_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indeksy
    INDEX idx_routing_thread_id (thread_id),
    INDEX idx_routing_target_agent (target_agent),
    INDEX idx_routing_created_at (created_at)
);

-- ====== TABELE KONFIGURACJI ======

-- Tabela ustawień aplikacji
CREATE TABLE IF NOT EXISTS app_settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL,
    value_type VARCHAR(20) DEFAULT 'string', -- 'string', 'number', 'boolean', 'json'
    description TEXT,
    is_sensitive BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela ustawień użytkowników
CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    setting_key VARCHAR(100) NOT NULL,
    setting_value TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, setting_key),
    INDEX idx_user_settings_user_id (user_id)
);

-- ====== FUNKCJE I TRIGGERY ======

-- Funkcja aktualizacji timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggery dla aktualizacji updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_threads_updated_at 
    BEFORE UPDATE ON conversation_threads 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at 
    BEFORE UPDATE ON documents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_app_settings_updated_at 
    BEFORE UPDATE ON app_settings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at 
    BEFORE UPDATE ON user_settings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ====== DANE POCZĄTKOWE ======

-- Ustawienia domyślne aplikacji
INSERT INTO app_settings (key, value, value_type, description) VALUES
('default_agent', 'auto', 'string', 'Domyślny agent do używania'),
('max_tokens_workforce', '1024', 'number', 'Maksymalna liczba tokenów dla Workforce Agent'),
('max_tokens_strategist', '2048', 'number', 'Maksymalna liczba tokenów dla Strategist Agent'),
('temperature_workforce', '0.7', 'number', 'Temperatura dla Workforce Agent'),
('temperature_strategist', '0.6', 'number', 'Temperatura dla Strategist Agent'),
('enable_streaming', 'true', 'boolean', 'Włącz streaming odpowiedzi'),
('max_conversation_history', '10', 'number', 'Maksymalna liczba wiadomości w kontekście'),
('embedding_model', 'text-embedding-ada-002', 'string', 'Model do generowania embeddingów'),
('chunk_size', '1000', 'number', 'Rozmiar chunków dla RAG'),
('chunk_overlap', '200', 'number', 'Nakładanie się chunków')
ON CONFLICT (key) DO NOTHING;

-- Użytkownik demo (hasło: demo123)
INSERT INTO users (username, email, password_hash) VALUES
('demo', 'demo@hackathon.dev', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdenF.FUyDe8u7K')
ON CONFLICT (username) DO NOTHING;

-- ====== INDEKSY DODATKOWE ======

-- Indeks dla wyszukiwania pełnotekstowego w dokumentach
CREATE INDEX IF NOT EXISTS idx_documents_content_fulltext ON documents USING gin(to_tsvector('polish', content));

-- Indeks dla wyszukiwania w wiadomościach
CREATE INDEX IF NOT EXISTS idx_messages_content_fulltext ON messages USING gin(to_tsvector('polish', content));

-- Indeks dla metadanych JSON
CREATE INDEX IF NOT EXISTS idx_documents_metadata ON documents USING gin(metadata);
CREATE INDEX IF NOT EXISTS idx_messages_metadata ON messages USING gin(metadata);
CREATE INDEX IF NOT EXISTS idx_interactions_metadata ON agent_interactions USING gin(metadata);

-- ====== WIDOKI POMOCNICZE ======

-- Widok statystyk agentów
CREATE OR REPLACE VIEW agent_stats AS
SELECT 
    agent_type,
    COUNT(*) as total_interactions,
    AVG(processing_time_ms) as avg_processing_time,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_interactions,
    ROUND(SUM(CASE WHEN success THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate
FROM agent_interactions 
GROUP BY agent_type;

-- Widok aktywnych konwersacji
CREATE OR REPLACE VIEW active_conversations AS
SELECT 
    ct.id,
    ct.title,
    ct.user_id,
    u.username,
    ct.created_at,
    ct.updated_at,
    COUNT(m.id) as message_count,
    MAX(m.created_at) as last_message_at
FROM conversation_threads ct
LEFT JOIN users u ON ct.user_id = u.id
LEFT JOIN messages m ON ct.id = m.thread_id
WHERE ct.is_active = TRUE
GROUP BY ct.id, ct.title, ct.user_id, u.username, ct.created_at, ct.updated_at
ORDER BY ct.updated_at DESC;

-- ====== KOMENTARZE KOŃCOWE ======

COMMENT ON DATABASE current_database() IS 'Hackathon Beszketnyky - AI Agents Platform Database';
COMMENT ON TABLE users IS 'Tabela użytkowników systemu';
COMMENT ON TABLE conversation_threads IS 'Wątki konwersacji między użytkownikami a agentami';
COMMENT ON TABLE messages IS 'Wiadomości w konwersacjach';
COMMENT ON TABLE documents IS 'Dokumenty do RAG (Retrieval-Augmented Generation)';
COMMENT ON TABLE document_embeddings IS 'Embeddingi dokumentów dla wyszukiwania semantycznego';
COMMENT ON TABLE agent_interactions IS 'Logi interakcji z agentami AI';
COMMENT ON TABLE routing_decisions IS 'Decyzje routingu supervisora między agentami';