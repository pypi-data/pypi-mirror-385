# Phase 6.0 - "Ship It" Checklist

**Version**: v0.8.1 | **Time**: 15 minutes | **Status**: ✅ READY

---

## 🚀 Quick Deploy (Copy-Paste Ready)

### 1. Build & Push (2 min)

```bash
export REG="your-registry.example.com"
export IMAGE_TAG="0.8.1"

git checkout base && git pull
docker build -t $REG/mdp-pipeline:$IMAGE_TAG .
docker push $REG/mdp-pipeline:$IMAGE_TAG
```

### 2. Update & Deploy (3 min)

```bash
# Update image in manifest
sed -i "s|image:.*|image: $REG/mdp-pipeline:$IMAGE_TAG|" deploy/keda/deployment-pipeline.yaml

# Apply all manifests
kubectl create ns market-data --dry-run=client -o yaml | kubectl apply -f -
kubectl -n market-data apply -f deploy/keda/deployment-pipeline.yaml
kubectl -n market-data apply -f deploy/keda/scaledobject-pipeline.yaml
kubectl -n market-data apply -f deploy/keda/prometheus-servicemonitor.yaml
```

### 3. Verify (2 min)

```bash
# Pods running?
kubectl -n market-data get pods -l app=mdp-pipeline

# Metrics working?
kubectl -n market-data port-forward deploy/mdp-pipeline 8000:8000 &
curl localhost:8000/metrics | grep -E 'pipeline_(rate|backpressure|queue)'
kill %1

# KEDA active?
kubectl -n market-data get scaledobject
```

---

## ✅ Verification Matrix

| Check | Command | Expected |
|-------|---------|----------|
| **Pods** | `kubectl -n market-data get pods` | 1/1 READY |
| **Health** | `curl localhost:8000/health` | `"healthy"` |
| **Metrics** | `curl localhost:8000/metrics \| grep pipeline_` | 3 gauges |
| **Prometheus** | Visit `/targets` | UP (1/1) |
| **KEDA** | `kubectl get scaledobject -n market-data` | READY=True |
| **HPA** | `kubectl get hpa -n market-data` | TARGETS shown |

---

## 📊 Prometheus Queries (Must Work)

```promql
# Queue depth
max(pipeline_feedback_queue_depth{source="store_coordinator"})

# Rate scale  
avg(pipeline_rate_scale_factor{provider="ibkr"})

# Backpressure
max(pipeline_backpressure_state{provider="ibkr"})
```

---

## 🎯 Grafana Quick Setup

**4 Panels Required**:

1. **Queue Depth**: `max(pipeline_feedback_queue_depth)`  
   *Time series, threshold: 5000=yellow, 8000=red*

2. **Rate Scale**: `avg(pipeline_rate_scale_factor)`  
   *Gauge, 0-1 range, <0.5=yellow, <0.2=red*

3. **Backpressure**: `max(pipeline_backpressure_state)`  
   *Stat, 0=OK, 1=SOFT, 2=HARD*

4. **Pod Count**: `count(kube_pod_info{pod=~"mdp-pipeline-.*"})`  
   *Stat*

**Alerts** (3 Required):
- Queue > 8000 for 5m (warning)
- Backpressure == 2 for 2m (critical)
- Rate < 0.3 for 10m (warning)

---

## 🔄 KEDA Behavior (Expected)

| Condition | Queue | State | Scale | Pods |
|-----------|-------|-------|-------|------|
| **Idle** | < 2K | OK (0) | 1.0 | 1 |
| **Moderate** | 5-7K | SOFT (1) | 0.5 | 3-5 |
| **High** | 8-9K | SOFT (1) | 0.5 | 6-8 |
| **Critical** | 9K+ | HARD (2) | 0.0 | 10 |
| **Recovery** | < 2K | OK (0) | 1.0 | 1 |

*Scale-up: 15-30s | Scale-down: 60-90s (cooldown)*

---

## 🚨 Rollback (< 2 min)

```bash
# Option 1: Undo last deployment
kubectl -n market-data rollout undo deployment/mdp-pipeline

# Option 2: Specific version
kubectl -n market-data set image deployment/mdp-pipeline \
  pipeline=$REG/mdp-pipeline:0.8.0

# Option 3: Kill KEDA (emergency)
kubectl -n market-data delete scaledobject mdp-pipeline-scaler
```

---

## ⚡ Quick Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| **Pods crash** | `kubectl logs -n market-data -l app=mdp-pipeline` |
| **No metrics** | Check ServiceMonitor: `kubectl get servicemonitor -n market-data` |
| **KEDA not scaling** | Check logs: `kubectl logs -n keda -l app=keda-operator` |
| **Oscillating** | Edit: `kubectl edit scaledobject -n market-data` → increase cooldown |

---

## 💡 Ops Tips

✅ **Start conservative**: `threshold: 5000` (50% of capacity)  
✅ **Smooth Grafana**: Use 5-min rolling avg  
✅ **Monitor cardinality**: Keep providers < 10  
✅ **Gradual rollout**: Dev → Staging → Prod  
✅ **Watch for 24h**: Before considering stable

---

## 📋 24-Hour Success Criteria

- [ ] Zero pod crashes
- [ ] KEDA scaled up successfully (at least once)
- [ ] KEDA scaled down successfully
- [ ] Metrics continuity (no scrape gaps)
- [ ] < 5 alerts/day
- [ ] Grafana dashboard rendering correctly
- [ ] Team trained on rollback procedure

---

## 🎯 One-Liner Status Check

```bash
kubectl -n market-data get pods,scaledobject,hpa && \
echo "---" && \
curl -s localhost:8000/health && \
echo "---" && \
kubectl -n market-data logs -l app=mdp-pipeline --tail=10
```

---

## 🎉 Ship It!

**Time to Production**: 15 minutes  
**Zero Downtime**: ✅  
**Rollback Ready**: ✅  
**Fully Observable**: ✅  

**Go!** 🚀

