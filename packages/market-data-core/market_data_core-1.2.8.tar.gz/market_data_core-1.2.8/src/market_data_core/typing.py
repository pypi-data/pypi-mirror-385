"""Shared type aliases and literals."""

from typing import Literal


# Health states
HealthState = Literal["healthy", "degraded", "unhealthy"]

# Control states
ControlStatus = Literal["ok", "error"]

# Backpressure levels
BackpressureLevelLiteral = Literal["ok", "soft", "hard"]

# Node roles
NodeRoleLiteral = Literal["orchestrator", "pipeline", "store"]

# Probe types
ProbeType = Literal["liveness", "readiness"]


__all__ = [
    "HealthState",
    "ControlStatus",
    "BackpressureLevelLiteral",
    "NodeRoleLiteral",
    "ProbeType",
]

