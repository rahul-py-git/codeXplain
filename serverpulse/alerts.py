"""Turn a metrics snapshot into human-readable threshold alerts."""

from models import AlertItem, MetricsResponse


# These are teaching defaults. Tune them for the workload before production use.
CPU_THRESHOLD = 85.0
MEMORY_THRESHOLD = 85.0
DISK_THRESHOLD = 90.0


def evaluate_alerts(metrics: MetricsResponse) -> list[AlertItem]:
    """Return an alert for each metric at or above its threshold."""

    alerts: list[AlertItem] = []

    checks = [
        ("cpu_percent", metrics.cpu_percent, CPU_THRESHOLD, "CPU usage"),
        ("memory_percent", metrics.memory_percent, MEMORY_THRESHOLD, "Memory usage"),
        ("disk_percent", metrics.disk_percent, DISK_THRESHOLD, "Disk usage"),
    ]

    for metric_name, value, threshold, label in checks:
        if value >= threshold:
            alerts.append(
                AlertItem(
                    metric=metric_name,
                    value=value,
                    threshold=threshold,
                    severity="warning",
                    message=f"{label} is {value:.1f}% (threshold: {threshold:.1f}%).",
                )
            )

    return alerts
