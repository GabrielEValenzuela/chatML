#!/bin/bash
set -e

echo "Creating PostgreSQL database and user..."

# Create database and user with privileges
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE api_db;
    CREATE USER api_user WITH ENCRYPTED PASSWORD 'api_password';
    GRANT ALL PRIVILEGES ON DATABASE api_db TO api_user;
EOSQL

echo "Switching to api_db to create tables..."

# Connect to the database as the superuser and create the table
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname="api_db" <<-EOSQL
    CREATE TABLE IF NOT EXISTS api_keys (
        api_key TEXT PRIMARY KEY,
        user_email TEXT,
        account_type TEXT
    );

    -- Ensure api_user has full privileges on the table
    GRANT ALL PRIVILEGES ON TABLE api_keys TO api_user;
EOSQL

echo "PostgreSQL initialization complete."
