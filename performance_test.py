"""Performance test for the Campus Event Management System.

This script measures real HTTP response times against the five running services.
It uses safe GET endpoints only, so it does not create bookings, notifications,
or reviews. Results are written to performance_results.md and
performance_results.csv for use in the assignment report.

Windows usage from the project root:
    pip install requests
    python performance_test.py

Optional examples:
    python performance_test.py --requests 50
    python performance_test.py --requests 100 --workers 5 --timeout 10
"""

from __future__ import annotations

import argparse
import csv
import platform
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import requests

SERVICES = {
    "User / Auth Service": {
        "base_url": "http://127.0.0.1:8001",
        "endpoints": ["/health"],
    },
    "Event Service": {
        "base_url": "http://127.0.0.1:8002",
        "endpoints": ["/health", "/api/events"],
    },
    "Booking Service": {
        "base_url": "http://127.0.0.1:8003",
        "endpoints": ["/health"],
    },
    "Notification Service": {
        "base_url": "http://127.0.0.1:8004",
        "endpoints": ["/health"],
    },
    "Review Service": {
        "base_url": "http://127.0.0.1:8005",
        "endpoints": ["/health"],
    },
}


def request_once(url: str, timeout: float) -> dict:
    """Make one request and return timing and outcome data."""
    started = time.perf_counter()
    try:
        response = requests.get(url, timeout=timeout)
        elapsed_ms = (time.perf_counter() - started) * 1000
        return {
            "ok": 200 <= response.status_code < 400,
            "status_code": response.status_code,
            "elapsed_ms": elapsed_ms,
            "error": "",
        }
    except requests.RequestException as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        return {
            "ok": False,
            "status_code": "ERR",
            "elapsed_ms": elapsed_ms,
            "error": type(exc).__name__,
        }


def percentile(values: list[float], percentage: float) -> float:
    """Return a nearest-rank percentile without requiring NumPy."""
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round((percentage / 100) * len(ordered) + 0.5) - 1))
    return ordered[index]


def measure_endpoint(service: str, base_url: str, endpoint: str, count: int, workers: int, timeout: float) -> dict:
    url = f"{base_url}{endpoint}"
    started = time.perf_counter()
    observations = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(request_once, url, timeout) for _ in range(count)]
        for future in as_completed(futures):
            observations.append(future.result())
    wall_time = time.perf_counter() - started
    successful = [item["elapsed_ms"] for item in observations if item["ok"]]
    failures = [item for item in observations if not item["ok"]]
    status_codes = sorted({str(item["status_code"]) for item in observations})
    return {
        "service": service,
        "endpoint": endpoint,
        "requests": len(observations),
        "successes": len(successful),
        "failures": len(failures),
        "error_rate_pct": round((len(failures) / len(observations)) * 100, 2) if observations else 100.0,
        "avg_ms": round(statistics.mean(successful), 2) if successful else None,
        "median_ms": round(statistics.median(successful), 2) if successful else None,
        "p95_ms": round(percentile(successful, 95), 2) if successful else None,
        "min_ms": round(min(successful), 2) if successful else None,
        "max_ms": round(max(successful), 2) if successful else None,
        "throughput_req_s": round(len(observations) / wall_time, 2) if wall_time else 0.0,
        "status_codes": ", ".join(status_codes),
    }


def run_measurements(count: int, workers: int, timeout: float) -> list[dict]:
    results = []
    for service, config in SERVICES.items():
        for endpoint in config["endpoints"]:
            print(f"Testing {service} -> {endpoint} ({count} requests, {workers} workers)...")
            result = measure_endpoint(service, config["base_url"], endpoint, count, workers, timeout)
            results.append(result)
            print(
                f"  successes={result['successes']} failures={result['failures']} "
                f"avg={result['avg_ms']}ms p95={result['p95_ms']}ms "
                f"throughput={result['throughput_req_s']} req/s"
            )
    return results


def save_markdown(results: list[dict], path: Path, count: int, workers: int, timeout: float) -> None:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Performance Test Results",
        "",
        f"Generated: {generated}",
        f"Environment: {platform.platform()} | Python {platform.python_version()}",
        f"Workload: {count} requests per endpoint, {workers} concurrent worker(s), {timeout}s timeout",
        "",
        "> These are client-observed HTTP timings against the locally running services. They include request, application, and database time. They are not a substitute for a production load test.",
        "",
        "| Service | Endpoint | Requests | Successes | Failures | Error rate | Avg ms | Median ms | P95 ms | Min ms | Max ms | Throughput req/s | Status codes |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in results:
        def value(key):
            return "unavailable" if r[key] is None else r[key]
        lines.append(
            f"| {r['service']} | `{r['endpoint']}` | {r['requests']} | {r['successes']} | {r['failures']} | {r['error_rate_pct']}% | {value('avg_ms')} | {value('median_ms')} | {value('p95_ms')} | {value('min_ms')} | {value('max_ms')} | {r['throughput_req_s']} | {r['status_codes']} |"
        )
    lines += [
        "",
        "## Interpretation guidance",
        "",
        "Use the P95 column to describe the upper-end response time observed during the test. Report the request count, worker count, timeout, machine, service deployment mode, and error rate alongside the results. Repeat the test with a higher worker count to discuss scalability; do not claim scalability from a single sequential run.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def save_csv(results: list[dict], path: Path) -> None:
    if not results:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure response time for the campus event services.")
    parser.add_argument("--requests", type=int, default=20, help="Requests per endpoint; default: 20")
    parser.add_argument("--workers", type=int, default=1, help="Concurrent workers; default: 1")
    parser.add_argument("--timeout", type=float, default=5.0, help="Request timeout in seconds; default: 5")
    parser.add_argument("--output-dir", default=".", help="Folder for result files; default: current folder")
    args = parser.parse_args()
    if args.requests < 1 or args.workers < 1 or args.timeout <= 0:
        parser.error("--requests and --workers must be at least 1, and --timeout must be positive")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Running performance test: {args.requests} requests per endpoint, {args.workers} worker(s)\n")
    results = run_measurements(args.requests, args.workers, args.timeout)
    save_markdown(results, output_dir / "performance_results.md", args.requests, args.workers, args.timeout)
    save_csv(results, output_dir / "performance_results.csv")
    print(f"\nSaved results to {output_dir / 'performance_results.md'}")
    print(f"Saved raw results to {output_dir / 'performance_results.csv'}")


if __name__ == "__main__":
    main()
