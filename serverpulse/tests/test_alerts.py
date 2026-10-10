"""Unit tests for threshold alert evaluation."""

from alerts import evaluate_alerts
from models import MetricsResponse


def make_metrics(
    cpu: float = 10.0,
    memory: float = 20.0,
    disk: float = 30.0,
) -> MetricsResponse:
    """Create a valid sample without reading the actual host."""

    return MetricsResponse(
        hostname="test-host",
        cpu_percent=cpu,
        memory_percent=memory,
        memory_available_mb=1024.0,
        disk_percent=disk,
        disk_free_gb=10.0,
        uptime_seconds=100.0,
    )


def test_no_alerts_when_metrics_are_below_thresholds() -> None:
    alerts = evaluate_alerts(make_metrics())
    assert alerts == []


def test_cpu_alert_at_threshold() -> None:
    alerts = evaluate_alerts(make_metrics(cpu=85.0))
    assert len(alerts) == 1
    assert alerts[0].metric == "cpu_percent"
    assert alerts[0].threshold == 85.0


def test_multiple_alerts_can_be_returned() -> None:
    alerts = evaluate_alerts(make_metrics(cpu=95.0, memory=90.0, disk=99.0))
    assert {alert.metric for alert in alerts} == {
        "cpu_percent",
        "memory_percent",
        "disk_percent",
    }
    assert len(alerts) == 3
