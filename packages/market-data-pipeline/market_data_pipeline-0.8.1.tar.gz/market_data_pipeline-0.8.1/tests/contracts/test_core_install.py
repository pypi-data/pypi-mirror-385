"""
Contract test: Core package installation and imports.

Verifies that market-data-core v1.1.0+ can be imported and
provides expected public interfaces.
"""

import pytest


def test_core_version_imports():
    """
    Verify Core v1.1.0 telemetry and protocol imports.
    
    This test ensures the pipeline can import all required Core DTOs
    and protocols. Failure indicates a breaking change in Core's public API.
    """
    # Import telemetry DTOs
    from market_data_core.telemetry import (
        BackpressureLevel,
        FeedbackEvent,
        RateAdjustment,
    )
    
    # Import protocols
    from market_data_core.protocols import FeedbackPublisher, RateController
    
    # Verify BackpressureLevel enum
    assert BackpressureLevel.ok.value == "ok"
    assert BackpressureLevel.soft.value == "soft"
    assert BackpressureLevel.hard.value == "hard"
    
    # Verify protocol classes exist
    assert RateController is not None
    assert FeedbackPublisher is not None
    
    # Verify DTOs are Pydantic models
    assert hasattr(FeedbackEvent, 'model_validate')
    assert hasattr(RateAdjustment, 'model_dump')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

