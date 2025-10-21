"""
Feedback settings for backpressure coordination (Phase 8.0).

Phase 8.0: Updated to use Core v1.1.0 BackpressureLevel enum.

Configures the feedback loop between store WriteCoordinator and
pipeline RateCoordinator using Core telemetry contracts.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings
from market_data_core.telemetry import BackpressureLevel


class PipelineFeedbackSettings(BaseSettings):
    """
    Settings for pipeline backpressure feedback system.
    
    Environment variables:
        MDP_FB_ENABLE_FEEDBACK: Enable/disable feedback (default: True)
        MDP_FB_PROVIDER_NAME: Provider to adjust (default: "ibkr")
        MDP_FB_SCALE_OK: Scale factor for OK state (default: 1.0)
        MDP_FB_SCALE_SOFT: Scale factor for SOFT state (default: 0.5)
        MDP_FB_SCALE_HARD: Scale factor for HARD state (default: 0.0)
    
    Example:
        settings = PipelineFeedbackSettings()
        if settings.enable_feedback:
            handler = FeedbackHandler(
                rate=coordinator,
                provider=settings.provider_name,
                policy=settings.get_policy()
            )
    """

    enable_feedback: bool = Field(
        default=True,
        description="Enable backpressure feedback loop"
    )
    
    provider_name: str = Field(
        default="ibkr",
        description="Provider to adjust rates for"
    )
    
    scale_ok: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Scale factor for OK backpressure state"
    )
    
    scale_soft: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Scale factor for SOFT backpressure state"
    )
    
    scale_hard: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Scale factor for HARD backpressure state"
    )

    model_config = {
        "env_prefix": "MDP_FB_",
        "extra": "ignore"
    }

    def get_policy(self) -> dict[BackpressureLevel, float]:
        """
        Get the scale policy as a dict with Core enum keys.
        
        Phase 8.0: Returns BackpressureLevel enum keys instead of strings.
        
        Returns:
            Dictionary mapping Core BackpressureLevel enum to scale factor
        """
        return {
            BackpressureLevel.ok: self.scale_ok,
            BackpressureLevel.soft: self.scale_soft,
            BackpressureLevel.hard: self.scale_hard,
        }

