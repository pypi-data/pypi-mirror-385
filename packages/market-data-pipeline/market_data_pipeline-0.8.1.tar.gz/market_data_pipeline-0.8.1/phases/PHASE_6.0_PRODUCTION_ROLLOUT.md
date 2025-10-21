# Phase 6.0 - Production Rollout Guide

**Version**: v0.8.1  
**Status**: ✅ READY TO SHIP  
**Estimated Time**: 15-30 minutes

---

## 🎯 Pre-Flight Checklist

- [ ] Git on `base` branch with v0.8.1 tag
- [ ] Docker registry access configured
- [ ] Kubernetes cluster context set
- [ ] KEDA operator installed (`kubectl get deploy -n keda`)
- [ ] Prometheus running and accessible
- [ ] Store WriteCoordinator ready (market_data_store v0.3.0+)

---

## 🚀 Step 1: Build & Push (5 min)

### Set Variables

```bash
# Configure your registry
export REG="your-registry.example.com"  # or ghcr.io/your-org
export IMAGE_TAG="0.8.1"

# Verify git state
git checkout base
git pull origin base
git describe --tags  # Should show v0.8.1
```

### Build Image

```bash
# Option A: Docker
docker build -t $REG/mdp-pipeline:$IMAGE_TAG .
docker push $REG/mdp-pipeline:$IMAGE_TAG

# Option B: With BuildKit (faster)
DOCKER_BUILDKIT=1 docker build -t $REG/mdp-pipeline:$IMAGE_TAG .
docker push $REG/mdp-pipeline:$IMAGE_TAG

# Tag as latest (optional)
docker tag $REG/mdp-pipeline:$IMAGE_TAG $REG/mdp-pipeline:latest
docker push $REG/mdp-pipeline:latest
```

**Verify**:
```bash
docker images | grep mdp-pipeline
# Should show: $REG/mdp-pipeline  0.8.1  <image-id>  <size>
```

---

## ☸️ Step 2: Deploy to Kubernetes (5 min)

### Update Deployment Manifest

```bash
# Edit deploy/keda/deployment-pipeline.yaml
# Line 25: Update image reference
sed -i "s|image:.*|image: $REG/mdp-pipeline:$IMAGE_TAG|" deploy/keda/deployment-pipeline.yaml

# Or manually edit:
# image: your-registry.example.com/mdp-pipeline:0.8.1
```

### Apply Manifests

```bash
# Create namespace (idempotent)
kubectl create namespace market-data --dry-run=client -o yaml | kubectl apply -f -

# Apply deployment
kubectl -n market-data apply -f deploy/keda/deployment-pipeline.yaml

# Apply KEDA ScaledObject
kubectl -n market-data apply -f deploy/keda/scaledobject-pipeline.yaml

# Apply Prometheus ServiceMonitor (if using Prometheus Operator)
kubectl -n market-data apply -f deploy/keda/prometheus-servicemonitor.yaml
```

**Expected Output**:
```
deployment.apps/mdp-pipeline configured
scaledobject.keda.sh/mdp-pipeline-scaler created
servicemonitor.monitoring.coreos.com/mdp-pipeline created
service/mdp-pipeline created
```

---

## ✅ Step 3: Health Checks (2 min)

### Pod Status

```bash
# Wait for pod to be ready
kubectl -n market-data get pods -l app=mdp-pipeline -w
# CTRL+C after STATUS = Running, READY = 1/1

# Check logs
kubectl -n market-data logs -l app=mdp-pipeline --tail=50

# Expected: No errors, "Application startup complete"
```

### Metrics Endpoint

```bash
# Port-forward to pod
kubectl -n market-data port-forward deploy/mdp-pipeline 8000:8000 &

# Test health
curl localhost:8000/health
# Expected: {"status":"healthy","service":"market-data-pipeline"}

# Test metrics
curl localhost:8000/metrics | grep -E 'pipeline_(rate_scale_factor|backpressure_state|feedback_queue_depth)'

# Expected output:
# # HELP pipeline_rate_scale_factor Current rate scale factor...
# # TYPE pipeline_rate_scale_factor gauge
# # HELP pipeline_backpressure_state Backpressure state...
# # TYPE pipeline_backpressure_state gauge
# # HELP pipeline_feedback_queue_depth Queue depth...
# # TYPE pipeline_feedback_queue_depth gauge

# Stop port-forward
kill %1
```

