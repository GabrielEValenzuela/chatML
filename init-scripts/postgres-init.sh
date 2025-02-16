#!/bin/bash
set -e

echo "Creating PostgreSQL database and user..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE api_db;
    CREATE USER api_user WITH ENCRYPTED PASSWORD 'api_password';
    GRANT ALL PRIVILEGES ON DATABASE api_db TO api_user;
EOSQL

echo "Switching to api_db to create tables..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname="api_db" <<-EOSQL
    CREATE TABLE IF NOT EXISTS api_keys (
        api_key TEXT PRIMARY KEY,
        user_email TEXT,
        account_type TEXT
    );
EOSQL

echo "PostgreSQL initialization complete."
