# PowerShell script to regenerate requirements.txt from pyproject.toml

Write-Host "Updating requirements.txt from pyproject.toml..." -ForegroundColor Green

# Check if pip-tools is available
try {
    python -m piptools --help | Out-Null
} catch {
    Write-Host "Installing pip-tools..." -ForegroundColor Yellow
    pip install pip-tools
}

# Compile requirements.txt
python -m piptools compile pyproject.toml --output-file=requirements.txt

Write-Host "✅ requirements.txt updated successfully" -ForegroundColor Green
Write-Host "📦 Dependencies pinned to specific versions for deterministic builds" -ForegroundColor Cyan
Write-Host "🔄 Remember to commit requirements.txt to version control" -ForegroundColor Yellow
