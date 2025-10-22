"""Registry protocols for schema enforcement and drift detection.

These protocols define the interfaces that Registry clients and downstream
services should implement for Phase 11.1 enforcement and drift intelligence.
"""

from __future__ import annotations

from typing import Any, Protocol

from market_data_core.models.registry import (
    EnforcementMode,
    SchemaDriftEvent,
    SchemaValidationResult,
)


class RegistryClient(Protocol):
    """Protocol for a Registry client that supports schema fetching and validation.
    
    Implementations:
    - core-registry-client SDK (v0.2.0+)
    - Custom client implementations in downstream services
    """

    async def get_schema(self, track: str, name: str) -> dict[str, Any]:
        """Fetch a schema from the Registry by track and name.
        
        Args:
            track: Schema track ('v1' or 'v2')
            name: Schema name (e.g., 'telemetry.FeedbackEvent.schema')
            
        Returns:
            JSON Schema dictionary
            
        Raises:
            SchemaNotFoundError: If schema doesn't exist in Registry
            RegistryUnavailableError: If Registry is unreachable
        """
        ...

    async def validate(
        self, payload: dict[str, Any], schema_name: str, track: str = "v1"
    ) -> SchemaValidationResult:
        """Validate a payload against a Registry schema.
        
        Args:
            payload: The data to validate
            schema_name: Name of schema to validate against
            track: Schema track to use
            
        Returns:
            SchemaValidationResult with validation outcome
        """
        ...


class DriftDetector(Protocol):
    """Protocol for services that detect schema drift.
    
    Services should implement this protocol to compare their local schemas
    against the Registry and emit drift events via Pulse.
    """

    async def detect_drift(self, schema_name: str, track: str = "v1") -> SchemaDriftEvent | None:
        """Detect drift between local schema and Registry version.
        
        Args:
            schema_name: Name of schema to check
            track: Schema track to check
            
        Returns:
            SchemaDriftEvent if drift detected, None if schemas match
        """
        ...

    async def emit_drift_event(self, event: SchemaDriftEvent) -> None:
        """Publish a drift event to the Pulse event bus.
        
        Args:
            event: The drift event to emit
        """
        ...


class EnforcementPolicy(Protocol):
    """Protocol for enforcement policy implementations.
    
    Services should implement this to decide how to handle validation failures
    based on the configured enforcement mode.
    """

    @property
    def mode(self) -> EnforcementMode:
        """Current enforcement mode ('warn' or 'strict')."""
        ...

    def handle_validation_failure(
        self, result: SchemaValidationResult, payload: Any
    ) -> None:
        """Handle a validation failure according to enforcement policy.
        
        Args:
            result: The validation result (with errors)
            payload: The original payload that failed validation
            
        Raises:
            SchemaValidationError: If enforcement mode is 'strict'
        """
        ...


class SchemaUsageTracker(Protocol):
    """Protocol for tracking schema usage metrics.
    
    Registry service should implement this to track which schemas are actively
    used, enabling deprecation planning and usage dashboards.
    """

    async def record_access(self, schema_name: str, track: str, service: str) -> None:
        """Record a schema access event.
        
        Args:
            schema_name: Name of accessed schema
            track: Schema track accessed
            service: Service that accessed the schema
        """
        ...

    async def get_usage_stats(self, schema_name: str, track: str) -> dict[str, Any]:
        """Get usage statistics for a schema.
        
        Args:
            schema_name: Name of schema
            track: Schema track
            
        Returns:
            Dict with usage stats (access_count, last_accessed, services, etc.)
        """
        ...

