"""
Contract tests for market-data-core v1.1.0+ compatibility.

These tests verify that market_data_pipeline maintains compatibility
with core protocol contracts and data transfer objects (DTOs).

Tests in this directory are automatically triggered by market-data-core
when contract schemas change.

Test Categories:
- test_core_install.py: Verifies Core package imports
- test_feedback_flow.py: Tests FeedbackEvent ↔ RateAdjustment flow
- test_protocol_conformance.py: Validates protocol implementations

These are a minimal, fast subset of the comprehensive integration tests.
"""

