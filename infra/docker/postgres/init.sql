-- Initialize PostgreSQL with pgvector extension
-- This script runs on first container creation

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Log success
DO $$
BEGIN
  RAISE NOTICE 'pgvector extension enabled successfully';
END $$;
