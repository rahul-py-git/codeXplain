"""Read a point-in-time set of host metrics using psutil."""

import socket
import time

import psutil

from models import MetricsResponse


# Capture the monotonic clock when this module is loaded. Unlike wall-clock
# time, monotonic time is not affected by changes to the system clock.
_START_TIME = time.monotonic()


def collect_metrics() -> MetricsResponse:
    """Collect CPU, memory, disk, hostname, and process uptime.

    This reports the machine running the API, not a remote machine.
    """

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/" if psutil.POSIX else "C:\\")

    # interval=None returns a recent CPU utilization value without deliberately
    # blocking this request for a full sampling interval.
    cpu_percent = psutil.cpu_percent(interval=None)

    return MetricsResponse(
        hostname=socket.gethostname(),
        cpu_percent=cpu_percent,
        memory_percent=memory.percent,
        memory_available_mb=memory.available / (1024 * 1024),
        disk_percent=disk.percent,
        disk_free_gb=disk.free / (1024 ** 3),
        uptime_seconds=max(0.0, time.monotonic() - _START_TIME),
    )
