"""
Performance monitoring per enterprise observability
"""
import time
import statistics
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Metriche performance aggregate"""

    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0

    # Timing metrics (in milliseconds)
    request_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    db_write_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    parse_times: deque = field(default_factory=lambda: deque(maxlen=1000))

    # Throughput
    start_time: float = field(default_factory=time.time)

    # Errors
    error_counts: Dict[str, int] = field(default_factory=dict)

    # Memory (bytes)
    memory_samples: deque = field(default_factory=lambda: deque(maxlen=100))

    @property
    def success_rate(self) -> float:
        """Calcola success rate percentuale"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def avg_request_time(self) -> float:
        """Tempo medio richiesta in ms"""
        if not self.request_times:
            return 0.0
        return statistics.mean(self.request_times)

    @property
    def p95_request_time(self) -> float:
        """95th percentile tempo richiesta"""
        if not self.request_times:
            return 0.0
        sorted_times = sorted(self.request_times)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[idx] if idx < len(sorted_times) else sorted_times[-1]

    @property
    def p99_request_time(self) -> float:
        """99th percentile tempo richiesta"""
        if not self.request_times:
            return 0.0
        sorted_times = sorted(self.request_times)
        idx = int(len(sorted_times) * 0.99)
        return sorted_times[idx] if idx < len(sorted_times) else sorted_times[-1]

    @property
    def requests_per_second(self) -> float:
        """Throughput in richieste/secondo"""
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0.0
        return self.total_requests / elapsed

    @property
    def avg_memory_mb(self) -> float:
        """Memoria media in MB"""
        if not self.memory_samples:
            return 0.0
        return statistics.mean(self.memory_samples) / (1024 * 1024)

    def to_dict(self) -> Dict[str, Any]:
        """Esporta metriche come dict"""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate_pct': round(self.success_rate, 2),
            'avg_request_time_ms': round(self.avg_request_time, 2),
            'p95_request_time_ms': round(self.p95_request_time, 2),
            'p99_request_time_ms': round(self.p99_request_time, 2),
            'requests_per_second': round(self.requests_per_second, 2),
            'avg_memory_mb': round(self.avg_memory_mb, 2),
            'error_counts': dict(self.error_counts),
            'uptime_seconds': round(time.time() - self.start_time, 2)
        }


