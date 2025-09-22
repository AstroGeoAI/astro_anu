-- AstroGeo Database Schema
-- Compatible with PostgreSQL

-- Users table for authentication and user management
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create indexes for users table
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);

-- Query logs for tracking user interactions
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    query_text TEXT NOT NULL,
    query_type VARCHAR(50),
    processing_time_seconds FLOAT,
    result_status VARCHAR(20),
    result_summary TEXT,
    agents_involved JSONB,
    data_sources JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- Create indexes for query_logs table
CREATE INDEX idx_query_logs_user_id ON query_logs(user_id);
CREATE INDEX idx_query_logs_query_type ON query_logs(query_type);
CREATE INDEX idx_query_logs_created_at ON query_logs(created_at);
CREATE INDEX idx_query_logs_result_status ON query_logs(result_status);

-- API usage tracking for monitoring external API consumption
CREATE TABLE api_usage (
    id SERIAL PRIMARY KEY,
    api_provider VARCHAR(50) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    request_method VARCHAR(10),
    request_params JSONB,
    response_status INTEGER,
    response_time_ms FLOAT,
    data_size_bytes INTEGER,
    rate_limit_remaining INTEGER,
    error_message TEXT,
    user_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for api_usage table
CREATE INDEX idx_api_usage_api_provider ON api_usage(api_provider);
CREATE INDEX idx_api_usage_endpoint ON api_usage(endpoint);
CREATE INDEX idx_api_usage_created_at ON api_usage(created_at);
CREATE INDEX idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX idx_api_usage_response_status ON api_usage(response_status);

-- Feedback table for user ratings and system improvement
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    query_log_id INTEGER,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_type VARCHAR(50),
    feedback_text TEXT,
    is_resolved BOOLEAN DEFAULT FALSE,
    admin_response TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    category VARCHAR(50)
);

-- Create indexes for feedback table
CREATE INDEX idx_feedback_user_id ON feedback(user_id);
CREATE INDEX idx_feedback_query_log_id ON feedback(query_log_id);
CREATE INDEX idx_feedback_rating ON feedback(rating);
CREATE INDEX idx_feedback_created_at ON feedback(created_at);
CREATE INDEX idx_feedback_category ON feedback(category);

-- Add foreign key constraints
ALTER TABLE query_logs ADD CONSTRAINT fk_query_logs_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE api_usage ADD CONSTRAINT fk_api_usage_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE feedback ADD CONSTRAINT fk_feedback_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE feedback ADD CONSTRAINT fk_feedback_query_log_id 
    FOREIGN KEY (query_log_id) REFERENCES query_logs(id) ON DELETE CASCADE;

-- Create update timestamp triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_feedback_updated_at BEFORE UPDATE ON feedback
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
