# PostgreSQL Troubleshooting Guide

## Common Issue: Password Authentication Failed

### Problem

You see an error like:
```
postgres | FATAL: password authentication failed for user "decisioncalm"
api | asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "decisioncalm"
```

### Why This Happens

PostgreSQL initialization scripts only run **once** when the database is first created. If you have an existing database volume from a previous run, PostgreSQL skips initialization and uses the existing database with its original credentials.

This causes authentication failures when:
1. You change environment variables after the first run
2. You don't have a `.env` file and rely on different default values
3. The database was created with different credentials than currently configured

### Solutions

#### Solution 1: Fix Credentials in Existing Database (Recommended)

Use the provided fix script to update credentials without losing data:

```bash
# Make sure the .env file exists with your desired credentials
cp .env.example .env
# Edit .env and set your POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

# Start only the PostgreSQL container
docker compose up -d postgres

# Run the fix script
bash scripts/fix-postgres-credentials.sh

# Restart all services
docker compose restart
```

#### Solution 2: Reset Database (Deletes All Data)

If you don't need to preserve data, you can completely reset:

```bash
# Stop all containers and remove volumes
docker compose down -v

# Start fresh
docker compose --profile dev up --build
```

**WARNING:** This will delete all data in your database!

#### Solution 3: Manual Fix

If the script doesn't work, you can manually fix it:

```bash
# Connect to the running PostgreSQL container
docker exec -it decisioncalm-postgres psql -U postgres

# Or if 'postgres' user doesn't exist:
docker exec -it decisioncalm-postgres psql -U decisioncalm
```

Then run these SQL commands:

```sql
-- Update the password
ALTER USER decisioncalm WITH PASSWORD 'your_password_here';

-- Ensure database exists
CREATE DATABASE decisioncalm;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE decisioncalm TO decisioncalm;

-- Enable extensions
\c decisioncalm
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### Prevention

To avoid this issue in the future:

1. **Always use a `.env` file**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Keep credentials consistent**
   Once you've created the database, don't change the credentials without using one of the solutions above.

3. **Document your setup**
   Keep track of the credentials you used for initialization.

## Other Common Issues

### Issue: Database Not Ready

If the API fails because the database isn't ready yet:

```bash
# Check PostgreSQL container logs
docker logs decisioncalm-postgres

# Check if PostgreSQL is responding
docker exec decisioncalm-postgres pg_isready -U decisioncalm
```

### Issue: Extensions Not Installed

If you get errors about missing `vector` or `uuid-ossp` extensions:

```bash
# Connect to the database
docker exec -it decisioncalm-postgres psql -U decisioncalm -d decisioncalm

# Install extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### Issue: Port Already in Use

If port 5432 is already in use:

```bash
# Check what's using the port
lsof -i :5432  # On macOS/Linux
netstat -ano | findstr :5432  # On Windows

# Either stop the other PostgreSQL instance or change the port in docker-compose.yml:
ports:
  - "5433:5432"  # Use 5433 on host, 5432 in container
```

## Useful Commands

```bash
# View PostgreSQL logs
docker logs decisioncalm-postgres -f

# Check PostgreSQL status
docker exec decisioncalm-postgres pg_isready -U decisioncalm

# Connect to PostgreSQL CLI
docker exec -it decisioncalm-postgres psql -U decisioncalm -d decisioncalm

# List databases
docker exec decisioncalm-postgres psql -U decisioncalm -c "\l"

# List users
docker exec decisioncalm-postgres psql -U decisioncalm -c "\du"

# Restart just PostgreSQL
docker compose restart postgres

# View all running containers
docker compose ps

# Clean up everything (WARNING: deletes data!)
docker compose down -v
```

## Getting Help

If you're still experiencing issues:

1. Check the logs: `docker compose logs postgres api`
2. Verify your `.env` file exists and has correct values
3. Ensure Docker has enough resources (memory, disk space)
4. Try the "Reset Database" solution if data loss is acceptable
