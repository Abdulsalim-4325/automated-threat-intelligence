#!/bin/bash
set -e

echo "[Entrypoint] Running database migrations..."
alembic upgrade head

echo "[Entrypoint] Starting the application..."
exec "$@"