#!/bin/sh

set -e

echo "Waiting for PostgreSQL..."

until python -c "
import os
import psycopg2

url = os.environ['DATABASE_URL']
conn = psycopg2.connect(url)
conn.close()
"; do
    sleep 1
done

echo "PostgreSQL is ready."

echo "Running database migrations..."

alembic upgrade head

echo "Creating initial admin..."

python -m app.scripts.create_admin

echo "Starting API..."

exec uvicorn app.main:app --host 0.0.0.0 --port 8000