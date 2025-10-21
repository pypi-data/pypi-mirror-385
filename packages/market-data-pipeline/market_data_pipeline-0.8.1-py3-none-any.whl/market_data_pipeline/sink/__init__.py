"""Sink modules for data persistence."""

from .base import Sink
from .capabilities import SinkCapabilities, SinkHealth, SinkSLA
from .store import StoreSink
from .kafka import KafkaSink
from .database import DatabaseSink, DatabaseSinkSettings
from .telemetry import SinkTelemetry, get_sink_telemetry

__all__ = [
    "Sink",
    "SinkCapabilities",
    "SinkHealth",
    "SinkSLA",
    "StoreSink",
    "KafkaSink",
    "DatabaseSink",
    "DatabaseSinkSettings",
    "SinkTelemetry",
    "get_sink_telemetry",
]
