"""Tests for v1.1.0 settings additions."""

from market_data_core.settings import (
    CompositeSettings,
    ProviderConfig,
    SinkConfig,
    WiringPlan,
)


class TestCompositeSettings:
    """Tests for CompositeSettings."""
    
    def test_composite_settings_creation(self):
        """Test CompositeSettings composition."""
        settings = CompositeSettings(
            pipeline={"batch_size": 500},
            store={"pool_max": 10},
            orchestrator={"mode": "dag"},
        )
        assert settings.pipeline["batch_size"] == 500
        assert settings.store["pool_max"] == 10
    
    def test_composite_settings_empty(self):
        """Test CompositeSettings with empty sections."""
        settings = CompositeSettings()
        assert settings.pipeline == {}
        assert settings.store == {}


class TestProviderSinkConfig:
    """Tests for ProviderConfig and SinkConfig."""
    
    def test_provider_config(self):
        """Test ProviderConfig."""
        config = ProviderConfig(name="ibkr", params={"host": "127.0.0.1"})
        assert config.name == "ibkr"
        assert config.params["host"] == "127.0.0.1"
    
    def test_sink_config(self):
        """Test SinkConfig."""
        config = SinkConfig(name="bars_sink", params={"db_url": "postgresql://..."})
        assert config.name == "bars_sink"


class TestWiringPlan:
    """Tests for WiringPlan."""
    
    def test_wiring_plan_creation(self):
        """Test WiringPlan composition."""
        plan = WiringPlan(
            providers=[ProviderConfig(name="ibkr")],
            sinks=[SinkConfig(name="bars_sink")],
        )
        assert len(plan.providers) == 1
        assert len(plan.sinks) == 1
        assert plan.providers[0].name == "ibkr"
    
    def test_wiring_plan_empty(self):
        """Test WiringPlan with no providers/sinks."""
        plan = WiringPlan()
        assert plan.providers == []
        assert plan.sinks == []
    
    def test_wiring_plan_json_roundtrip(self):
        """Test WiringPlan JSON round-trip."""
        plan = WiringPlan(
            providers=[ProviderConfig(name="test", params={"key": "value"})],
        )
        json_data = plan.model_dump_json()
        restored = WiringPlan.model_validate_json(json_data)
        assert restored.providers[0].name == "test"
        assert restored.providers[0].params["key"] == "value"

