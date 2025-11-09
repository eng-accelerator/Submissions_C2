-- database/schema.sql
-- PostgreSQL Schema for AI Financial Coach
-- For production deployment with PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    country VARCHAR(50) DEFAULT 'India',
    currency VARCHAR(3) DEFAULT 'INR',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Core transaction data
    transaction_date DATE NOT NULL,
    value_date DATE,
    amount DECIMAL(15, 2) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('debit', 'credit')),
    balance DECIMAL(15, 2),
    
    -- Description and categorization
    description TEXT,
    party_name VARCHAR(255),
    category VARCHAR(50),
    subcategory VARCHAR(50),
    mode VARCHAR(30),
    
    -- Reference information
    reference_number VARCHAR(100),
    cheque_number VARCHAR(50),
    
    -- Metadata
    is_recurring BOOLEAN DEFAULT FALSE,
    tags TEXT[],
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Monthly summary table (aggregated data for fast queries)
CREATE TABLE IF NOT EXISTS monthly_summary (
    summary_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    
    total_income DECIMAL(15, 2) DEFAULT 0,
    total_expenses DECIMAL(15, 2) DEFAULT 0,
    net_savings DECIMAL(15, 2) DEFAULT 0,
    savings_rate DECIMAL(5, 2) DEFAULT 0,
    
    -- JSON fields for category breakdown
    category_breakdown JSONB,
    mode_breakdown JSONB,
    
    transaction_count INTEGER DEFAULT 0,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, year, month)
);

-- Category patterns table (for auto-categorization)
CREATE TABLE IF NOT EXISTS category_patterns (
    pattern_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    keywords TEXT[] NOT NULL,
    regex_pattern TEXT,
    priority INTEGER DEFAULT 0,
    region VARCHAR(50) DEFAULT 'global',
    is_system BOOLEAN DEFAULT TRUE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User corrections table (learning from feedback)
CREATE TABLE IF NOT EXISTS user_corrections (
    correction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    transaction_id UUID REFERENCES transactions(transaction_id),
    
    original_category VARCHAR(50),
    corrected_category VARCHAR(50) NOT NULL,
    description_pattern TEXT,
    apply_to_similar BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_transactions_user_date 
    ON transactions(user_id, transaction_date DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_user_type 
    ON transactions(user_id, transaction_type);

CREATE INDEX IF NOT EXISTS idx_transactions_user_category 
    ON transactions(user_id, category);

CREATE INDEX IF NOT EXISTS idx_transactions_date_range 
    ON transactions(transaction_date);

CREATE INDEX IF NOT EXISTS idx_monthly_summary_user 
    ON monthly_summary(user_id, year DESC, month DESC);

CREATE INDEX IF NOT EXISTS idx_category_patterns_keywords 
    USING GIN(keywords);

-- Insert default category patterns
INSERT INTO category_patterns (category, keywords, priority, is_system) VALUES
('cash_withdrawal', ARRAY['atm', 'cash', 'withdrawal', 'atm-wdl'], 10, TRUE),
('food_dining', ARRAY['swiggy', 'zomato', 'restaurant', 'cafe', 'food'], 10, TRUE),
('transport', ARRAY['uber', 'ola', 'rapido', 'petrol', 'fuel'], 10, TRUE),
('shopping', ARRAY['amazon', 'flipkart', 'shop', 'mall'], 10, TRUE),
('utilities', ARRAY['electricity', 'water', 'gas', 'internet', 'mobile'], 10, TRUE),
('entertainment', ARRAY['netflix', 'spotify', 'movie', 'prime'], 10, TRUE),
('healthcare', ARRAY['hospital', 'pharmacy', 'doctor', 'medical'], 10, TRUE),
('investment', ARRAY['mutual fund', 'sip', 'stock', 'investment'], 10, TRUE),
('insurance', ARRAY['insurance', 'premium', 'policy'], 10, TRUE),
('emi', ARRAY['emi', 'loan', 'installment'], 10, TRUE),
('transfer', ARRAY['upi', 'neft', 'imps', 'transfer'], 5, TRUE),
('salary', ARRAY['salary', 'sal credit', 'income'], 10, TRUE)
ON CONFLICT DO NOTHING;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE users IS 'User accounts and profiles';
COMMENT ON TABLE transactions IS 'All financial transactions';
COMMENT ON TABLE monthly_summary IS 'Pre-aggregated monthly statistics for dashboard';
COMMENT ON TABLE category_patterns IS 'Patterns for auto-categorizing transactions';
COMMENT ON TABLE user_corrections IS 'User feedback for improving categorization';
