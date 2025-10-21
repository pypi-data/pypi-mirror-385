"""Tests for registry contracts (DTOs only)."""

from market_data_core.registry import Capability, ProviderSpec, SinkSpec


class TestRegistryTypes:
    """Tests for registry type definitions."""
    
    def test_capability(self):
        """Test Capability DTO."""
        cap = Capability(name="realtime_quotes", params={"delay_ms": "0"})
        assert cap.name == "realtime_quotes"
        assert cap.params["delay_ms"] == "0"
    
    def test_capability_empty_params(self):
        """Test Capability with no params."""
        cap = Capability(name="basic")
        assert cap.name == "basic"
        assert cap.params == {}
    
    def test_provider_spec(self):
        """Test ProviderSpec DTO."""
        spec = ProviderSpec(
            name="ibkr",
            module="market_data_ibkr",
            entry="IBKRProvider",
            capabilities=[Capability(name="historical_bars")],
        )
        assert spec.name == "ibkr"
        assert spec.module == "market_data_ibkr"
        assert len(spec.capabilities) == 1
    
    def test_provider_spec_no_capabilities(self):
        """Test ProviderSpec without capabilities."""
        spec = ProviderSpec(
            name="simple",
            module="simple.provider",
            entry="SimpleProvider"
        )
        assert spec.name == "simple"
        assert spec.capabilities == []
    
    def test_sink_spec(self):
        """Test SinkSpec DTO."""
        spec = SinkSpec(
            name="bars_sink",
            module="market_data_store.sinks",
            entry="BarsSink",
            kind="bars",
        )
        assert spec.kind == "bars"
        assert spec.name == "bars_sink"
    
    def test_provider_spec_json_roundtrip(self):
        """Test ProviderSpec JSON serialization."""
        spec = ProviderSpec(
            name="test",
            module="test.mod",
            entry="TestProvider",
            capabilities=[Capability(name="test_cap")]
        )
        json_data = spec.model_dump_json()
        restored = ProviderSpec.model_validate_json(json_data)
        assert restored.name == spec.name
        assert len(restored.capabilities) == 1

