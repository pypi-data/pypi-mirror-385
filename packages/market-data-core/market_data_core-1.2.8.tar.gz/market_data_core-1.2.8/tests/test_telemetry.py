"""Tests for telemetry contracts."""

import time
import pytest
from pydantic import ValidationError

from market_data_core.telemetry import (
    BackpressureLevel,
    FeedbackEvent,
    RateAdjustment,
    HealthState,
    HealthComponent,
    HealthStatus,
    Probe,
    MetricPoint,
    MetricSeries,
    Labels,
    ControlAction,
    ControlResult,
    AuditEnvelope,
)


class TestBackpressure:
    """Tests for backpressure contracts."""
    
    def test_backpressure_level_enum(self):
        """Test BackpressureLevel enum values."""
        assert BackpressureLevel.ok == "ok"
        assert BackpressureLevel.soft == "soft"
        assert BackpressureLevel.hard == "hard"
    
    def test_feedback_event_creation(self):
        """Test FeedbackEvent model creation and validation."""
        event = FeedbackEvent(
            coordinator_id="test_coordinator",
            queue_size=800,
            capacity=1000,
            level=BackpressureLevel.soft,
            source="store",
            ts=time.time(),
        )
        assert event.coordinator_id == "test_coordinator"
        assert event.level == BackpressureLevel.soft
        assert event.queue_size == 800
    
    def test_feedback_event_validation_negative_queue_size(self):
        """Test FeedbackEvent validation rejects negative queue_size."""
        with pytest.raises(ValidationError):
            FeedbackEvent(
                coordinator_id="test",
                queue_size=-1,
                capacity=1000,
                level=BackpressureLevel.ok,
                ts=time.time(),
            )
    
    def test_feedback_event_validation_zero_capacity(self):
        """Test FeedbackEvent validation rejects zero capacity."""
        with pytest.raises(ValidationError):
            FeedbackEvent(
                coordinator_id="test",
                queue_size=0,
                capacity=0,
                level=BackpressureLevel.ok,
                ts=time.time(),
            )
    
    def test_rate_adjustment(self):
        """Test RateAdjustment model."""
        adj = RateAdjustment(
            provider="ibkr",
            scale=0.7,
            reason=BackpressureLevel.soft,
            ts=time.time(),
        )
        assert 0.0 <= adj.scale <= 1.0
        assert adj.provider == "ibkr"
    
    def test_rate_adjustment_scale_bounds(self):
        """Test RateAdjustment scale must be between 0 and 1."""
        with pytest.raises(ValidationError):
            RateAdjustment(
                provider="ibkr",
                scale=1.5,  # Invalid
                reason=BackpressureLevel.hard,
                ts=time.time(),
            )
    
    def test_feedback_event_json_roundtrip(self):
        """Test FeedbackEvent JSON serialization/deserialization."""
        event = FeedbackEvent(
            coordinator_id="test",
            queue_size=500,
            capacity=1000,
            level=BackpressureLevel.ok,
            ts=time.time(),
        )
        json_data = event.model_dump_json()
        restored = FeedbackEvent.model_validate_json(json_data)
        assert restored.coordinator_id == event.coordinator_id


class TestHealth:
    """Tests for health contracts."""
    
    def test_health_component(self):
        """Test HealthComponent creation."""
        component = HealthComponent(
            name="db",
            state="healthy",
            details={"connected": "true"}
        )
        assert component.name == "db"
        assert component.state == "healthy"
    
    def test_health_status_composition(self):
        """Test HealthStatus composition."""
        status = HealthStatus(
            service="test-service",
            state="healthy",
            components=[
                HealthComponent(name="db", state="healthy"),
                HealthComponent(name="cache", state="degraded", details={"reason": "high latency"}),
            ],
            version="1.0.0",
            ts=time.time(),
        )
        assert len(status.components) == 2
        assert status.components[1].state == "degraded"
    
    def test_probe(self):
        """Test Probe model."""
        probe = Probe(
            probe_type="readiness",
            passed=True,
            message="All systems ready"
        )
        assert probe.probe_type == "readiness"
        assert probe.passed is True


class TestMetrics:
    """Tests for metrics contracts."""
    
    def test_labels(self):
        """Test Labels model."""
        labels = Labels(values={"symbol": "AAPL", "exchange": "NASDAQ"})
        assert labels.values["symbol"] == "AAPL"
    
    def test_metric_point(self):
        """Test MetricPoint with labels."""
        point = MetricPoint(
            name="requests_total",
            value=1500.0,
            labels=Labels(values={"method": "GET", "status": "200"}),
            ts=time.time(),
        )
        assert point.name == "requests_total"
        assert point.labels.values["method"] == "GET"
    
    def test_metric_series(self):
        """Test MetricSeries."""
        ts = time.time()
        series = MetricSeries(
            name="latency_ms",
            points=[
                MetricPoint(name="latency_ms", value=12.0, ts=ts),
                MetricPoint(name="latency_ms", value=15.0, ts=ts + 1),
            ]
        )
        assert len(series.points) == 2


class TestControl:
    """Tests for control contracts."""
    
    def test_control_action_enum(self):
        """Test ControlAction enum."""
        assert ControlAction.pause == "pause"
        assert ControlAction.resume == "resume"
        assert ControlAction.reload == "reload"
    
    def test_control_result(self):
        """Test ControlResult."""
        result = ControlResult(status="ok", detail="Success")
        assert result.status == "ok"
    
    def test_audit_envelope(self):
        """Test AuditEnvelope for control actions."""
        audit = AuditEnvelope(
            actor="admin@test.com",
            role="admin",
            action=ControlAction.pause,
            result=ControlResult(status="ok", detail="Success"),
            ts=time.time(),
        )
        assert audit.action == ControlAction.pause
        assert audit.result.status == "ok"
        assert audit.actor == "admin@test.com"

