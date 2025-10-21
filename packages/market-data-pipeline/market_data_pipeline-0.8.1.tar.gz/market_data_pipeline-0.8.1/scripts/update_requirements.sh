#!/usr/bin/env bash
# Script to regenerate requirements.txt from pyproject.toml

set -euo pipefail

echo "Updating requirements.txt from pyproject.toml..."

# Check if pip-tools is installed
if ! command -v pip-compile &> /dev/null; then
    echo "Installing pip-tools..."
    pip install pip-tools
fi

# Compile requirements.txt
pip-compile pyproject.toml --output-file=requirements.txt

echo "✅ requirements.txt updated successfully"
echo "📦 Dependencies pinned to specific versions for deterministic builds"
echo "🔄 Remember to commit requirements.txt to version control"
