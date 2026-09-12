#!/bin/sh
set -e

if [ "$SEED_ON_START" = "true" ]; then
  echo "Seeding synthetic data (if the database is empty)..."
  python -m seed.generate_synthetic_data || true
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
