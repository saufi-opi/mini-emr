#! /usr/bin/env bash

set -e

# Determine the backend directory (parent of the scripts directory)
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
BACKEND_DIR=$(dirname "$SCRIPT_DIR")

# Navigate to the backend directory so alembic can find alembic.ini
cd "$BACKEND_DIR"
export PYTHONPATH=.

# Alembic Helper Script
# Usage: ./scripts/alembic.sh <command> [args]

COMMAND=$1

case $COMMAND in
  makemigration)
    if [ -z "$2" ]; then
      echo "Error: Migration message is required. Usage: ./scripts/alembic.sh makemigration 'your message'"
      exit 1
    fi
    alembic revision --autogenerate -m "$2"
    ;;
  migrate)
    alembic upgrade head
    ;;
  rollback)
    # Default to -1 if no revision provided
    VERSION=${2:--1}
    alembic downgrade "$VERSION"
    ;;
  history)
    alembic history
    ;;
  current)
    alembic current
    ;;
  heads)
    alembic heads
    ;;
  help)
    echo "Portal Compliance - Alembic Helper"
    echo ""
    echo "Commands:"
    echo "  makemigration 'message'  - Create a new migration revision based on models"
    echo "  migrate                  - Apply all pending migrations (upgrade head)"
    echo "  rollback [rev]           - Rollback migrations (defaults to -1)"
    echo "  history                  - Show migration history"
    echo "  current                  - Show current migration revision"
    echo "  heads                    - Show latest available heads"
    echo ""
    echo "All other arguments will be passed directly to alembic."
    ;;
  *)
    if [ -z "$COMMAND" ]; then
      ./scripts/alembic.sh help
      exit 1
    fi
    # Pass-through to alembic for any other command
    alembic "$@"
    ;;
esac