---

## 📊 Step 4: Prometheus Verification (3 min)

### Check Target

```bash
# Port-forward to Prometheus
kubectl -n monitoring port-forward svc/prometheus 9090:9090 &

# Open browser: http://localhost:9090/targets
# Search for: market_data_pipeline or mdp-pipeline
# Status should be: UP (1/1)
```

### Test Queries

Execute these in Prometheus UI or via API:

```promql
# Query 1: Queue depth (should return data, may be 0)
max(pipeline_feedback_queue_depth{source="store_coordinator"})

# Query 2: Rate scale (should return 1.0 initially)
avg(pipeline_rate_scale_factor{provider="ibkr"})

# Query 3: Backpressure (should return 0 = OK)
max(pipeline_backpressure_state{provider="ibkr"})
```

**Via curl**:
```bash
# Query queue depth
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=max(pipeline_feedback_queue_depth{source="store_coordinator"})'

# Expected: {"status":"success","data":{"resultType":"vector",...}}
```

**Stop port-forward**:
```bash
kill %1
```

---

## 📈 Step 5: Grafana Dashboard (5 min)

### Import Dashboard

1. Navigate to Grafana → Dashboards → Import
2. Copy JSON from `PHASE_6.0_VERIFICATION_REPORT.md` (Section 3)
3. Or create manually:

### Panel 1: Queue Depth (Time Series)

```json
{
  "title": "Store Queue Depth",
  "targets": [{
    "expr": "max(pipeline_feedback_queue_depth{source=\"store_coordinator\"})",
    "legendFormat": "Queue Depth"
  }],
  "fieldConfig": {
    "defaults": {
      "unit": "short",
      "thresholds": {
        "steps": [
          {"value": 0, "color": "green"},
          {"value": 5000, "color": "yellow"},
          {"value": 8000, "color": "red"}
        ]
      }
    }
  },
  "options": {
    "tooltip": {"mode": "multi"},
    "legend": {"displayMode": "list"}
  }
}
```

### Panel 2: Rate Scale (Gauge)

```json
{
  "title": "Pipeline Rate Scale",
  "targets": [{
    "expr": "avg(pipeline_rate_scale_factor{provider=\"ibkr\"})"
  }],
  "type": "gauge",
  "fieldConfig": {
    "defaults": {
      "unit": "percentunit",
      "min": 0,
      "max": 1,
      "thresholds": {
        "steps": [
          {"value": 0, "color": "red"},
          {"value": 0.5, "color": "yellow"},
          {"value": 0.9, "color": "green"}
        ]
      }
    }
  }
}
```

### Panel 3: Backpressure State (Stat)

```json
{
  "title": "Backpressure State",
  "targets": [{
    "expr": "max(pipeline_backpressure_state{provider=\"ibkr\"})"
  }],
  "type": "stat",
  "fieldConfig": {
    "defaults": {
      "mappings": [
        {"value": 0, "text": "OK", "color": "green"},
        {"value": 1, "text": "SOFT", "color": "yellow"},
        {"value": 2, "text": "HARD", "color": "red"}
      ]
    }
  }
}
```

### Panel 4: Pod Count (Stat)

```json
{
  "title": "Active Pods",
  "targets": [{
    "expr": "count(kube_pod_info{namespace=\"market-data\", pod=~\"mdp-pipeline-.*\", phase=\"Running\"})"
  }],
  "type": "stat"
}
```

### Configure Alerts

**Alert 1: High Queue Depth**
```yaml
alert: PipelineQueueHigh
expr: max(pipeline_feedback_queue_depth{source="store_coordinator"}) > 8000
for: 5m
labels:
  severity: warning
annotations:
  summary: "Pipeline queue depth high: {{ $value }}"
```

**Alert 2: Hard Backpressure**
```yaml
alert: PipelineHardBackpressure
expr: max(pipeline_backpressure_state{provider="ibkr"}) == 2
for: 2m
labels:
  severity: critical
annotations:
  summary: "Pipeline in HARD backpressure state"
```

**Alert 3: Low Rate Scale**
```yaml
alert: PipelineRateScaleLow
expr: avg(pipeline_rate_scale_factor{provider="ibkr"}) < 0.3
for: 10m
labels:
  severity: warning
annotations:
  summary: "Pipeline rate scaled down to {{ $value }}"
```

