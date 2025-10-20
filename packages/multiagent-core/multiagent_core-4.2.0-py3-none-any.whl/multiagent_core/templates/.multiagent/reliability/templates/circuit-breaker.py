"""
Circuit Breaker Implementation
Purpose: Prevent cascading failures by failing fast when service is unhealthy
States: CLOSED -> OPEN -> HALF_OPEN -> CLOSED
"""

import time
import threading
from enum import Enum
from typing import Callable, Any, Optional
from functools import wraps
from dataclasses import dataclass


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Number of failures to open circuit
    timeout_ms: int = 30000  # Request timeout in milliseconds
    reset_timeout_ms: int = 60000  # Time before trying half-open
    success_threshold: int = 2  # Successes needed to close from half-open
    minimum_requests: int = 10  # Min requests before evaluating


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Usage:
        circuit_breaker = CircuitBreaker(
            name="external_api",
            failure_threshold=5,
            timeout_ms=30000,
            reset_timeout_ms=60000
        )

        @circuit_breaker
        def call_external_api():
            return requests.get("https://api.example.com/data")
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout_ms: int = 30000,
        reset_timeout_ms: int = 60000,
        success_threshold: int = 2,
        minimum_requests: int = 10,
    ):
        self.name = name
        self.config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            timeout_ms=timeout_ms,
            reset_timeout_ms=reset_timeout_ms,
            success_threshold=success_threshold,
            minimum_requests=minimum_requests,
        )

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.request_count = 0
        self.last_failure_time = None
        self.last_state_change = time.time()

        self.lock = threading.Lock()

        # Metrics
        self.metrics = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "rejected_calls": 0,
            "state_changes": 0,
        }

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return False

        elapsed_ms = (time.time() - self.last_failure_time) * 1000
        return elapsed_ms >= self.config.reset_timeout_ms

    def _record_success(self):
        """Record successful request."""
        with self.lock:
            self.success_count += 1
            self.failure_count = 0
            self.metrics["successful_calls"] += 1

            if self.state == CircuitState.HALF_OPEN:
                if self.success_count >= self.config.success_threshold:
                    self._transition_to(CircuitState.CLOSED)

    def _record_failure(self):
        """Record failed request."""
        with self.lock:
            self.failure_count += 1
            self.success_count = 0
            self.last_failure_time = time.time()
            self.metrics["failed_calls"] += 1

            if self.state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)
            elif self.state == CircuitState.CLOSED:
                if (
                    self.request_count >= self.config.minimum_requests
                    and self.failure_count >= self.config.failure_threshold
                ):
                    self._transition_to(CircuitState.OPEN)

    def _transition_to(self, new_state: CircuitState):
        """Transition to a new state."""
        old_state = self.state
        self.state = new_state
        self.last_state_change = time.time()
        self.failure_count = 0
        self.success_count = 0
        self.metrics["state_changes"] += 1

        print(
            f"[CircuitBreaker:{self.name}] State transition: {old_state.value} -> {new_state.value}"
        )

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        """
        with self.lock:
            self.metrics["total_calls"] += 1
            self.request_count += 1

            # OPEN state: Fail fast
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to(CircuitState.HALF_OPEN)
                else:
                    self.metrics["rejected_calls"] += 1
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is OPEN"
                    )

        # Execute the function
        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            raise e

    def __call__(self, func: Callable) -> Callable:
        """Decorator interface."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)

        return wrapper

    def get_state(self) -> CircuitState:
        """Get current circuit state."""
        return self.state

    def get_metrics(self) -> dict:
        """Get circuit breaker metrics."""
        with self.lock:
            total_calls = self.metrics["total_calls"]
            success_rate = (
                self.metrics["successful_calls"] / total_calls if total_calls > 0 else 0
            )

            return {
                **self.metrics,
                "current_state": self.state.value,
                "failure_count": self.failure_count,
                "success_rate": success_rate,
                "time_in_current_state": time.time() - self.last_state_change,
            }

    def reset(self):
        """Manually reset circuit breaker to CLOSED state."""
        with self.lock:
            self._transition_to(CircuitState.CLOSED)
            self.failure_count = 0
            self.success_count = 0
            self.request_count = 0


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""

    pass


# Example Usage
if __name__ == "__main__":
    import requests

    # Create circuit breaker for external API
    api_circuit = CircuitBreaker(
        name="external_api",
        failure_threshold=3,
        timeout_ms=5000,
        reset_timeout_ms=10000,
    )

    @api_circuit
    def fetch_data(url: str):
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()

    # Usage
    try:
        data = fetch_data("https://api.example.com/data")
        print(f"Data: {data}")
    except CircuitBreakerOpenError:
        print("Circuit breaker is open, using fallback")
        data = {"fallback": True}
    except Exception as e:
        print(f"Request failed: {e}")

    # Get metrics
    metrics = api_circuit.get_metrics()
    print(f"Circuit breaker metrics: {metrics}")
