#!/usr/bin/env pwsh
# PowerShell version of smoke test for Windows compatibility

$API = "http://localhost:8083"

Write-Host "==> Health check" -ForegroundColor Green
try {
    $health = Invoke-RestMethod -Uri "$API/health" -Method Get
    $health | ConvertTo-Json
} catch {
    Write-Error "Health check failed: $_"
    exit 1
}

Write-Host "==> Create pipeline" -ForegroundColor Green
$body = @{
    tenant_id = "T1"
    pipeline_id = "smoke1"
    source_type = "synthetic"
    symbols = @("NVDA", "SPY")
    rate = 20
    duration = 5
    operator_type = "bars"
    sink_type = "store"
} | ConvertTo-Json

try {
    $resp = Invoke-RestMethod -Uri "$API/pipelines" -Method Post -Body $body -ContentType "application/json"
    $resp | ConvertTo-Json
    $key = $resp.pipeline_key
} catch {
    Write-Error "Pipeline creation failed: $_"
    exit 1
}

Write-Host "==> List pipelines" -ForegroundColor Green
try {
    $pipelines = Invoke-RestMethod -Uri "$API/pipelines" -Method Get
    $pipelines | ConvertTo-Json
} catch {
    Write-Error "List pipelines failed: $_"
}

Write-Host "==> Get pipeline status" -ForegroundColor Green
try {
    $status = Invoke-RestMethod -Uri "$API/pipelines/$key" -Method Get
    $status | ConvertTo-Json
} catch {
    Write-Error "Get pipeline status failed: $_"
}

Write-Host "==> Wait 6s for pipeline to complete" -ForegroundColor Green
Start-Sleep -Seconds 6

Write-Host "==> Get pipeline status again (should be gone or completed)" -ForegroundColor Green
try {
    $status2 = Invoke-RestMethod -Uri "$API/pipelines/$key" -Method Get
    $status2 | ConvertTo-Json
} catch {
    Write-Host "Pipeline not found (as expected)" -ForegroundColor Yellow
}

Write-Host "==> Delete pipeline (cleanup, should be no-op if already completed)" -ForegroundColor Green
try {
    Invoke-RestMethod -Uri "$API/pipelines/$key" -Method Delete
} catch {
    Write-Host "Delete failed (expected if pipeline already completed)" -ForegroundColor Yellow
}

Write-Host "Smoke test completed." -ForegroundColor Green
