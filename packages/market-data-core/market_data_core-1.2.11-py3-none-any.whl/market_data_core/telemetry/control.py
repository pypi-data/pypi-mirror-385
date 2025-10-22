"""Control and audit contracts."""

from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field


class ControlAction(str, Enum):
    """Control actions for runtime management."""
    
    pause = "pause"      # Pause data ingestion
    resume = "resume"    # Resume data ingestion
    reload = "reload"    # Reload configuration


class ControlResult(BaseModel):
    """Result of a control action.
    
    Example:
        ```python
        result = ControlResult(status="ok", detail="Pipeline paused successfully")
        ```
    """
    
    status: Literal["ok", "error"] = Field(..., description="Result status")
    detail: str | None = Field(default=None, description="Optional detail message")


class AuditEnvelope(BaseModel):
    """Audit envelope for control actions.
    
    Tracks who performed what action and the result.
    
    Example:
        ```python
        audit = AuditEnvelope(
            actor="admin@example.com",
            role="admin",
            action=ControlAction.pause,
            result=ControlResult(status="ok"),
            ts=time.time()
        )
        ```
    """
    
    actor: str = Field(..., description="User or service performing action")
    role: str = Field(..., description="Role of actor (admin, operator, system)")
    action: ControlAction = Field(..., description="Control action performed")
    result: ControlResult = Field(..., description="Action result")
    ts: float = Field(..., description="Unix epoch seconds")

