#!/bin/bash
set -e

# This script fixes PostgreSQL credentials when the database already exists
# Run this when you get "password authentication failed" errors

echo "==================================="
echo "PostgreSQL Credentials Fix Script"
echo "==================================="
echo ""

# Load environment variables from .env if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set defaults
POSTGRES_USER=${POSTGRES_USER:-decisioncalm}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-change_me_in_production}
POSTGRES_DB=${POSTGRES_DB:-decisioncalm}
CONTAINER_NAME=${CONTAINER_NAME:-decisioncalm-postgres}

echo "Configuration:"
echo "  Container: $CONTAINER_NAME"
echo "  User: $POSTGRES_USER"
echo "  Database: $POSTGRES_DB"
echo ""

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "ERROR: PostgreSQL container '$CONTAINER_NAME' is not running."
    echo "Please start it first with: docker compose up -d postgres"
    exit 1
fi

echo "Fixing PostgreSQL credentials..."
echo ""

# Execute SQL commands to fix the user and database
docker exec -i "$CONTAINER_NAME" psql -U postgres <<-EOSQL 2>/dev/null || docker exec -i "$CONTAINER_NAME" psql -U "$POSTGRES_USER" <<-EOSQL
    -- Ensure the user exists with the correct password
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${POSTGRES_USER}') THEN
            CREATE USER ${POSTGRES_USER} WITH SUPERUSER PASSWORD '${POSTGRES_PASSWORD}';
            RAISE NOTICE 'User ${POSTGRES_USER} created';
        ELSE
            ALTER USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';
            RAISE NOTICE 'Password updated for user ${POSTGRES_USER}';
        END IF;
    END
    \$\$;

    -- Ensure the database exists
    SELECT 'CREATE DATABASE ${POSTGRES_DB}'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB}')\gexec

    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};

    -- Enable required extensions
    \c ${POSTGRES_DB}
    CREATE EXTENSION IF NOT EXISTS vector;
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOSQL

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Credentials fixed successfully!"
    echo ""
    echo "You can now restart your services:"
    echo "  docker compose restart api"
    echo ""
else
    echo ""
    echo "✗ Failed to fix credentials."
    echo ""
    echo "If the issue persists, you may need to reset the database completely:"
    echo "  docker compose down -v"
    echo "  docker compose up -d"
    echo ""
    echo "WARNING: This will delete all data in the database!"
    echo ""
    exit 1
fi
