"""Pipeline-specific exceptions."""


class PipelineError(Exception):
    """Base exception for pipeline errors."""

    pass


class SourceError(PipelineError):
    """Source-related errors."""

    pass


class OperatorError(PipelineError):
    """Operator-related errors."""

    pass


class BatcherError(PipelineError):
    """Batcher-related errors."""

    pass


class SinkError(PipelineError):
    """Sink-related errors."""

    pass


class PacingError(PipelineError):
    """Pacing/throttling errors."""

    pass


class ConfigurationError(PipelineError):
    """Configuration-related errors."""

    pass


class SchemaValidationError(PipelineError):
    """
    Raised when schema validation fails in strict enforcement mode.
    
    Phase 11.1: Used when REGISTRY_ENFORCEMENT=strict and payload
    fails validation against registry schema.
    
    Attributes:
        schema_name: Name of schema that failed validation
        errors: List of validation error messages
        track: Schema track (v1/v2) used for validation
        enforcement_mode: Enforcement mode at time of error
    """

    def __init__(
        self,
        message: str,
        schema_name: str,
        errors: list[str],
        track: str,
        enforcement_mode: str = "strict",
    ) -> None:
        """Initialize validation error."""
        super().__init__(message)
        self.schema_name = schema_name
        self.errors = errors
        self.track = track
        self.enforcement_mode = enforcement_mode