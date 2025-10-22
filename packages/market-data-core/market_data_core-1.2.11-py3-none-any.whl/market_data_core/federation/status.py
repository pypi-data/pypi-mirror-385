"""Federation status and topology."""

from pydantic import BaseModel, Field
from .types import ClusterId, NodeId, NodeRole, Region
from ..telemetry.health import HealthState


class NodeStatus(BaseModel):
    """Status of a single node in the cluster.
    
    Example:
        ```python
        node = NodeStatus(
            node_id=NodeId(value="pipeline-01"),
            role=NodeRole.pipeline,
            health="healthy",
            version="0.8.1",
            last_seen_ts=time.time()
        )
        ```
    """
    
    node_id: NodeId = Field(..., description="Node identifier")
    role: NodeRole = Field(..., description="Node role")
    health: HealthState = Field(..., description="Node health state")
    version: str = Field(..., description="Software version")
    last_seen_ts: float = Field(..., description="Last heartbeat (Unix epoch)")


class ClusterTopology(BaseModel):
    """Complete cluster topology snapshot.
    
    Example:
        ```python
        topology = ClusterTopology(
            cluster_id=ClusterId(value="prod-cluster"),
            region=Region(name="us-east-1"),
            nodes=[
                NodeStatus(...),
                NodeStatus(...),
            ]
        )
        ```
    """
    
    cluster_id: ClusterId = Field(..., description="Cluster identifier")
    region: Region = Field(..., description="Cluster region")
    nodes: list[NodeStatus] = Field(default_factory=list, description="Nodes in cluster")

