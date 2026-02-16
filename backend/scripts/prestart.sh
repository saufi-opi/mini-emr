#! /usr/bin/env bash

set -e

# Determine the backend directory (parent of the scripts directory)
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
BACKEND_DIR=$(dirname "$SCRIPT_DIR")

# Navigate to the backend directory so alembic can find alembic.ini
cd "$BACKEND_DIR"
export PYTHONPATH=.

# Run migrations
echo "Running migrations..."
alembic upgrade head

# Seed initial data (Admin/Doctor)
echo "Seeding initial user data..."
python -m app.core.seed

# Seed ICD-10 data
echo "Seeding ICD-10 diagnoses..."
python scripts/seed_icd10.py

echo "Pre-start script finished successfully!"
