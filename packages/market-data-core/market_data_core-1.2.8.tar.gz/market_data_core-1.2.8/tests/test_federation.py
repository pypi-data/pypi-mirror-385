"""Tests for federation contracts."""

import time
from market_data_core.federation import (
    ClusterId,
    NodeId,
    NodeRole,
    Region,
    NodeStatus,
    ClusterTopology,
)


class TestFederationTypes:
    """Tests for federation type definitions."""
    
    def test_cluster_id(self):
        """Test ClusterId creation."""
        cluster = ClusterId(value="prod-cluster")
        assert cluster.value == "prod-cluster"
    
    def test_node_id(self):
        """Test NodeId creation."""
        node = NodeId(value="node-01")
        assert node.value == "node-01"
    
    def test_node_role_enum(self):
        """Test NodeRole enum values."""
        assert NodeRole.orchestrator == "orchestrator"
        assert NodeRole.pipeline == "pipeline"
        assert NodeRole.store == "store"
    
    def test_region(self):
        """Test Region with optional zone."""
        region = Region(name="us-west-2", zone="us-west-2a")
        assert region.name == "us-west-2"
        assert region.zone == "us-west-2a"
    
    def test_region_without_zone(self):
        """Test Region without zone."""
        region = Region(name="us-east-1")
        assert region.name == "us-east-1"
        assert region.zone is None


class TestFederationStatus:
    """Tests for federation status models."""
    
    def test_node_status(self):
        """Test NodeStatus creation."""
        status = NodeStatus(
            node_id=NodeId(value="node-01"),
            role=NodeRole.pipeline,
            health="healthy",
            version="1.0.0",
            last_seen_ts=time.time(),
        )
        assert status.role == NodeRole.pipeline
        assert status.health == "healthy"
    
    def test_cluster_topology(self):
        """Test ClusterTopology composition."""
        topology = ClusterTopology(
            cluster_id=ClusterId(value="test-cluster"),
            region=Region(name="us-east-1"),
            nodes=[
                NodeStatus(
                    node_id=NodeId(value="node-01"),
                    role=NodeRole.orchestrator,
                    health="healthy",
                    version="1.0.0",
                    last_seen_ts=time.time(),
                ),
            ],
        )
        assert len(topology.nodes) == 1
        assert topology.nodes[0].role == NodeRole.orchestrator
        assert topology.cluster_id.value == "test-cluster"
    
    def test_topology_empty_nodes(self):
        """Test ClusterTopology with no nodes."""
        topology = ClusterTopology(
            cluster_id=ClusterId(value="empty"),
            region=Region(name="us-east-1"),
            nodes=[],
        )
        assert len(topology.nodes) == 0
    
    def test_topology_json_serialization(self):
        """Test ClusterTopology JSON serialization."""
        topology = ClusterTopology(
            cluster_id=ClusterId(value="test"),
            region=Region(name="us-east-1"),
            nodes=[],
        )
        json_data = topology.model_dump_json()
        assert "test" in json_data
        assert "us-east-1" in json_data

