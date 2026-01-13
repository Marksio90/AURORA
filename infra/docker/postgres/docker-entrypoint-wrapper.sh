#!/bin/bash
set -e

# This wrapper ensures our custom initialization runs after PostgreSQL starts
# It works for both fresh installations and existing databases

echo "Starting PostgreSQL with custom initialization wrapper..."

# Start the original docker entrypoint in the background
docker-entrypoint.sh postgres &
PG_PID=$!

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
until pg_isready -U "${POSTGRES_USER:-postgres}" -h localhost 2>/dev/null; do
  sleep 1
done

echo "PostgreSQL is running. Running custom initialization..."

# Run our custom initialization script
if [ -f /docker-entrypoint-initdb.d/init-db.sh ]; then
    bash /docker-entrypoint-initdb.d/init-db.sh
fi

echo "Custom initialization completed. PostgreSQL is ready."

# Wait for the PostgreSQL process
wait $PG_PID
