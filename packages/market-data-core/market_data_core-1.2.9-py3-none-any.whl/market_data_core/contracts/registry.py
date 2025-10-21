"""Schema registry metadata and index generation.

Phase 9.0: Provides metadata tracking for versioned schemas.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SchemaMeta:
    """Metadata for a single schema in the registry.
    
    Tracks version, location, deprecation status, and compatibility info.
    """

    schema_id: str  # e.g. "telemetry.FeedbackEvent"
    core_version: str  # e.g. "1.1.2" or "2.0.0-dev"
    track: str  # "v1" or "v2"
    kind: str  # "telemetry" | "federation" | "registry"
    file: str  # relative path within artifacts/core-schemas/{track}/
    sha256: str  # content hash for verification
    deprecated: bool = False
    supersedes: list[str] | None = None  # schema_ids this version supersedes

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "schema_id": self.schema_id,
            "core_version": self.core_version,
            "track": self.track,
            "kind": self.kind,
            "file": self.file,
            "sha256": self.sha256,
            "deprecated": self.deprecated,
            "supersedes": self.supersedes or [],
        }


def make_index(entries: list[SchemaMeta]) -> dict:
    """Create a registry index from schema metadata entries.
    
    Args:
        entries: List of schema metadata entries
        
    Returns:
        Dictionary representing the complete registry index
    """
    return {
        "generated_at": int(time.time()),
        "core": {
            "version": entries[0].core_version if entries else "unknown",
        },
        "tracks": sorted({e.track for e in entries}),
        "schemas": [e.to_dict() for e in entries],
    }


def write_index(root: Path, entries: list[SchemaMeta]) -> None:
    """Write the registry index to disk.
    
    Args:
        root: Root directory for schema artifacts
        entries: List of schema metadata entries
    """
    index_path = root / "index.json"
    index_path.write_text(json.dumps(make_index(entries), indent=2))
    print(f"✅ Registry index written to {index_path}")


def compute_sha256(content: str) -> str:
    """Compute SHA256 hash of schema content.
    
    Args:
        content: JSON schema content as string
        
    Returns:
        Hexadecimal SHA256 hash
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def augment_schema(
    schema: dict,
    *,
    schema_id: str,
    core_version: str,
    track: str,
    deprecated_fields: dict[str, str] | None = None,
) -> dict:
    """Augment a JSON schema with Core-specific metadata.
    
    Args:
        schema: Base JSON schema dictionary
        schema_id: Unique identifier (e.g., "telemetry.FeedbackEvent")
        core_version: Core version string
        track: Version track ("v1" or "v2")
        deprecated_fields: Optional mapping of field name to deprecation message
        
    Returns:
        Augmented schema with metadata fields
    """
    out = dict(schema)
    
    # Add Core metadata at top level
    out["$schema_id"] = schema_id
    out["$core_version"] = core_version
    out["$track"] = track
    
    # Add deprecation metadata if present
    if deprecated_fields:
        out["x-deprecated"] = {"fields": deprecated_fields}
    
    return out

