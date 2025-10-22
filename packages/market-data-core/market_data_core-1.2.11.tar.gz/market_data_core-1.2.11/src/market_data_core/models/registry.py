"""Registry event models for schema lifecycle and drift detection.

These models define the event payloads emitted by the Schema Registry Service
and consumed by downstream services for enforcement and drift intelligence.

Phase 11.1: Enforcement & Drift Intelligence
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class EnforcementMode(str, Enum):
    """Enforcement mode for schema validation in downstream services.
    
    - warn: Log validation failures but allow processing (soft enforcement)
    - strict: Reject invalid payloads with exceptions (hard enforcement)
    """

    warn = "warn"
    strict = "strict"


class SchemaPublishedEvent(BaseModel):
    """Event emitted when a schema is published or updated in the Registry.
    
    This event is published by the Registry service after successfully syncing
    schemas from Core releases. Downstream services can subscribe to track
    schema availability and trigger validation updates.
    
    Example:
        >>> event = SchemaPublishedEvent(
        ...     name="telemetry.FeedbackEvent.schema",
        ...     track="v1",
        ...     core_version="v1.2.7",
        ...     sha256="abc123...",
        ...     deprecated=False
        ... )
    """

    __schema_id__ = "registry.SchemaPublishedEvent"

    name: str = Field(..., description="Schema name (e.g., 'telemetry.FeedbackEvent.schema')")
    track: Literal["v1", "v2"] = Field(..., description="Schema track (v1=stable, v2=preview)")
    core_version: str = Field(..., description="Core version that published this schema")
    sha256: str = Field(..., description="Content hash (SHA-256) of the schema")
    deprecated: bool = Field(
        default=False, description="Whether this schema is marked as deprecated"
    )
    supersedes: str | None = Field(
        None, description="Schema name that this version supersedes (if any)"
    )


class SchemaDeprecatedEvent(BaseModel):
    """Event emitted when a schema is marked as deprecated in the Registry.
    
    This event signals to downstream services that they should begin migrating
    to a newer version. Services in 'strict' enforcement mode may choose to
    reject deprecated schemas.
    
    Example:
        >>> event = SchemaDeprecatedEvent(
        ...     name="telemetry.FeedbackEvent.schema",
        ...     track="v1",
        ...     core_version="v1.2.7",
        ...     superseded_by="telemetry.FeedbackEventV2.schema"
        ... )
    """

    __schema_id__ = "registry.SchemaDeprecatedEvent"

    name: str = Field(..., description="Deprecated schema name")
    track: Literal["v1", "v2"] = Field(..., description="Schema track")
    core_version: str = Field(..., description="Core version where deprecation occurred")
    superseded_by: str | None = Field(
        None, description="Recommended replacement schema (if any)"
    )
    deprecation_reason: str | None = Field(
        None, description="Human-readable reason for deprecation"
    )


class SchemaDriftEvent(BaseModel):
    """Event emitted by downstream services when schema drift is detected.
    
    Schema drift occurs when a service's locally embedded schema differs from
    the authoritative version in the Registry. This can happen due to:
    - Service using outdated schema version
    - Registry schema updated but service not yet redeployed
    - Local schema customization/patching
    
    Orchestrator aggregates these events for visibility via Grafana dashboards.
    
    Example:
        >>> event = SchemaDriftEvent(
        ...     service="market-data-store",
        ...     schema_name="telemetry.FeedbackEvent.schema",
        ...     track="v1",
        ...     local_sha="abc123...",
        ...     registry_sha="def456...",
        ...     drift_type="version_mismatch"
        ... )
    """

    __schema_id__ = "telemetry.SchemaDriftEvent"

    service: str = Field(..., description="Service name reporting drift (e.g., 'market-data-store')")
    schema_name: str = Field(..., description="Name of the drifted schema")
    track: Literal["v1", "v2"] = Field(..., description="Schema track")
    local_sha: str = Field(..., description="SHA-256 hash of local schema")
    registry_sha: str = Field(..., description="SHA-256 hash of Registry's schema")
    drift_type: Literal["version_mismatch", "content_mismatch", "missing_in_registry"] = Field(
        ..., description="Type of drift detected"
    )
    detected_at: float = Field(..., description="Unix timestamp when drift was detected")
    enforcement_mode: EnforcementMode = Field(
        default=EnforcementMode.warn, description="Current enforcement mode of the service"
    )


class SchemaValidationResult(BaseModel):
    """Result of schema validation against the Registry.
    
    Used by downstream services to track validation outcomes and decide
    whether to allow or reject payloads based on enforcement mode.
    
    Example:
        >>> result = SchemaValidationResult(
        ...     valid=False,
        ...     schema_name="telemetry.FeedbackEvent.schema",
        ...     track="v1",
        ...     errors=["Missing required field 'coordinator_id'"],
        ...     enforcement_mode=EnforcementMode.warn
        ... )
    """

    valid: bool = Field(..., description="Whether the payload passed validation")
    schema_name: str = Field(..., description="Name of schema used for validation")
    track: Literal["v1", "v2"] = Field(..., description="Schema track used")
    errors: list[str] = Field(
        default_factory=list, description="Validation error messages (if any)"
    )
    enforcement_mode: EnforcementMode = Field(
        ..., description="Enforcement mode at time of validation"
    )
    registry_sha: str | None = Field(
        None, description="SHA-256 of Registry schema (if available)"
    )

