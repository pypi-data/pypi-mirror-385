#!/usr/bin/env bash
# Bash script to activate the virtual environment
# Usage: source ./scripts/activate.sh

echo "Activating virtual environment..."

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated!"
    echo "📦 Project installed in development mode"
    echo "🔧 Development tools available: black, ruff, mypy, pytest"
else
    echo "❌ Virtual environment not found. Run 'python -m venv .venv' first."
    exit 1
fi
