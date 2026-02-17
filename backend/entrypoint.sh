#!/bin/sh

# DB接続が可能になるまで待機するループ
echo "Waiting for database connection..."
until python -c "import os, psycopg2; psycopg2.connect(os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://', 1))" 2>/dev/null; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is up - running migrations"
alembic upgrade head

echo "Starting application"
uvicorn app.main:app --host 0.0.0.0 --port 8000
