# Market Data Pipeline — Documentation Index

## Phase 8.0 — Core v1.1.0 Integration (LATEST) ✅

**Status**: Production-ready | **Version**: v0.9.0 | **Date**: 2025-10-17

### Quick Links

| Document | Purpose | Audience |
|----------|---------|----------|
| [**Migration Guide**](PHASE_8.0_MIGRATION_GUIDE.md) | Step-by-step upgrade instructions | Developers & Operators |
| [**Implementation Complete**](../PHASE_8.0_IMPLEMENTATION_COMPLETE.md) | Technical design & architecture | Technical Reviewers |
| [**Ship-It Summary**](../PHASE_8.0_SHIP_IT_SUMMARY.md) | Executive summary & rollout plan | Leadership & Release Managers |
| [**Viability Assessment**](../PHASE_8.0_UPDATED_VIABILITY_ASSESSMENT.md) | Pre-implementation analysis | Technical Leads |

### What's New in Phase 8.0

✅ **Core Contracts Adopted**
- Integrated `market-data-core v1.1.0` DTOs: `FeedbackEvent`, `RateAdjustment`, `BackpressureLevel`
- Implemented Core protocols: `RateController`, `FeedbackPublisher`
- Protocol conformance verified with `isinstance` checks

✅ **Adapter Pattern**
- `RateCoordinatorAdapter` bridges Core protocols to legacy coordinator
- Zero breaking changes — full backward compatibility
- Deprecation timeline: v0.10.0

✅ **Test Coverage**: 29/29 Tests Passing ✅

### Key Files Changed

- `orchestration/feedback/consumer.py` — Core DTO adoption + adapter
- `orchestration/feedback/bus.py` — Protocol compliance
- `settings/feedback.py` — Enum-based policy keys
- `runtime/unified_runtime.py` — Automatic adapter wrapping

---

## Phase 6.0 — Production Rollout (Previous)

### Phase 6.0B — KEDA Autoscaling

| Document | Status |
|----------|--------|
| [KEDA Implementation](PHASE_6.0B_KEDA_AUTOSCALING.md) | ✅ Complete |
| [Implementation Summary](../PHASE_6.0B_IMPLEMENTATION_COMPLETE.md) | ✅ Complete |

### Phase 6.0A — Backpressure Feedback

| Document | Status |
|----------|--------|
| [Implementation Summary](../PHASE_6.0A_IMPLEMENTATION_COMPLETE.md) | ✅ Complete |
| [Evaluation & Plan](../PHASE_6.0AB_EVALUATION_AND_PLAN.md) | ✅ Complete |

### Phase 6.0 — General

| Document | Status |
|----------|--------|
| [Production Rollout](../PHASE_6.0_PRODUCTION_ROLLOUT.md) | ✅ Complete |
| [Ship-It Checklist](../PHASE_6.0_SHIP_IT_CHECKLIST.md) | ✅ Complete |
| [Verification Report](../PHASE_6.0_VERIFICATION_REPORT.md) | ✅ Complete |

---

## Phase 5.0 — DAG Runtime & Orchestration

### Phase 5.0.5 — Final Iteration

| Document | Status |
|----------|--------|
| [5.0.5a README](PHASE_5.0.5a_README.md) | ✅ Complete |
| [5.0.5b README](PHASE_5.0.5b_README.md) | ✅ Complete |
| [5.0.5c README](PHASE_5.0.5c_README.md) | ✅ Complete |
| [Implementation Summary](../PHASE_5.0.5_IMPLEMENTATION_COMPLETE.md) | ✅ Complete |
| [5.0.5a Implementation](../PHASE_5.0.5a_IMPLEMENTATION_COMPLETE.md) | ✅ Complete |

### Phase 5.0 — Earlier Iterations

