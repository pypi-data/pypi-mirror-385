"""Tests for v1.1.0 protocol additions."""

from market_data_core.protocols import (
    ProviderRegistry,
    SinkRegistry,
    FeedbackPublisher,
    RateController,
    FederationDirectory,
)


class TestProtocolConformance:
    """Tests for protocol conformance checks."""
    
    def test_provider_registry_protocol(self):
        """Test ProviderRegistry protocol conformance."""
        
        class MockRegistry:
            def providers(self):
                return []
            
            def get(self, name: str):
                return None
        
        registry = MockRegistry()
        assert isinstance(registry, ProviderRegistry)
    
    def test_sink_registry_protocol(self):
        """Test SinkRegistry protocol conformance."""
        
        class MockSinkRegistry:
            def sinks(self):
                return []
            
            def get(self, name: str):
                return None
        
        registry = MockSinkRegistry()
        assert isinstance(registry, SinkRegistry)
    
    def test_feedback_publisher_protocol(self):
        """Test FeedbackPublisher protocol conformance."""
        
        class MockPublisher:
            async def publish(self, event):
                pass
        
        publisher = MockPublisher()
        assert isinstance(publisher, FeedbackPublisher)
    
    def test_rate_controller_protocol(self):
        """Test RateController protocol conformance."""
        
        class MockController:
            async def apply(self, adj):
                pass
        
        controller = MockController()
        assert isinstance(controller, RateController)
    
    def test_federation_directory_protocol(self):
        """Test FederationDirectory protocol conformance."""
        
        class MockDirectory:
            def topology(self):
                return None
            
            def endpoints(self):
                return {}
        
        directory = MockDirectory()
        assert isinstance(directory, FederationDirectory)

