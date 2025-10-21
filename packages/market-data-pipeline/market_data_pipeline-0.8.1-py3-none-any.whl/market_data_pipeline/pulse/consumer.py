"""
Pulse feedback consumer — subscribes to telemetry.feedback and applies rate adjustments.

Phase 10.1: Wraps existing FeedbackHandler with Pulse event bus transport.
"""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

from loguru import logger
from market_data_core.events import create_event_bus
from market_data_core.events.envelope import EventEnvelope
from market_data_core.telemetry import FeedbackEvent

from ..orchestration.feedback.consumer import FeedbackHandler

if TYPE_CHECKING:
    from market_data_core.protocols import RateController
    from ..settings.feedback import PipelineFeedbackSettings
    from ..schemas import SchemaManager
    from .config import PulseConfig


STREAM = "telemetry.feedback"
GROUP = "pipeline"


class FeedbackConsumer:
    """
    Pulse consumer for Store feedback events.
    
    Subscribes to telemetry.feedback stream and applies rate adjustments
    via RateController using existing FeedbackHandler business logic.
    
    Features:
        - Idempotency: Deduplicate redelivered messages
        - Metrics: pulse_consume_total, pulse_lag_ms
        - ACK/FAIL: At-least-once delivery with DLQ
    
    Example:
        cfg = PulseConfig()
        settings = PipelineFeedbackSettings()
        consumer = FeedbackConsumer(rate_controller, settings, cfg)
        await consumer.run(consumer_name="pipeline_w1")
    """
    
    def __init__(
        self,
        rate_controller: RateController,
        settings: PipelineFeedbackSettings,
        cfg: PulseConfig | None = None,
        schema_manager: SchemaManager | None = None,
    ) -> None:
        """
        Initialize Pulse feedback consumer.
        
        Args:
            rate_controller: Core RateController protocol implementation
            settings: Pipeline feedback settings (policy, provider)
            cfg: Pulse configuration (defaults to env-based)
            schema_manager: Optional schema manager for validation (Phase 11.0B)
        """
        self.cfg = cfg or PulseConfig()
        self.settings = settings
        self.schema_manager = schema_manager
        
        # Reuse existing FeedbackHandler business logic
        self.handler = FeedbackHandler(
            rate=rate_controller,
            provider=settings.provider_name,
            policy=settings.get_policy(),
        )
        
        # Create event bus (inmem or redis)
        self.bus = create_event_bus(
            backend=self.cfg.backend,
            redis_url=self.cfg.redis_url if self.cfg.backend == "redis" else None,
        )
        
        # Idempotency: simple seen-set (LRU cache in production)
        self._seen_ids: set[str] = set()
        self._seen_lock = asyncio.Lock()
        
        # Metrics
        self._metrics_available = False
        try:
            from ...metrics import (
                PULSE_CONSUME_TOTAL,
                PULSE_LAG_MS,
            )
            self._metric_consume = PULSE_CONSUME_TOTAL
            self._metric_lag = PULSE_LAG_MS
            self._metrics_available = True
        except ImportError:
            logger.warning("Pulse metrics not available (prometheus-client not installed)")
    
    async def _is_seen(self, envelope_id: str) -> bool:
        """Check if envelope has been processed (idempotency)."""
        async with self._seen_lock:
            if envelope_id in self._seen_ids:
                return True
            self._seen_ids.add(envelope_id)
            
            # Simple LRU: keep only last 10k IDs
            if len(self._seen_ids) > 10000:
                # Remove oldest 1000 (approximation)
                to_remove = list(self._seen_ids)[:1000]
                for eid in to_remove:
                    self._seen_ids.discard(eid)
            
            return False
    
    async def _handle(self, envelope: EventEnvelope[FeedbackEvent]) -> None:
        """
        Handle a feedback event envelope.
        
        Args:
            envelope: Event envelope with FeedbackEvent payload
        """
        # Idempotency check
        if await self._is_seen(envelope.id):
            logger.debug(f"[pulse] Skipping duplicate envelope: {envelope.id}")
            if self._metrics_available:
                self._metric_consume.labels(
                    stream=STREAM,
                    track=self.cfg.track,
                    outcome="duplicate",
                ).inc()
            return
        
        # Phase 11.0B + 11.1: Schema validation with enforcement modes
        if self.schema_manager and self.schema_manager.enabled:
            try:
                is_valid, errors = await self.schema_manager.validate_payload(
                    "telemetry.FeedbackEvent",
                    envelope.payload.model_dump(),
                    prefer=self.cfg.track,
                    fallback="v1",
                )
                
                if not is_valid:
                    logger.warning(
                        f"[pulse] Schema validation failed for envelope {envelope.id}: {errors}"
                    )
                    # In warn mode, continue processing
                    
            except Exception as e:
                # Phase 11.1: SchemaValidationError raised in strict mode
                from ..errors import SchemaValidationError
                
                if isinstance(e, SchemaValidationError):
                    # Strict mode: validation failed, fail envelope to DLQ
                    logger.error(
                        f"[pulse] STRICT MODE: Schema validation failed, failing to DLQ: {e.errors}"
                    )
                    raise  # Re-raise to trigger DLQ processing
                else:
                    # Other validation errors: log but don't fail processing
                    logger.warning(f"[pulse] Schema validation error: {e}")
        
        # Delegate to existing FeedbackHandler
        await self.handler.handle(envelope.payload)
    
    async def run(self, consumer_name: str) -> None:
        """
        Start the Pulse consumer loop.
        
        Subscribes to telemetry.feedback and processes events until cancelled.
        
        Args:
            consumer_name: Consumer identifier for this worker (e.g., "pipeline_w1")
        
        Raises:
            asyncio.CancelledError: On graceful shutdown
        """
        stream = f"{self.cfg.ns}.{STREAM}"
        logger.info(
            f"[pulse] Starting feedback consumer: stream={stream} group={GROUP} consumer={consumer_name}"
        )
        
        try:
            async for envelope in self.bus.subscribe(stream, group=GROUP, consumer=consumer_name):
                t0 = time.time()
                
                try:
                    # Process event
                    await self._handle(envelope)
                    
                    # ACK successful processing
                    await self.bus.ack(stream, envelope.id)
                    
                    # Metrics: success
                    if self._metrics_available:
                        self._metric_consume.labels(
                            stream=STREAM,
                            track=self.cfg.track,
                            outcome="success",
                        ).inc()
                
                except Exception as e:
                    # Log and FAIL to DLQ
                    logger.exception(f"[pulse] Error processing envelope {envelope.id}")
                    await self.bus.fail(stream, envelope.id, str(e))
                    
                    # Metrics: error
                    if self._metrics_available:
                        self._metric_consume.labels(
                            stream=STREAM,
                            track=self.cfg.track,
                            outcome="error",
                        ).inc()
                
                finally:
                    # Metrics: lag
                    if self._metrics_available:
                        lag_ms = int((time.time() - envelope.ts) * 1000)
                        self._metric_lag.labels(stream=STREAM).set(lag_ms)
        
        except asyncio.CancelledError:
            logger.info("[pulse] Feedback consumer cancelled (graceful shutdown)")
            raise
        except Exception:
            logger.exception("[pulse] Feedback consumer crashed")
            raise

