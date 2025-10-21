# Phase 6.0B — KEDA Autoscaling (Pipeline)

**Status**: ✅ COMPLETE  
**Date**: October 16, 2025

---

## 🎯 Overview

Phase 6.0B implements Kubernetes Event-driven Autoscaling (KEDA) for the market data pipeline, enabling automatic horizontal scaling based on downstream backpressure metrics from the store.

Combined with Phase 6.0A (Backpressure Feedback Loop), this creates a fully adaptive system that:
- Scales pipeline pods up when store queue is full
- Scales down when backpressure eases
- Optimizes resource usage and cost

---

## 📊 Metrics (Pipeline)

### New Gauges (Phase 6.0B)

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `pipeline_rate_scale_factor` | Gauge | `provider` | Current rate scale factor (0.0-1.0) |
| `pipeline_backpressure_state` | Gauge | `provider` | Backpressure state (0=ok, 1=soft, 2=hard) |
| `pipeline_feedback_queue_depth` | Gauge | `source` | Queue depth echoed from store |

### Integration

Metrics are emitted by:
1. **RateCoordinator** → `pipeline_rate_scale_factor`, `pipeline_backpressure_state`
2. **FeedbackHandler** → `pipeline_feedback_queue_depth`

---

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│  WriteCoordinator (store)       │
│  - Queue fills up               │
│  - Publishes FeedbackEvent      │
└────────────┬────────────────────┘
             │ FeedbackEvent(queue_size=N, level=SOFT)
             v
    ┌────────────────────────┐
    │  FeedbackHandler       │ (pipeline)
    │  - Emit metric ────────┼───→ pipeline_feedback_queue_depth
    │  - Adjust rate         │
    └────────────────────────┘

    ┌────────────────────────┐
    │  RateCoordinator       │
    │  - Emit metrics ───────┼───→ pipeline_rate_scale_factor
    └────────────────────────┘      pipeline_backpressure_state

    ┌────────────────────────┐
    │  FastAPI App           │
    │  GET /metrics ─────────┼───→ Prometheus (scrapes)
    └────────────────────────┘

    ┌────────────────────────┐
    │  KEDA ScaledObject     │
    │  Query:                │
    │  max(pipeline_feedback_│
    │      queue_depth)      │
    │  > threshold           │
    │  ───────────────────────┼───→ Scale Deployment
    └────────────────────────┘
```

---

## 🚀 Endpoint

### `/metrics` (FastAPI)

**Location**: `src/market_data_pipeline/runners/api.py`

**Returns**: Prometheus text format with all registered metrics

**Example**:
```bash
curl http://localhost:8000/metrics
```

**Output** (excerpt):
```
# HELP pipeline_rate_scale_factor Current rate scale factor applied to provider (0.0..1.0).
# TYPE pipeline_rate_scale_factor gauge
pipeline_rate_scale_factor{provider="ibkr"} 0.5

# HELP pipeline_backpressure_state Backpressure state: 0=ok, 1=soft, 2=hard.
# TYPE pipeline_backpressure_state gauge
pipeline_backpressure_state{provider="ibkr"} 1.0

# HELP pipeline_feedback_queue_depth Queue depth reported by feedback source (echo of store).
# TYPE pipeline_feedback_queue_depth gauge
pipeline_feedback_queue_depth{source="store_coordinator"} 5234.0
```

### Standalone Server (Optional)

If FastAPI is disabled, start a standalone Prometheus server:

```yaml
# config.yaml
metrics:
  enable: true
  standalone_port: 9090
```

Or via environment variable:
```bash
export MDP_METRICS_ENABLE=true
export MDP_METRICS_STANDALONE_PORT=9090
```

---

## ⚙️ Configuration

### Python API

```python
from market_data_pipeline.runtime import UnifiedRuntime
from market_data_pipeline.settings import UnifiedRuntimeSettings

settings = UnifiedRuntimeSettings(
    mode="dag",
    dag={
        "graph": {...}
    },
    feedback={
        "enable_feedback": True,
        "provider_name": "ibkr"
    },
    metrics={
        "enable": True,
        "standalone_port": None  # Use FastAPI /metrics
    }
)

async with UnifiedRuntime(settings) as rt:
    await rt.run("my-job")
```

### YAML Config

```yaml
mode: dag
dag:
  graph:
    nodes: [...]
    edges: [...]
feedback:
  enable_feedback: true
  provider_name: ibkr
metrics:
  enable: true
  standalone_port: null  # or 9090 for standalone
```

### Environment Variables

```bash
# Metrics
export MDP_METRICS_ENABLE=true
export MDP_METRICS_STANDALONE_PORT=9090

# Feedback (Phase 6.0A)
export MDP_FB_ENABLE_FEEDBACK=true
export MDP_FB_PROVIDER_NAME=ibkr
```

---

## 📐 KEDA Scaling

### ScaledObject Configuration

**File**: `deploy/keda/scaledobject-pipeline.yaml`

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: mdp-pipeline-scaler
spec:
  scaleTargetRef:
    name: mdp-pipeline
  minReplicaCount: 1
  maxReplicaCount: 10
  cooldownPeriod: 60
  pollingInterval: 15
  triggers:
    # Trigger 1: Queue depth
    - type: prometheus
      metadata:
        metricName: pipeline_feedback_queue_depth
        threshold: "5000"
        query: max(pipeline_feedback_queue_depth{source="store_coordinator"})
    
    # Trigger 2: Hard backpressure
    - type: prometheus
      metadata:
        metricName: pipeline_backpressure_hard
        threshold: "0.5"
        query: max(pipeline_backpressure_state) == 2
```

