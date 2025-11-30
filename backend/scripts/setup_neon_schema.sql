-- =============================================================================
-- Neon Postgres Schema Setup for RAG Pipeline Query Endpoint
-- =============================================================================
-- This script creates the database schema for the RAG query endpoint feature.
-- It includes subscription management and query audit logging tables.
--
-- Requirements:
-- - Postgres 14+ (Neon supports Postgres 14+)
-- - Execute with appropriate permissions (CREATE TABLE, CREATE INDEX, etc.)
--
-- Usage:
--   psql $NEON_CONNECTION_STRING -f setup_neon_schema.sql
-- =============================================================================

-- =============================================================================
-- Table: subscriptions
-- =============================================================================
-- Stores user subscription information and chapter access permissions.
-- Used by FR-002 (Authorization - verify user has access to requested chapter).
--
-- Design decisions:
-- - user_id: UUID from Better-Auth authentication system
-- - subscription_tier: Enum for subscription levels (free, pro, enterprise)
-- - accessible_chapters: JSONB array of chapter IDs user can access
-- - GIN index on accessible_chapters for fast membership lookups (chapter access checks)
-- - expires_at: Nullable for non-expiring subscriptions (e.g., lifetime access)
-- =============================================================================

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    subscription_tier VARCHAR(50) NOT NULL CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
    accessible_chapters JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,

    CONSTRAINT valid_accessible_chapters CHECK (jsonb_typeof(accessible_chapters) = 'array')
);

-- Index for fast user_id lookups (primary access pattern: get subscription by user_id)
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);

-- GIN index for fast JSONB array membership checks (FR-002: verify chapter access)
-- Supports queries like: accessible_chapters @> '["chapter-123"]'::jsonb
CREATE INDEX IF NOT EXISTS idx_subscriptions_accessible_chapters
ON subscriptions USING GIN (accessible_chapters);

-- Partial index for active subscriptions (expires_at IS NULL OR expires_at > NOW())
-- Optimizes common query pattern: checking if user has active subscription
CREATE INDEX IF NOT EXISTS idx_subscriptions_active
ON subscriptions(user_id)
WHERE expires_at IS NULL OR expires_at > NOW();

-- =============================================================================
-- Table: query_audit_log
-- =============================================================================
-- Audit log for all RAG query requests.
-- Used by FR-016 (Privacy - log queries without storing query text).
--
-- Design decisions:
-- - Partitioned by month for efficient archival and query performance
-- - query_id: UUID for request tracing (correlates with application logs)
-- - user_id_hash: SHA-256 hash of user_id (privacy compliance - no PII)
-- - query_text: NOT INCLUDED per FR-016 privacy requirement
-- - grounding_status: Tracks quality of RAG responses (FULLY_GROUNDED, PARTIALLY_GROUNDED, SPECULATIVE)
-- - response_time_ms: p95 latency tracking (FR-015: 30-second timeout target)
-- - error_code: Standardized error codes from ErrorCode enum (nullable - NULL for success)
-- - Indexes optimized for common analytics queries (time-series, error rates, user activity)
-- =============================================================================

-- Drop existing table if recreating (be careful in production!)
-- DROP TABLE IF EXISTS query_audit_log CASCADE;

-- Create partitioned table (partitioned by month for efficient archival)
CREATE TABLE IF NOT EXISTS query_audit_log (
    id BIGSERIAL,
    query_id UUID NOT NULL,
    user_id_hash VARCHAR(64) NOT NULL,
    chapter_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    response_time_ms INTEGER NOT NULL CHECK (response_time_ms >= 0),
    grounding_status VARCHAR(50) NOT NULL CHECK (grounding_status IN ('FULLY_GROUNDED', 'PARTIALLY_GROUNDED', 'SPECULATIVE')),
    citation_count INTEGER NOT NULL DEFAULT 0 CHECK (citation_count >= 0),
    error_code VARCHAR(50),
    http_status_code INTEGER NOT NULL CHECK (http_status_code >= 100 AND http_status_code < 600),

    PRIMARY KEY (id, timestamp)  -- Composite primary key required for partitioning
) PARTITION BY RANGE (timestamp);

-- Create partitions for current and next 3 months
-- Note: In production, automate partition creation with a cron job or pg_partman
CREATE TABLE IF NOT EXISTS query_audit_log_2025_11 PARTITION OF query_audit_log
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE TABLE IF NOT EXISTS query_audit_log_2025_12 PARTITION OF query_audit_log
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