---

## 🔄 Step 6: KEDA Verification (5 min)

### Check ScaledObject

```bash
# View ScaledObject config
kubectl -n market-data get scaledobject mdp-pipeline-scaler -o yaml

# Check min/max replicas
kubectl -n market-data get scaledobject mdp-pipeline-scaler -o yaml | grep -E 'minReplicaCount|maxReplicaCount'
# Expected:
# minReplicaCount: 1
# maxReplicaCount: 10

# Check HPA (created by KEDA)
kubectl -n market-data get hpa
# NAME                              REFERENCE                 TARGETS         MINPODS   MAXPODS   REPLICAS
# keda-hpa-mdp-pipeline-scaler      Deployment/mdp-pipeline   <unknown>/5000  1         10        1
```

### Monitor Scaling (Real-Time)

```bash
# Watch HPA status
kubectl -n market-data get hpa -w

# In another terminal: Watch pods
kubectl -n market-data get pods -l app=mdp-pipeline -w

# In another terminal: Watch KEDA logs
kubectl -n keda logs -l app=keda-operator -f
```

### Trigger Scale-Up (Optional Test)

If you have control over the store to simulate load:

1. **Increase write rate** → Queue fills to > 5000
2. **Observe**: HPA target value increases
3. **Wait 15-30s**: New pods start (DESIRED → 3-5)
4. **Reduce load** → Queue drains to < 2000
5. **Wait 60s** (cooldown): Pods scale down to 1

---

## 🔙 Rollback Procedures

### Quick Rollback (Undo Last Deploy)

```bash
# Rollback to previous deployment
kubectl -n market-data rollout undo deployment/mdp-pipeline

# Check status
kubectl -n market-data rollout status deployment/mdp-pipeline
```

### Rollback to Specific Version

```bash
# List rollout history
kubectl -n market-data rollout history deployment/mdp-pipeline

# Rollback to specific revision
kubectl -n market-data rollout undo deployment/mdp-pipeline --to-revision=2
```

### Pin to Previous Image

```bash
# Set specific image version
export PREV_TAG="0.8.0"
kubectl -n market-data set image deployment/mdp-pipeline \
  pipeline=$REG/mdp-pipeline:$PREV_TAG

# Verify
kubectl -n market-data get deployment mdp-pipeline -o yaml | grep image:
```

### Emergency: Delete ScaledObject

```bash
# Stop KEDA scaling (keeps pods running)
kubectl -n market-data delete scaledobject mdp-pipeline-scaler

# HPA will be removed, replicas stay at current count
```

---

## ⚙️ Step 7: Configuration Tuning

### Adjust KEDA Thresholds

**Conservative Start** (recommended):
```yaml
# deploy/keda/scaledobject-pipeline.yaml
triggers:
  - type: prometheus
    metadata:
      threshold: "5000"  # store_capacity * 0.5
```

**Aggressive** (high throughput):
```yaml
triggers:
  - type: prometheus
    metadata:
      threshold: "8000"  # store_capacity * 0.8
```

**Apply changes**:
```bash
kubectl -n market-data apply -f deploy/keda/scaledobject-pipeline.yaml
```

### Adjust Cooldown/Polling

```yaml
spec:
  cooldownPeriod: 60      # Seconds before scale-down
  pollingInterval: 15     # Seconds between Prometheus queries
```

**Reduce oscillation** (increase both):
```yaml
spec:
  cooldownPeriod: 120     # More conservative scale-down
  pollingInterval: 30     # Less frequent checks
```

---

## 📋 Post-Deployment Checklist

- [ ] All pods running (1/1 READY)
- [ ] Health endpoint responding
- [ ] Metrics endpoint returning Phase 6.0 metrics
- [ ] Prometheus target UP
- [ ] Grafana dashboard showing data
- [ ] KEDA ScaledObject active
- [ ] HPA created and showing targets
- [ ] Alerts configured
- [ ] Rollback plan documented
- [ ] Team notified of deployment

---

## 🎯 Expected Behavior

### Normal Operation (Baseline)

```
Pods: 1
Queue Depth: 500-2000
Backpressure: 0 (OK)
Rate Scale: 1.0 (100%)
```

### Moderate Load

```
Pods: 1 → 3 (15-30s)
Queue Depth: 5000-7000
Backpressure: 1 (SOFT)
Rate Scale: 0.5 (50%)
```

