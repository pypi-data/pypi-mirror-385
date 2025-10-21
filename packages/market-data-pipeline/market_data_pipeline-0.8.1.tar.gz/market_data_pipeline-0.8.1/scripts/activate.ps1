# PowerShell script to activate the virtual environment
# Usage: .\scripts\activate.ps1

Write-Host "Activating virtual environment..." -ForegroundColor Green

if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    .\.venv\Scripts\Activate.ps1
    Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
    Write-Host "📦 Project installed in development mode" -ForegroundColor Cyan
    Write-Host "🔧 Development tools available: black, ruff, mypy, pytest" -ForegroundColor Yellow
} else {
    Write-Host "❌ Virtual environment not found. Run 'python -m venv .venv' first." -ForegroundColor Red
    exit 1
}
