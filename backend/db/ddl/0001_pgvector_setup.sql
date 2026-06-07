-- Enforce strict extension creation in the correct schema
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;

-- Verify installation
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        RAISE EXCEPTION 'CRITICAL: pgvector extension failed to initialize.';
    END IF;
END $$;
