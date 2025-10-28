-- (pgvector not required; using Qdrant for vectors)

-- Create chatbot database schema
CREATE TABLE IF NOT EXISTS kb_entries (
    id VARCHAR(255) PRIMARY KEY,
    category VARCHAR(100),
    language VARCHAR(10) DEFAULT 'en',
    canonical_answer TEXT,
    follow_up_suggestions TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chatbot_variables (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    message_text TEXT,
    response_text TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_cost_cents INTEGER DEFAULT 0,
    response_ms INTEGER DEFAULT 0,
    confidence_score DECIMAL(3,2),
    session_id VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS sessions (
    user_id VARCHAR(255) PRIMARY KEY,
    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    language VARCHAR(10) DEFAULT 'en',
    session_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_kb_entries_category ON kb_entries(category);
CREATE INDEX IF NOT EXISTS idx_kb_entries_status ON kb_entries(status);
CREATE INDEX IF NOT EXISTS idx_sessions_last_active ON sessions(last_active_at);

-- Insert default variables
INSERT INTO chatbot_variables (key, value) VALUES 
    ('store_name', 'ACME Shop'),
    ('ig_handle', '@acme_shop'),
    ('whatsapp_number', '+1234567890')
ON CONFLICT (key) DO NOTHING;
