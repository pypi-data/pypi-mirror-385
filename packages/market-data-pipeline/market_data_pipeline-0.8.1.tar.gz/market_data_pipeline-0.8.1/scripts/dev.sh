#!/usr/bin/env bash
# Bash development script for market_data_pipeline
# Usage: ./scripts/dev.sh <command>

PYTHON=${PYTHON:-python}
PIP="$PYTHON -m pip"
PYTEST=${PYTEST:-pytest}

case "${1:-help}" in
    help)
        echo "Common commands:"
        echo "  ./scripts/dev.sh test              Run unit tests only"
        echo "  ./scripts/dev.sh test-integration  Run integration tests (requires DB + AMDS client)"
        echo "  ./scripts/dev.sh lint              Run ruff/flake8 linting"
        echo "  ./scripts/dev.sh fmt               Auto-format with black"
        echo "  ./scripts/dev.sh clean             Remove caches and build artifacts"
        ;;
    test)
        $PYTEST tests/unit -q
        ;;
    test-integration)
        if [ -z "$DATABASE_URL" ]; then
            echo "DATABASE_URL not set; integration tests will fail."
        fi
        $PYTEST tests/integration -q
        ;;
    lint)
        if command -v ruff >/dev/null 2>&1; then
            ruff check src tests
        else
            echo "ruff not installed"
        fi
        ;;
    fmt)
        if command -v black >/dev/null 2>&1; then
            black src tests
        else
            echo "black not installed"
        fi
        ;;
    clean)
        rm -rf .pytest_cache __pycache__ build dist *.egg-info
        echo "Cleaned caches and build artifacts"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Run './scripts/dev.sh help' for available commands"
        exit 1
        ;;
esac