### High Load

```
Pods: 3 → 8 (30-60s)
Queue Depth: 9000+
Backpressure: 2 (HARD)
Rate Scale: 0.0 (paused)
```

### Recovery

```
Pods: 8 → 1 (60-90s after queue < 2000)
Queue Depth: < 1000
Backpressure: 0 (OK)
Rate Scale: 1.0 (100%)
```

---

## 🚨 Troubleshooting

### Issue: Pod CrashLoopBackOff

```bash
# Check logs
kubectl -n market-data logs -l app=mdp-pipeline --tail=100

# Common causes:
# - Missing environment variables
# - Database connection failed
# - Store coordinator unreachable

# Fix: Check environment config
kubectl -n market-data get deployment mdp-pipeline -o yaml | grep -A 20 env:
```

### Issue: Metrics not appearing in Prometheus

```bash
# Check ServiceMonitor
kubectl -n market-data get servicemonitor mdp-pipeline -o yaml

# Check service endpoints
kubectl -n market-data get endpoints mdp-pipeline

# Test direct scrape
kubectl -n market-data port-forward deploy/mdp-pipeline 8000:8000 &
curl localhost:8000/metrics
kill %1

# Check Prometheus config
# Verify: serviceMonitorSelector matches labels
```

### Issue: KEDA not scaling

```bash
# Check KEDA operator logs
kubectl -n keda logs -l app=keda-operator --tail=50

# Check ScaledObject events
kubectl -n market-data describe scaledobject mdp-pipeline-scaler

# Verify Prometheus query
kubectl -n market-data get scaledobject mdp-pipeline-scaler -o yaml | grep query:

# Test query manually in Prometheus
```

### Issue: Rapid pod oscillation

**Symptoms**: Pods scale 1→3→1→3 rapidly

**Fix**: Increase cooldown and polling intervals

```bash
kubectl -n market-data edit scaledobject mdp-pipeline-scaler

# Change:
# cooldownPeriod: 120 (from 60)
# pollingInterval: 30 (from 15)
```

---

## 💡 Operations Tips

### 1. Start Conservative

- **Threshold**: Set to `store_capacity * 0.5` initially
- **Max replicas**: Start with 5, increase if needed
- **Cooldown**: Keep at 60s, increase if oscillating

### 2. Grafana Smoothing

Use **5-10 minute rolling averages** to avoid reacting to transient spikes:

```promql
# Instead of: max(pipeline_feedback_queue_depth)
# Use: avg_over_time(max(pipeline_feedback_queue_depth)[5m])
```

### 3. Monitor Cardinality

Watch for cardinality explosion if adding many providers:

```promql
# Check unique label combinations
count(count by(provider) (pipeline_rate_scale_factor))

# Expected: < 10 providers
# If > 20: Consider aggregation
```

### 4. Gradual Rollout

Deploy to environments in this order:
1. **Dev** (validate KEDA scaling)
2. **Staging** (validate with realistic load)
3. **Production** (monitor for 24-48h)

### 5. Canary Deployment (Optional)

```yaml
# Use Argo Rollouts or Flagger for gradual rollout
spec:
  replicas: 5
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: {duration: 5m}
      - setWeight: 50
      - pause: {duration: 5m}
      - setWeight: 100
```

---

## 📞 Emergency Contacts

| Issue | Contact | SLA |
|-------|---------|-----|
| Pod crashes | Platform team | 15 min |
| KEDA not scaling | Platform team | 30 min |
| Metrics missing | Observability team | 1 hour |
| High backpressure | Data team + Store team | 15 min |

---

## 📊 Success Criteria (First 24h)

- [ ] Zero pod crashes
- [ ] KEDA scaled up at least once
- [ ] KEDA scaled down successfully
- [ ] No alert fatigue (< 5 alerts/day)
- [ ] Metrics continuity (no gaps)
- [ ] Grafana dashboard showing expected behavior
- [ ] Team trained on troubleshooting procedures

---

## 🎉 Production Deployment Complete!

**Time to Production**: ~30 minutes  
**Rollback Time**: < 2 minutes  
**Zero Downtime**: ✅  
**Full Observability**: ✅  
**Adaptive Scaling**: ✅

---

**You're now running a fully adaptive, self-scaling, production-grade market data pipeline!** 🚀

**Monitor for 24-48 hours, then celebrate!** 🎊

