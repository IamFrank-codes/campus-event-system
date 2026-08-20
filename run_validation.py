"""Run health checks and all service test suites, then write validation_results.md.

Windows usage from the project root:
    python run_validation.py
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
SERVICES = [
    ("User/Auth Service", "user-service", 8001),
    ("Event Service", "event-service", 8002),
    ("Booking Service", "booking-service", 8003),
    ("Notification Service", "notification-service", 8004),
    ("Review Service", "review-services", 8005),
]

def health_checks():
    rows=[]
    for name, _, port in SERVICES:
        url=f"http://127.0.0.1:{port}/health"
        try:
            response=requests.get(url, timeout=5)
            rows.append((name, url, response.status_code, response.status_code == 200, response.text[:200]))
        except requests.RequestException as exc:
            rows.append((name, url, "ERR", False, type(exc).__name__))
    return rows

def test_suites():
    rows=[]
    for name, folder, _ in SERVICES:
        service_python = ROOT / folder / "venv" / "Scripts" / "python.exe"
        if not service_python.exists():
            service_python = ROOT / folder / "venv" / "bin" / "python"
        interpreter = str(service_python) if service_python.exists() else sys.executable
        command=[interpreter, "-m", "pytest", "-q"]
        completed=subprocess.run(command, cwd=ROOT / folder, capture_output=True, text=True)
        output=(completed.stdout + "\n" + completed.stderr).strip()
        summary=output.splitlines()[-1] if output else "No pytest output"
        rows.append((name, folder, completed.returncode, completed.returncode == 0, summary, output[-1200:]))
    return rows

def main():
    health=health_checks()
    tests=test_suites()
    lines=["# Validation Results", "", f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", ""]
    lines += ["## Service health", "", "| Service | URL | HTTP status | Result | Detail |", "|---|---|---:|---|---|"]
    for name,url,status,passed,detail in health:
        lines.append(f"| {name} | `{url}` | {status} | {'PASS' if passed else 'FAIL'} | {detail.replace('|','/')} |")
    lines += ["", "## Test suites", "", "| Service | Folder | Exit code | Result | Summary |", "|---|---|---:|---|---|"]
    for name,folder,code,passed,summary,_ in tests:
        lines.append(f"| {name} | `{folder}` | {code} | {'PASS' if passed else 'FAIL'} | {summary.replace('|','/')} |")
    lines += ["", "## Evidence notes", "", "The health section proves whether each service was reachable at the time of testing. The test section records the actual pytest result; do not replace failed results with an earlier claim. If failures are caused by stale unauthenticated fixtures, update the tests and rerun this script.", ""]
    (ROOT / "validation_results.md").write_text("\n".join(lines), encoding="utf-8")
    print("Saved validation_results.md")
    return 0 if all(row[3] for row in health) and all(row[3] for row in tests) else 1

if __name__ == "__main__":
    raise SystemExit(main())