class PerformanceMonitor:
    """
    Monitor performance enterprise-grade con metrics collection

    Features:
    - Request timing tracking
    - Database operation timing
    - Parse timing
    - Memory monitoring
    - Error tracking
    - Percentile calculations
    - Export Prometheus-style metrics
    """

    def __init__(self, enable_memory_tracking: bool = True):
        """
        Inizializza monitor

        Args:
            enable_memory_tracking: Abilita tracking memoria (default: True)
        """
        self.metrics = PerformanceMetrics()
        self.enable_memory_tracking = enable_memory_tracking

        # Per context managers
        self._current_operation: Optional[str] = None
        self._operation_start: float = 0.0

    def track_request(self, duration_ms: float, success: bool = True) -> None:
        """
        Traccia richiesta HTTP

        Args:
            duration_ms: Durata in millisecondi
            success: Se richiesta ha avuto successo
        """
        self.metrics.total_requests += 1
        self.metrics.request_times.append(duration_ms)

        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1

    def track_db_write(self, duration_ms: float) -> None:
        """Traccia scrittura database"""
        self.metrics.db_write_times.append(duration_ms)

    def track_parse(self, duration_ms: float) -> None:
        """Traccia parsing HTML"""
        self.metrics.parse_times.append(duration_ms)

    def track_error(self, error_type: str) -> None:
        """
        Traccia errore per tipo

        Args:
            error_type: Tipo errore (es: "TimeoutError", "HTTPError")
        """
        if error_type not in self.metrics.error_counts:
            self.metrics.error_counts[error_type] = 0
        self.metrics.error_counts[error_type] += 1

    def track_memory(self) -> None:
        """Traccia utilizzo memoria corrente"""
        if not self.enable_memory_tracking:
            return

        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_bytes = process.memory_info().rss
            self.metrics.memory_samples.append(memory_bytes)
        except ImportError:
            # psutil non installato, skip
            pass
        except Exception as e:
            logger.debug(f"Error tracking memory: {e}")

    def start_operation(self, operation_name: str) -> None:
        """
        Inizia tracking operazione

        Args:
            operation_name: Nome operazione (es: "request", "db_write")
        """
        self._current_operation = operation_name
        self._operation_start = time.time()

    def end_operation(self, success: bool = True) -> float:
        """
        Termina tracking operazione

        Args:
            success: Se operazione ha avuto successo

        Returns:
            Durata operazione in millisecondi
        """
        if not self._current_operation:
            return 0.0

        duration_ms = (time.time() - self._operation_start) * 1000

        # Track based on operation type
        if self._current_operation == "request":
            self.track_request(duration_ms, success)
        elif self._current_operation == "db_write":
            self.track_db_write(duration_ms)
        elif self._current_operation == "parse":
            self.track_parse(duration_ms)

        self._current_operation = None
        return duration_ms

    def get_summary(self) -> Dict[str, Any]:
        """Ritorna summary completo metriche"""
        summary = self.metrics.to_dict()

        # Aggiungi database metrics se disponibili
        if self.metrics.db_write_times:
            summary['avg_db_write_ms'] = round(
                statistics.mean(self.metrics.db_write_times), 2
            )

        # Aggiungi parse metrics se disponibili
        if self.metrics.parse_times:
            summary['avg_parse_ms'] = round(
                statistics.mean(self.metrics.parse_times), 2
            )

        return summary

    def log_summary(self, level: int = logging.INFO) -> None:
        """Log summary metriche"""
        summary = self.get_summary()

        logger.log(level, "📊 Performance Summary:")
        logger.log(level, f"  Total requests: {summary['total_requests']}")
        logger.log(level, f"  Success rate: {summary['success_rate_pct']}%")
        logger.log(level, f"  Avg request time: {summary['avg_request_time_ms']}ms")
        logger.log(level, f"  P95 request time: {summary['p95_request_time_ms']}ms")
        logger.log(level, f"  P99 request time: {summary['p99_request_time_ms']}ms")
        logger.log(level, f"  Throughput: {summary['requests_per_second']} req/s")

        if summary.get('avg_memory_mb'):
            logger.log(level, f"  Avg memory: {summary['avg_memory_mb']} MB")

        if summary.get('error_counts'):
            logger.log(level, f"  Errors: {summary['error_counts']}")

    def export_prometheus(self) -> str:
        """
        Esporta metriche in formato Prometheus

        Returns:
            String con metriche formato Prometheus
        """
        summary = self.get_summary()
        lines = [
            f"# HELP pyprestascan_requests_total Total number of requests",
            f"# TYPE pyprestascan_requests_total counter",
            f"pyprestascan_requests_total {summary['total_requests']}",
            "",
            f"# HELP pyprestascan_requests_success Success requests",
            f"# TYPE pyprestascan_requests_success counter",
            f"pyprestascan_requests_success {summary['successful_requests']}",
            "",
            f"# HELP pyprestascan_request_duration_ms Request duration",
            f"# TYPE pyprestascan_request_duration_ms gauge",
            f"pyprestascan_request_duration_ms{{quantile=\"0.5\"}} {summary['avg_request_time_ms']}",
            f"pyprestascan_request_duration_ms{{quantile=\"0.95\"}} {summary['p95_request_time_ms']}",
            f"pyprestascan_request_duration_ms{{quantile=\"0.99\"}} {summary['p99_request_time_ms']}",
            "",
            f"# HELP pyprestascan_throughput_rps Requests per second",
            f"# TYPE pyprestascan_throughput_rps gauge",
            f"pyprestascan_throughput_rps {summary['requests_per_second']}",
            ""
        ]

        return "\n".join(lines)


# Context manager per timing facile
class TimedOperation:
    """Context manager per timing automatico operazioni"""

    def __init__(self, monitor: PerformanceMonitor, operation_name: str):
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = 0.0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        success = exc_type is None

        if self.operation_name == "request":
            self.monitor.track_request(duration_ms, success)
        elif self.operation_name == "db_write":
            self.monitor.track_db_write(duration_ms)
        elif self.operation_name == "parse":
            self.monitor.track_parse(duration_ms)


# Export
__all__ = [
    'PerformanceMetrics',
    'PerformanceMonitor',
    'TimedOperation'
]
