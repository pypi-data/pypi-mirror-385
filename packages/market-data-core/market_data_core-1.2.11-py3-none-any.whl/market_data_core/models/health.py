from datetime import datetime

from pydantic import BaseModel, Field


class Health(BaseModel):
    """Health status with connection statistics."""

    status: str = "ok"
    version: str = "0.1.0"
    ibkr_connected: bool = Field(False, description="IBKR connection status")
    gateway_type: str | None = Field(None, description="Gateway type (TWS/Gateway)")
    gateway_port: int | None = Field(None, description="Gateway port")
    last_connect_ts: datetime | None = Field(None, description="Last connection timestamp")
    reconnects_total: int = Field(0, description="Total reconnections")
    subscriptions_active: int = Field(0, description="Active subscriptions")
    errors_total: int = Field(0, description="Total errors")
