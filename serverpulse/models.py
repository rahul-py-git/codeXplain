"""Typed response shapes used by the ServerPulse HTTP API."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response returned by the lightweight health endpoint."""

    status: str = "ok"
    service: str = "ServerPulse"


class MetricsResponse(BaseModel):
    """A point-in-time snapshot of the machine running ServerPulse."""

    hostname: str
    cpu_percent: float = Field(ge=0, le=100)
    memory_percent: float = Field(ge=0, le=100)
    memory_available_mb: float = Field(ge=0)
    disk_percent: float = Field(ge=0, le=100)
    disk_free_gb: float = Field(ge=0)
    uptime_seconds: float = Field(ge=0)


class AlertItem(BaseModel):
    """One threshold warning for a metric."""

    metric: str
    value: float
    threshold: float
    severity: str = "warning"
    message: str


class AlertsResponse(BaseModel):
    """All alerts detected in one metric snapshot."""

    alerts: list[AlertItem]
    alert_count: int
