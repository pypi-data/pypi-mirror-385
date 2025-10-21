"""Federation type definitions."""

from enum import Enum
from pydantic import BaseModel, Field


class ClusterId(BaseModel):
    """Unique cluster identifier.
    
    Example:
        ```python
        cluster = ClusterId(value="prod-us-east-1")
        ```
    """
    
    value: str = Field(..., min_length=1, description="Cluster ID")
    
    class Config:
        frozen = True


class NodeId(BaseModel):
    """Unique node identifier within a cluster.
    
    Example:
        ```python
        node = NodeId(value="orchestrator-01")
        ```
    """
    
    value: str = Field(..., min_length=1, description="Node ID")
    
    class Config:
        frozen = True


class NodeRole(str, Enum):
    """Node role in the market data system."""
    
    orchestrator = "orchestrator"  # Orchestration/control plane
    pipeline = "pipeline"          # Data pipeline worker
    store = "store"                # Storage coordinator


class Region(BaseModel):
    """Geographic region for node placement.
    
    Example:
        ```python
        region = Region(name="us-east-1", zone="us-east-1a")
        ```
    """
    
    name: str = Field(..., description="Region name")
    zone: str | None = Field(default=None, description="Availability zone")