CREATE TABLE IF NOT EXISTS query_audit_log_2026_01 PARTITION OF query_audit_log
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE IF NOT EXISTS query_audit_log_2026_02 PARTITION OF query_audit_log
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- Index for query_id lookups (request tracing, debugging)
CREATE INDEX IF NOT EXISTS idx_query_audit_log_query_id
ON query_audit_log(query_id);

-- Index for user_id_hash analytics (user activity, rate limiting checks)
CREATE INDEX IF NOT EXISTS idx_query_audit_log_user_id_hash
ON query_audit_log(user_id_hash, timestamp DESC);

-- Index for chapter_id analytics (popular chapters, chapter-specific metrics)
CREATE INDEX IF NOT EXISTS idx_query_audit_log_chapter_id
ON query_audit_log(chapter_id, timestamp DESC);

-- Index for error rate analytics (WHERE error_code IS NOT NULL)
CREATE INDEX IF NOT EXISTS idx_query_audit_log_errors
ON query_audit_log(error_code, timestamp DESC)
WHERE error_code IS NOT NULL;

-- Index for grounding quality analytics
CREATE INDEX IF NOT EXISTS idx_query_audit_log_grounding_status
ON query_audit_log(grounding_status, timestamp DESC);

-- Index for latency p95 analytics (ORDER BY response_time_ms DESC LIMIT percentile)
CREATE INDEX IF NOT EXISTS idx_query_audit_log_response_time
ON query_audit_log(timestamp DESC, response_time_ms);

-- =============================================================================
-- Updated_at Trigger for subscriptions
-- =============================================================================
-- Automatically update updated_at timestamp when row is modified.
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Sample Data (Optional - for development/testing only)
-- =============================================================================
-- Uncomment to insert sample subscriptions and audit log entries.
-- DO NOT use in production!
-- =============================================================================

-- INSERT INTO subscriptions (user_id, subscription_tier, accessible_chapters, expires_at)
-- VALUES
--     ('00000000-0000-0000-0000-000000000001', 'free', '["chapter-01", "chapter-02"]'::jsonb, NULL),
--     ('00000000-0000-0000-0000-000000000002', 'pro', '["chapter-01", "chapter-02", "chapter-03", "chapter-04", "chapter-05"]'::jsonb, '2026-12-31 23:59:59+00'),
--     ('00000000-0000-0000-0000-000000000003', 'enterprise', '["chapter-01", "chapter-02", "chapter-03", "chapter-04", "chapter-05", "chapter-06", "chapter-07", "chapter-08", "chapter-09", "chapter-10"]'::jsonb, NULL)
-- ON CONFLICT (user_id) DO NOTHING;

-- INSERT INTO query_audit_log (query_id, user_id_hash, chapter_id, response_time_ms, grounding_status, citation_count, error_code, http_status_code, timestamp)
-- VALUES
--     (gen_random_uuid(), 'a1b2c3d4e5f6...', 'chapter-01', 2500, 'FULLY_GROUNDED', 5, NULL, 200, '2025-11-15 10:30:00+00'),
--     (gen_random_uuid(), 'a1b2c3d4e5f6...', 'chapter-02', 3200, 'PARTIALLY_GROUNDED', 3, NULL, 200, '2025-11-15 11:45:00+00'),
--     (gen_random_uuid(), 'x9y8z7w6v5u4...', 'chapter-03', 1800, 'FULLY_GROUNDED', 7, NULL, 200, '2025-11-15 14:20:00+00'),
--     (gen_random_uuid(), 'x9y8z7w6v5u4...', 'chapter-01', 5000, 'SPECULATIVE', 0, 'VECTOR_DB_TIMEOUT', 500, '2025-11-15 15:10:00+00');

-- =============================================================================
-- Verification Queries
-- =============================================================================
-- Run these queries to verify schema setup:
-- =============================================================================

-- Check tables exist
-- SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('subscriptions', 'query_audit_log');

-- Check indexes exist
-- SELECT indexname FROM pg_indexes WHERE schemaname = 'public' AND tablename IN ('subscriptions', 'query_audit_log');

-- Check partitions exist
-- SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename LIKE 'query_audit_log_%';

-- Check trigger exists
-- SELECT tgname FROM pg_trigger WHERE tgrelid = 'subscriptions'::regclass;

-- =============================================================================
-- Schema Setup Complete
-- =============================================================================
-- Tables created:
--   1. subscriptions - User subscription and chapter access management
--   2. query_audit_log - Privacy-compliant query audit trail (partitioned by month)
--
-- Next steps:
--   1. Grant appropriate permissions to application database user
--   2. Set up automated partition management (e.g., pg_partman, cron job)
--   3. Configure backup and archival policies for audit logs
--   4. Monitor query performance and adjust indexes as needed
-- =============================================================================
