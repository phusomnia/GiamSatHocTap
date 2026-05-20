import time
from typing import Dict, Optional, Callable, Any
from functools import wraps
from contextlib import contextmanager
from src.SharedKernel.base.Logger import get_logger

logger = get_logger(__name__)

class Metrics:
    """Metrics class for tracking execution time, counters, and custom metrics."""
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize Metrics instance.
        
        Args:
            name: Optional name for this metrics instance
        """
        self.name = name or "metrics"
        self._start_time: float = time.perf_counter()
        self._stages: Dict[str, float] = {}
        self._stage_timestamps: Dict[str, float] = {}
        self._counters: Dict[str, int] = {}
        self._custom_metrics: Dict[str, float] = {}
        self._logger = get_logger(__name__)
    
    def stage(self, name: str) -> None:
        """
        Mark a timestamp for a specific stage.
        
        Args:
            name: Name of the stage to mark
        """
        timestamp = time.perf_counter()
        self._stage_timestamps[name] = timestamp
        self._stages[name] = timestamp - self._start_time
    
    def record(self, name: str, value: float) -> None:
        """
        Record a custom metric value.
        
        Args:
            name: Name of the metric
            value: Value to record
        """
        self._custom_metrics[name] = value
    
    def increment(self, name: str, value: int = 1) -> None:
        """
        Increment a counter.
        
        Args:
            name: Name of the counter
            value: Amount to increment (default: 1)
        """
        if name not in self._counters:
            self._counters[name] = 0
        self._counters[name] += value
    
    def get_timing(self, stage_name: str) -> Optional[float]:
        """
        Get elapsed time for a specific stage.
        
        Args:
            stage_name: Name of the stage
            
        Returns:
            Elapsed time in seconds, or None if stage not found
        """
        if stage_name not in self._stages:
            return None
        
        # If stage has a timestamp, calculate time from start to that stage
        if stage_name in self._stage_timestamps:
            return self._stage_timestamps[stage_name] - self._start_time
        
        return self._stages[stage_name]
    
    def total_timing(self) -> float:
        """
        Get total elapsed time since creation.
        
        Returns:
            Total elapsed time in seconds
        """
        return time.perf_counter() - self._start_time
    
    def log_summary(self) -> None:
        """Log all metrics using the custom logger."""
        self._logger.metric(f"=== Metrics Summary: {self.name} ===")
        
        # Total timing
        total = self.total_timing()
        self._logger.metric(f"Total time: {total:.4f}s")
        
        # Stages
        if self._stages:
            self._logger.metric("Stages:")
            for stage_name, timing in sorted(self._stages.items(), key=lambda x: x[1]):
                self._logger.metric(f"  - {stage_name}: {timing:.4f}s")
        
        # Counters
        if self._counters:
            self._logger.metric("Counters:")
            for counter_name, count in sorted(self._counters.items()):
                self._logger.metric(f"  - {counter_name}: {count}")
        
        # Custom metrics
        if self._custom_metrics:
            self._logger.metric("Custom metrics:")
            for metric_name, value in sorted(self._custom_metrics.items()):
                self._logger.metric(f"  - {metric_name}: {value}")
        
        self._logger.metric(f"=== End Metrics Summary: {self.name} ===")
    
    def _to_dict(self) -> Dict[str, Any]:
        """
        Convert all metrics to dictionary format.
        
        Returns:
            Dictionary containing all metrics
        """
        return {
            "name": self.name,
            "total_time": self.total_timing(),
            "stages": dict(self._stages),
            "counters": dict(self._counters),
            "custom_metrics": dict(self._custom_metrics)
        }
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically log summary."""
        self.log_summary()
        return False
    
    @staticmethod
    def time_function(func: Optional[Callable] = None, *, name: Optional[str] = None) -> Any:
        """
        Decorator to time function execution.
        
        Args:
            func: Function to decorate
            name: Optional name for the metrics instance
            
        Returns:
            Decorated function or decorator
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def wrapper(*args, **kwargs):
                metrics_name = name or f.__name__
                with Metrics(name=metrics_name) as m:
                    m.stage("start")
                    result = f(*args, **kwargs)
                    m.stage("end")
                return result
            return wrapper
        
        if func is None:
            return decorator
        return decorator(func)


@contextmanager
def measure_time(name: Optional[str] = None) -> Metrics:
    """
    Context manager for measuring execution time.
    
    Args:
        name: Optional name for the metrics instance
        
    Yields:
        Metrics instance
    """
    metrics = Metrics(name=name)
    metrics.stage("start")
    try:
        yield metrics
    finally:
        metrics.stage("end")
        metrics.log_summary()
