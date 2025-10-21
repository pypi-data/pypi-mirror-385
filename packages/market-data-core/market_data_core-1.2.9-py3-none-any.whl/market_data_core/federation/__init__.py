"""Federation contracts for multi-node deployments."""

from .types import ClusterId, NodeId, NodeRole, Region
from .status import NodeStatus, ClusterTopology

__all__ = [
    # Types
    "ClusterId",
    "NodeId",
    "NodeRole",
    "Region",
    # Status
    "NodeStatus",
    "ClusterTopology",
]

