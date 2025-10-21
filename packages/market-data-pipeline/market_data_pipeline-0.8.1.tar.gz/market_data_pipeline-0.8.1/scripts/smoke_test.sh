#!/usr/bin/env bash
set -euo pipefail

API="http://localhost:8083"

echo "==> Health check"
curl -s "$API/health" | jq .

echo "==> Create pipeline"
resp=$(curl -s -X POST "$API/pipelines" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "T1",
    "pipeline_id": "smoke1",
    "source_type": "synthetic",
    "symbols": ["NVDA","SPY"],
    "rate": 20,
    "duration": 5,
    "operator_type": "bars",
    "sink_type": "store"
  }')
echo "$resp" | jq .

key=$(echo "$resp" | jq -r .pipeline_key)

echo "==> List pipelines"
curl -s "$API/pipelines" | jq .

echo "==> Get pipeline status"
curl -s "$API/pipelines/$key" | jq .

echo "==> Wait 6s for pipeline to complete"
sleep 6

echo "==> Get pipeline status again (should be gone or completed)"
curl -s "$API/pipelines/$key" || echo "Pipeline not found (as expected)"

echo "==> Delete pipeline (cleanup, should be no-op if already completed)"
curl -s -X DELETE "$API/pipelines/$key" || true

echo "Smoke test completed."
