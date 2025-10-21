"""
Metrics collector for request tracking and statistics.
"""

import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Lock
from typing import Any


@dataclass
class RequestRecord:
    """Single request record."""

    timestamp: datetime
    provider: str
    method: str
    path: str
    status: int
    duration: float  # seconds


class MetricsCollector:
    """
    Thread-safe metrics collector for request tracking.

    Stores recent requests in memory and provides aggregated statistics.
    """

    def __init__(self, max_history: int = 10000):
        """
        Initialize metrics collector.

        Args:
            max_history: Maximum number of requests to keep in history
        """
        self._requests: deque[RequestRecord] = deque(maxlen=max_history)
        self._lock = Lock()

    def record_request(
        self,
        provider: str,
        method: str,
        path: str,
        status: int,
        duration: float,
    ) -> None:
        """
        Record a single request.

        Args:
            provider: Provider name that handled the request
            method: HTTP method (GET, POST, etc.)
            path: Request path
            status: HTTP status code
            duration: Request duration in seconds
        """
        with self._lock:
            self._requests.append(
                RequestRecord(
                    timestamp=datetime.utcnow(),
                    provider=provider,
                    method=method,
                    path=path,
                    status=status,
                    duration=duration,
                )
            )

    @property
    def total_requests(self) -> int:
        """Total number of requests recorded."""
        return len(self._requests)

    @property
    def success_rate(self) -> float:
        """Success rate (2xx status codes) as percentage."""
        if not self._requests:
            return 0.0
        with self._lock:
            success = sum(1 for r in self._requests if 200 <= r.status < 300)
            return (success / len(self._requests)) * 100

    @property
    def avg_latency_ms(self) -> float:
        """Average latency in milliseconds."""
        if not self._requests:
            return 0.0
        with self._lock:
            total_duration = sum(r.duration for r in self._requests)
            return (total_duration / len(self._requests)) * 1000

    def get_latest(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get latest N requests.

        Args:
            limit: Number of recent requests to return

        Returns:
            List of request dictionaries
        """
        with self._lock:
            recent = list(self._requests)[-limit:]
            return [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "provider": r.provider,
                    "method": r.method,
                    "path": r.path,
                    "status": r.status,
                    "duration_ms": r.duration * 1000,
                }
                for r in recent
            ]

    def get_requests_timeline(self, hours: int = 1, interval_minutes: int = 1) -> list[dict[str, Any]]:
        """
        Get request count timeline aggregated by time intervals.

        Args:
            hours: Number of hours to look back
            interval_minutes: Aggregation interval in minutes

        Returns:
            List of time buckets with request counts
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        interval_seconds = interval_minutes * 60

        # Create time buckets
        buckets: dict[int, int] = {}
        with self._lock:
            for request in self._requests:
                if request.timestamp >= cutoff:
                    # Round timestamp to interval
                    bucket_key = int(request.timestamp.timestamp() / interval_seconds)
                    buckets[bucket_key] = buckets.get(bucket_key, 0) + 1

        # Convert to sorted list
        result = []
        for bucket_key in sorted(buckets.keys()):
            timestamp = datetime.fromtimestamp(bucket_key * interval_seconds)
            result.append(
                {
                    "time": timestamp.strftime("%H:%M"),
                    "timestamp": timestamp.isoformat(),
                    "count": buckets[bucket_key],
                }
            )

        return result

    def get_provider_stats(self) -> list[dict[str, Any]]:
        """
        Get statistics per provider.

        Returns:
            List of provider statistics
        """
        provider_data: dict[str, dict[str, Any]] = {}

        with self._lock:
            for request in self._requests:
                if request.provider not in provider_data:
                    provider_data[request.provider] = {
                        "name": request.provider,
                        "total": 0,
                        "success": 0,
                        "error": 0,
                        "total_duration": 0.0,
                    }

                data = provider_data[request.provider]
                data["total"] += 1
                if 200 <= request.status < 300:
                    data["success"] += 1
                else:
                    data["error"] += 1
                data["total_duration"] += request.duration

        # Calculate derived metrics
        result = []
        for provider, data in provider_data.items():
            result.append(
                {
                    "name": provider,
                    "total_requests": data["total"],
                    "success_count": data["success"],
                    "error_count": data["error"],
                    "success_rate": (data["success"] / data["total"]) * 100 if data["total"] > 0 else 0,
                    "avg_latency_ms": (data["total_duration"] / data["total"]) * 1000
                    if data["total"] > 0
                    else 0,
                }
            )

        return result

    def get_latency_stats(self) -> dict[str, float]:
        """
        Get latency percentile statistics.

        Returns:
            Dictionary with p50, p95, p99 latencies in milliseconds
        """
        if not self._requests:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

        with self._lock:
            latencies = sorted([r.duration * 1000 for r in self._requests])

        total = len(latencies)
        return {
            "p50": latencies[int(total * 0.50)] if total > 0 else 0.0,
            "p95": latencies[int(total * 0.95)] if total > 1 else latencies[0] if total == 1 else 0.0,
            "p99": latencies[int(total * 0.99)] if total > 2 else latencies[-1] if total > 0 else 0.0,
        }

    def get_requests_per_minute(self, minutes: int = 60) -> list[int]:
        """
        Get requests per minute for the last N minutes.

        Args:
            minutes: Number of minutes to look back

        Returns:
            List of request counts, one per minute
        """
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        minute_buckets: dict[int, int] = {}

        with self._lock:
            for request in self._requests:
                if request.timestamp >= cutoff:
                    # Round to minute
                    minute_key = int(request.timestamp.timestamp() / 60)
                    minute_buckets[minute_key] = minute_buckets.get(minute_key, 0) + 1

        # Fill in missing minutes with 0
        if not minute_buckets:
            return [0] * minutes

        min_minute = min(minute_buckets.keys())
        max_minute = max(minute_buckets.keys())

        result = []
        for minute_key in range(min_minute, max_minute + 1):
            result.append(minute_buckets.get(minute_key, 0))

        # Pad or trim to requested length
        if len(result) < minutes:
            result = [0] * (minutes - len(result)) + result
        elif len(result) > minutes:
            result = result[-minutes:]

        return result


# Global singleton instance
metrics_collector = MetricsCollector()
