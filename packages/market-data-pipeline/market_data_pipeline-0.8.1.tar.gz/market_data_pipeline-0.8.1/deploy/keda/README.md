# KEDA Autoscaling for `market_data_pipeline`

This directory contains Kubernetes manifests for deploying and autoscaling the market data pipeline using KEDA (Kubernetes Event-driven Autoscaling).

## 📋 Prerequisites

- **Kubernetes cluster** (v1.19+)
- **KEDA v2+** installed ([installation guide](https://keda.sh/docs/2.12/deploy/))
- **Prometheus** (for metrics scraping)
- **Prometheus Operator** (optional, for ServiceMonitor)

## 📦 Files

| File | Description |
|------|-------------|
| `deployment-pipeline.yaml` | Pipeline Deployment with health checks and resource limits |
| `scaledobject-pipeline.yaml` | KEDA ScaledObject with Prometheus triggers |
| `prometheus-servicemonitor.yaml` | Service + ServiceMonitor for Prometheus scraping |

## 🚀 Quick Start

### 1. Deploy the Pipeline

```bash
# Create namespace
kubectl create namespace market-data

# Deploy pipeline
kubectl apply -n market-data -f deployment-pipeline.yaml

# Deploy service for metrics scraping
kubectl apply -n market-data -f prometheus-servicemonitor.yaml

# Verify deployment
kubectl -n market-data get deploy mdp-pipeline
kubectl -n market-data get pods -l app=mdp-pipeline
```

### 2. Deploy KEDA Scaler

```bash
# Apply ScaledObject
kubectl apply -n market-data -f scaledobject-pipeline.yaml

# Verify ScaledObject
kubectl -n market-data get scaledobject mdp-pipeline-scaler -o yaml
kubectl -n market-data describe scaledobject mdp-pipeline-scaler
```

### 3. Verify Scaling

```bash
# Watch HPA (created by KEDA)
kubectl -n market-data get hpa -w

# Watch pod count
kubectl -n market-data get pods -l app=mdp-pipeline -w

# Check KEDA logs
kubectl -n keda logs -l app=keda-operator -f
```

## ⚙️ Threshold Tuning

The default `threshold: 5000` assumes:
- Store queue capacity: 10,000 items
- Target utilization: 50%
- Safety margin: Conservative

### Formula

```
threshold = store_capacity × target_utilization
```

### Example Scenarios

| Scenario | Store Capacity | Target Util | Threshold | Notes |
|----------|----------------|-------------|-----------|-------|
| **High Throughput** | 10,000 | 80% | 8,000 | Aggressive scaling |
| **Balanced** | 10,000 | 50% | 5,000 | **Default** |
| **Low Latency** | 10,000 | 20% | 2,000 | Conservative, fast response |
| **Large Store** | 50,000 | 60% | 30,000 | High-capacity deployment |

### Adjusting Thresholds

Edit `scaledobject-pipeline.yaml`:

```yaml
triggers:
  - type: prometheus
    metadata:
      threshold: "8000"  # ← Change here
```

Then reapply:

```bash
kubectl apply -n market-data -f scaledobject-pipeline.yaml
```

## 📊 Monitoring

### Prometheus Queries

```promql
# Queue depth (primary scaling metric)
max(pipeline_feedback_queue_depth{source="store_coordinator"})

# Backpressure state (0=ok, 1=soft, 2=hard)
max(pipeline_backpressure_state)

# Rate scale factor (0.0-1.0)
pipeline_rate_scale_factor{provider="ibkr"}

# Pod count
count(kube_pod_info{namespace="market-data", pod=~"mdp-pipeline-.*"})
```

### Grafana Dashboard

Add panels for:
1. **Queue Depth** (line chart)
2. **Backpressure State** (gauge, 0-2)
3. **Rate Scale** (gauge, 0-1.0)
4. **Pod Count** (stat panel)
5. **HPA Target vs Current** (dual-axis)

## 🔧 Troubleshooting

### KEDA not scaling

**Symptoms**: Metrics show high queue depth but pod count stays at minReplica

**Check**:
```bash
# Verify ScaledObject status
kubectl -n market-data describe scaledobject mdp-pipeline-scaler

# Check KEDA operator logs
kubectl -n keda logs -l app=keda-operator --tail=100

# Verify Prometheus query
kubectl -n market-data port-forward svc/prometheus 9090:9090
# Then query: max(pipeline_feedback_queue_depth{source="store_coordinator"})
```

**Common Issues**:
- Prometheus not reachable from KEDA pods
- Metric query returns no data (check label selectors)
- `serverAddress` incorrect in ScaledObject

---

### Metrics not appearing

**Symptoms**: `/metrics` endpoint returns empty or missing pipeline metrics

**Check**:
```bash
# Port-forward to pipeline pod
kubectl -n market-data port-forward deployment/mdp-pipeline 8000:8000

# Curl metrics
curl http://localhost:8000/metrics | grep pipeline_

# Check environment variables
kubectl -n market-data exec deployment/mdp-pipeline -- env | grep MDP_
```

**Fix**:
```bash
# Ensure MDP_METRICS_ENABLE=true
kubectl -n market-data set env deployment/mdp-pipeline MDP_METRICS_ENABLE=true

# Restart pods
kubectl -n market-data rollout restart deployment/mdp-pipeline
```

---

### Rapid oscillation

**Symptoms**: Pod count rapidly scales up/down

**Fix**: Increase `cooldownPeriod` and `pollingInterval`

```yaml
spec:
  cooldownPeriod: 120  # Increase from 60
  pollingInterval: 30  # Increase from 15
```

---

### High backpressure never scales down

**Symptoms**: Pods scaled up during HARD backpressure but don't scale down when OK

**Check**: Verify both triggers are working:

```bash
# Trigger 1: Queue depth
max(pipeline_feedback_queue_depth{source="store_coordinator"})

# Trigger 2: Backpressure
max(pipeline_backpressure_state) == 2
```

**Note**: KEDA scales based on **maximum** of all triggers. If queue is empty but backpressure is HARD, it won't scale down.

**Fix**: Ensure store feedback is publishing OK events when queue drains.

## 📐 Advanced Configuration

### Multi-trigger scaling

Add additional triggers for rate scale factor:

```yaml
triggers:
  - type: prometheus
    metadata:
      metricName: pipeline_rate_scale_low
      threshold: "0.3"  # Scale up if rate < 30%
      query: |
        min(pipeline_rate_scale_factor) < 0.3
```

### Per-provider scaling

Scale different providers independently:

```yaml
triggers:
  - type: prometheus
    metadata:
      metricName: pipeline_ibkr_backpressure
      threshold: "1"
      query: |
        pipeline_backpressure_state{provider="ibkr"} > 1
```

## 📚 References

- [KEDA Documentation](https://keda.sh/docs/)
- [KEDA Prometheus Scaler](https://keda.sh/docs/2.12/scalers/prometheus/)
- [Phase 6.0B Implementation](../../docs/PHASE_6.0B_KEDA_AUTOSCALING.md)
- [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator)

## 📝 Notes

- **Metric Cardinality**: The `provider` label should remain small (< 10 unique values) to avoid cardinality explosion.
- **Resource Limits**: Adjust `resources` in Deployment based on your workload profile.
- **Cooldown vs Latency**: Higher cooldown = more stable scaling, higher latency = slower response to load changes.
- **Store Capacity**: Coordinate with store team on queue capacity to set appropriate thresholds.