| Document | Status |
|----------|--------|
| [Phase 5.0 Index](../PHASE_5_INDEX.md) | Overview |
| [5.0.1 README](PHASE_5.0.1_README.md) | ✅ Complete |
| [5.0.1 Implementation](../PHASE_5.0.1_IMPLEMENTATION_COMPLETE.md) | ✅ Complete |
| [5.0.2 Implementation](../PHASE_5.0.2_IMPLEMENTATION_COMPLETE.md) | ✅ Complete |
| [5.0.3 README](PHASE_5.0.3_README.md) | ✅ Complete |
| [5.0.3 Implementation](../PHASE_5.0.3_IMPLEMENTATION_COMPLETE.md) | ✅ Complete |
| [5.0.4 README](PHASE_5.0.4_README.md) | ✅ Complete |
| [5.0.4 Implementation](../PHASE_5.0.4_IMPLEMENTATION_COMPLETE.md) | ✅ Complete |

### Phase 5.0 — Planning & Architecture

| Document | Status |
|----------|--------|
| [Decision Brief](../PHASE_5_DECISION_BRIEF.md) | Reference |
| [Evaluation & Plan](../PHASE_5_EVALUATION_AND_PLAN.md) | Reference |
| [Visual Summary](../PHASE_5_VISUAL_SUMMARY.md) | Reference |
| [Orchestration Guide](ORCHESTRATION.md) | Reference |

---

## Phase 3 — Initial Architecture

| Document | Status |
|----------|--------|
| [Evaluation](../PHASE_3_EVALUATION.md) | ✅ Complete |
| [Implementation](../PHASE_3_IMPLEMENTATION_COMPLETE.md) | ✅ Complete |

---

## General Documentation

### Guides & References

| Document | Purpose |
|----------|---------|
| [Pipeline Builder Guide](PIPELINE_BUILDER.md) | Pipeline construction API |
| [Production Guide](PRODUCTION.md) | Deployment & operations |
| [Typed Overrides Guide](../TYPED_OVERRIDES_GUIDE.md) | Type-safe configuration |

### Changelogs & Releases

| Document | Purpose |
|----------|---------|
| [CHANGELOG](../CHANGELOG.md) | Version history |
| [PR Description (Phase 6.0)](../PR_PHASE_6.0_DESCRIPTION.md) | Release notes |
| [Implementation Summary](../IMPLEMENTATION_SUMMARY.md) | High-level overview |

---

## Quick Start

### For New Users

1. Read [README](../README.md) — System overview
2. Follow [Quick Start Guide](../QUICK_START_CORE.md) — Get running in 5 minutes
3. Explore [Examples](../examples/README.md) — Sample pipelines

### For Developers Upgrading to v0.9.0

1. Read [Phase 8.0 Migration Guide](PHASE_8.0_MIGRATION_GUIDE.md)
2. Update dependencies: `pip install market-data-core>=1.1.0`
3. Review breaking changes (none!) and deprecations
4. Run tests: `pytest -q --maxfail=1`

---

## Version History

| Version | Phase | Key Features | Status |
|---------|-------|--------------|--------|
| **v0.9.0** | **Phase 8.0** | **Core v1.1.0 integration, protocol adoption** | **✅ Current** |
| v0.7.0 | Phase 6.0 | Backpressure feedback + KEDA autoscaling | ✅ Stable |
| v0.6.0 | Phase 5.0.5 | DAG runtime with unified API | ✅ Stable |
| v0.5.0 | Phase 5.0.4 | DAG orchestration | ✅ Stable |
| v0.4.0 | Phase 5.0.3 | Pipeline primitives | ✅ Stable |
| v0.3.0 | Phase 3 | Initial architecture | ✅ Stable |

---

## Contributing

See [PR Description Template](../PR_DESCRIPTION.md) for contribution guidelines.

---

## Support & Contact

For questions or issues:
- Review relevant phase documentation above
- Check examples in `examples/` directory
- See troubleshooting in migration guides

---

**Last Updated**: 2025-10-17 | **Maintained By**: Market Data Platform Team

