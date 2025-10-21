# PowerShell development script for market_data_pipeline
# Usage: .\scripts\dev.ps1 <command>

param(
    [Parameter(Mandatory=$true)]
    [string]$Command
)

$PYTHON = "python"
$PIP = "$PYTHON -m pip"
$PYTEST = "pytest"

switch ($Command.ToLower()) {
    "help" {
        Write-Host "Common commands:"
        Write-Host "  .\scripts\dev.ps1 test              Run unit tests only"
        Write-Host "  .\scripts\dev.ps1 test-integration  Run integration tests (requires DB + AMDS client)"
        Write-Host "  .\scripts\dev.ps1 lint              Run ruff/flake8 linting"
        Write-Host "  .\scripts\dev.ps1 fmt               Auto-format with black"
        Write-Host "  .\scripts\dev.ps1 clean             Remove caches and build artifacts"
    }
    "test" {
        & $PYTEST tests/unit -q
    }
    "test-integration" {
        if (-not $env:DATABASE_URL) {
            Write-Host "DATABASE_URL not set; integration tests will fail." -ForegroundColor Yellow
        }
        & $PYTEST tests/integration -q
    }
    "lint" {
        try {
            & ruff check src tests
        } catch {
            Write-Host "ruff not installed" -ForegroundColor Yellow
        }
    }
    "fmt" {
        try {
            & black src tests
        } catch {
            Write-Host "black not installed" -ForegroundColor Yellow
        }
    }
    "clean" {
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue .pytest_cache, __pycache__, build, dist, *.egg-info
        Write-Host "Cleaned caches and build artifacts"
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Run '.\scripts\dev.ps1 help' for available commands"
    }
}