### Threshold Tuning

**Formula**:
```
threshold = store_capacity × target_utilization
```

**Examples**:
- **High Throughput**: `threshold: 8000` (80% of 10k capacity)
- **Balanced** (default): `threshold: 5000` (50%)
- **Low Latency**: `threshold: 2000` (20%)

**Adjusting**:
```bash
kubectl edit scaledobject mdp-pipeline-scaler -n market-data
# Or
kubectl apply -f deploy/keda/scaledobject-pipeline.yaml
```

---

## 🧪 Testing

### Unit Tests

**Location**: `tests/unit/metrics/test_pipeline_metrics.py`

```bash
pytest tests/unit/metrics/ -v
```

**Coverage**:
- ✅ Metrics accept labels and values
- ✅ Graceful degradation if Prometheus unavailable
- ✅ Multiple providers handled independently

### Integration Tests

**Manual** (requires K8s + KEDA):
```bash
# Deploy pipeline + KEDA
kubectl apply -n market-data -f deploy/keda/

# Simulate load
# ... trigger feedback events with high queue depth ...

# Watch scaling
kubectl -n market-data get hpa -w
kubectl -n market-data get pods -w
```

---

## 📈 Expected Behavior

### Scenario 1: Normal Operation

```
Store Queue: 1000 / 10000 (10%)
→ pipeline_feedback_queue_depth = 1000
→ pipeline_backpressure_state = 0 (ok)
→ pipeline_rate_scale_factor = 1.0

KEDA: No scaling (below threshold)
Pods: 1 (minReplica)
```

### Scenario 2: High Load

```
Store Queue: 6000 / 10000 (60%)
→ pipeline_feedback_queue_depth = 6000
→ pipeline_backpressure_state = 1 (soft)
→ pipeline_rate_scale_factor = 0.5

KEDA: Scale up (above threshold 5000)
Pods: 1 → 3
```

### Scenario 3: Overload

```
Store Queue: 9500 / 10000 (95%)
→ pipeline_feedback_queue_depth = 9500
→ pipeline_backpressure_state = 2 (hard)
→ pipeline_rate_scale_factor = 0.0

KEDA: Aggressive scale up (both triggers)
Pods: 3 → 8
Pipeline: Paused (rate = 0)
```

### Scenario 4: Recovery

```
Store Queue: 500 / 10000 (5%)
→ pipeline_feedback_queue_depth = 500
→ pipeline_backpressure_state = 0 (ok)
→ pipeline_rate_scale_factor = 1.0

KEDA: Scale down (below threshold, after cooldown)
Pods: 8 → 1
Pipeline: Full rate restored
```

---

## 🔧 Troubleshooting

### Metrics Not Appearing

**Check**:
```bash
curl http://localhost:8000/metrics | grep pipeline_
```

**Fix**:
- Ensure `MDP_METRICS_ENABLE=true`
- Check FastAPI is running
- Verify Prometheus scraping (check ServiceMonitor)

### KEDA Not Scaling

**Check**:
```bash
kubectl -n market-data describe scaledobject mdp-pipeline-scaler
kubectl -n keda logs -l app=keda-operator --tail=50
```

**Common Issues**:
- Prometheus unreachable from KEDA pods
- Metric query returns no data (check labels)
- `serverAddress` incorrect

### Rapid Oscillation

**Symptoms**: Pods scale up/down rapidly

**Fix**: Increase `cooldownPeriod` and `pollingInterval`:
```yaml
cooldownPeriod: 120  # from 60
pollingInterval: 30  # from 15
```

---

## 📚 Grafana Dashboards

### Recommended Panels

1. **Queue Depth** (Time Series)
   ```promql
   pipeline_feedback_queue_depth{source="store_coordinator"}
   ```

2. **Backpressure State** (Gauge)
   ```promql
   pipeline_backpressure_state{provider="ibkr"}
   ```

3. **Rate Scale** (Gauge)
   ```promql
   pipeline_rate_scale_factor{provider="ibkr"}
   ```

4. **Pod Count** (Stat)
   ```promql
   count(kube_pod_info{namespace="market-data", pod=~"mdp-pipeline-.*"})
   ```

5. **HPA Target vs Current** (Time Series)
   ```promql
   kube_horizontalpodautoscaler_status_desired_replicas{horizontalpodautoscaler="keda-hpa-mdp-pipeline-scaler"}
   kube_horizontalpodautoscaler_status_current_replicas{horizontalpodautoscaler="keda-hpa-mdp-pipeline-scaler"}
   ```

---

## 🎯 Key Takeaways

1. **Automatic**: No manual intervention required for scaling
2. **Adaptive**: Responds to actual downstream pressure, not arbitrary metrics
3. **Cost-Efficient**: Scales down during low load
4. **Observable**: All decisions visible in Prometheus/Grafana
5. **Tunable**: Thresholds can be adjusted based on workload profile

---

## 📖 References

- [Phase 6.0A: Backpressure Feedback Loop](../PHASE_6.0A_IMPLEMENTATION_COMPLETE.md)
- [KEDA Documentation](https://keda.sh/docs/)
- [Prometheus Scaler](https://keda.sh/docs/2.12/scalers/prometheus/)
- [Deployment Manifests](../deploy/keda/README.md)

---

**Phase 6.0B Status**: ✅ COMPLETE and PRODUCTION-READY

