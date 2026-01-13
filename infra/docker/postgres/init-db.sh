#!/bin/bash
set -e

# This script runs during PostgreSQL initialization (first time only)
# It ensures the database is properly configured with required extensions
# Note: This only runs when the database is first created

echo "==================================="
echo "PostgreSQL Initialization Script"
echo "==================================="
echo ""
echo "Database: ${POSTGRES_DB:-decisioncalm}"
echo "User: ${POSTGRES_USER:-decisioncalm}"
echo ""

# The POSTGRES_USER and POSTGRES_DB are automatically created by the base image
# This script runs as that user, so we just need to ensure extensions are enabled

# Enable required extensions in the database
echo "Enabling required extensions..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable pgvector extension
    CREATE EXTENSION IF NOT EXISTS vector;

    -- Create extension for UUID generation
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- Log success
    DO \$\$
    BEGIN
        RAISE NOTICE 'Extensions enabled successfully';
        RAISE NOTICE 'Database is ready for use';
    END \$\$;
EOSQL

echo ""
echo "✓ Database initialization completed successfully!"
echo "==================================="
