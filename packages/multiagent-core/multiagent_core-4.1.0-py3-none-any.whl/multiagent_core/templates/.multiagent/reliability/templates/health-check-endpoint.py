"""
Health Check Endpoint Implementation
Purpose: Provide comprehensive health status for Kubernetes/load balancer probes
Endpoints: /health (liveness), /readiness, /health/detailed
"""

from flask import Flask, jsonify, Response
from typing import Dict, List, Callable
import time
import psycopg2
import redis


app = Flask(__name__)


class HealthCheck:
    """
    Comprehensive health check system.

    Supports:
    - Liveness probes (is the app running?)
    - Readiness probes (can the app serve traffic?)
    - Detailed health (component-level status)
    """

    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.startup_time = time.time()

    def register_check(self, name: str, check_func: Callable):
        """Register a health check function."""
        self.checks[name] = check_func

    def check_database(self) -> Dict:
        """Check database connectivity."""
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="myapp",
                user="user",
                password="password",
                connect_timeout=3,
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return {"status": "healthy", "latency_ms": 0}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def check_redis(self) -> Dict:
        """Check Redis connectivity."""
        try:
            r = redis.Redis(host="localhost", port=6379, db=0, socket_connect_timeout=3)
            start = time.time()
            r.ping()
            latency_ms = (time.time() - start) * 1000
            return {"status": "healthy", "latency_ms": round(latency_ms, 2)}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def check_external_api(self, url: str) -> Dict:
        """Check external API availability."""
        import requests

        try:
            start = time.time()
            response = requests.get(url, timeout=5)
            latency_ms = (time.time() - start) * 1000

            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "latency_ms": round(latency_ms, 2),
                    "status_code": response.status_code,
                }
            else:
                return {
                    "status": "degraded",
                    "latency_ms": round(latency_ms, 2),
                    "status_code": response.status_code,
                }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def check_disk_space(self) -> Dict:
        """Check available disk space."""
        import shutil

        try:
            usage = shutil.disk_usage("/")
            percent_used = (usage.used / usage.total) * 100

            if percent_used > 90:
                status = "unhealthy"
            elif percent_used > 80:
                status = "degraded"
            else:
                status = "healthy"

            return {
                "status": status,
                "percent_used": round(percent_used, 2),
                "free_gb": round(usage.free / (1024**3), 2),
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def check_memory(self) -> Dict:
        """Check available memory."""
        import psutil

        try:
            memory = psutil.virtual_memory()
            percent_used = memory.percent

            if percent_used > 95:
                status = "unhealthy"
            elif percent_used > 85:
                status = "degraded"
            else:
                status = "healthy"

            return {
                "status": status,
                "percent_used": percent_used,
                "available_gb": round(memory.available / (1024**3), 2),
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def run_all_checks(self) -> Dict:
        """Run all registered checks."""
        results = {}
        for name, check_func in self.checks.items():
            try:
                results[name] = check_func()
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}

        return results

    def get_overall_status(self, results: Dict) -> str:
        """Determine overall health status from component checks."""
        statuses = [check["status"] for check in results.values()]

        if any(status == "unhealthy" for status in statuses):
            return "unhealthy"
        elif any(status == "degraded" for status in statuses):
            return "degraded"
        else:
            return "healthy"


# Initialize health checker
health_checker = HealthCheck()

# Register checks
health_checker.register_check("database", health_checker.check_database)
health_checker.register_check("redis", health_checker.check_redis)
health_checker.register_check("disk", health_checker.check_disk_space)
health_checker.register_check("memory", health_checker.check_memory)


@app.route("/health", methods=["GET"])
def liveness():
    """
    Liveness probe: Is the application running?
    Kubernetes uses this to restart unhealthy pods.
    Returns 200 if app is alive, regardless of dependencies.
    """
    uptime_seconds = int(time.time() - health_checker.startup_time)

    return jsonify(
        {
            "status": "alive",
            "uptime_seconds": uptime_seconds,
            "timestamp": time.time(),
        }
    ), 200


@app.route("/readiness", methods=["GET"])
@app.route("/health/ready", methods=["GET"])
def readiness():
    """
    Readiness probe: Can the application serve traffic?
    Kubernetes uses this to route traffic to the pod.
    Returns 200 only if all critical dependencies are healthy.
    """
    # Run critical checks only (database, redis)
    critical_checks = {
        "database": health_checker.check_database(),
        "redis": health_checker.check_redis(),
    }

    overall_status = health_checker.get_overall_status(critical_checks)

    if overall_status == "healthy":
        return jsonify({"status": "ready", "checks": critical_checks}), 200
    else:
        return jsonify({"status": "not_ready", "checks": critical_checks}), 503


@app.route("/health/detailed", methods=["GET"])
def detailed_health():
    """
    Detailed health check: Component-level status.
    Used for monitoring and debugging.
    Always returns 200 with detailed status.
    """
    results = health_checker.run_all_checks()
    overall_status = health_checker.get_overall_status(results)
    uptime_seconds = int(time.time() - health_checker.startup_time)

    return jsonify(
        {
            "status": overall_status,
            "uptime_seconds": uptime_seconds,
            "timestamp": time.time(),
            "checks": results,
        }
    ), 200


@app.route("/metrics", methods=["GET"])
def prometheus_metrics():
    """
    Prometheus metrics endpoint.
    Returns health status in Prometheus format.
    """
    results = health_checker.run_all_checks()

    metrics = []
    for name, check in results.items():
        # Convert status to numeric (1=healthy, 0.5=degraded, 0=unhealthy)
        status_value = {
            "healthy": 1,
            "degraded": 0.5,
            "unhealthy": 0,
        }.get(check["status"], 0)

        metrics.append(f'health_check{{component="{name}"}} {status_value}')

        # Add latency if available
        if "latency_ms" in check:
            metrics.append(
                f'health_check_latency_ms{{component="{name}"}} {check["latency_ms"]}'
            )

    return Response("\n".join(metrics), mimetype="text/plain"), 200


if __name__ == "__main__":
    # Run the Flask app
    app.run(host="0.0.0.0", port=8080)
