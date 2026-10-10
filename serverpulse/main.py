"""HTTP entry point for ServerPulse."""

from fastapi import FastAPI

from alerts import evaluate_alerts
from collector import collect_metrics
from models import AlertsResponse, HealthResponse, MetricsResponse


app = FastAPI(
    title="ServerPulse",
    description="A learning API for host resource monitoring and threshold alerts.",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse, tags=["service"])
def health_check() -> HealthResponse:
    """Confirm that the API process can answer requests."""

    return HealthResponse()


@app.get("/metrics", response_model=MetricsResponse, tags=["monitoring"])
def get_metrics() -> MetricsResponse:
    """Return the latest resource metrics for this host."""

    return collect_metrics()


@app.get("/alerts", response_model=AlertsResponse, tags=["monitoring"])
def get_alerts() -> AlertsResponse:
    """Collect a fresh snapshot and evaluate configured thresholds."""

    alerts = evaluate_alerts(collect_metrics())
    return AlertsResponse(alerts=alerts, alert_count=len(alerts))
