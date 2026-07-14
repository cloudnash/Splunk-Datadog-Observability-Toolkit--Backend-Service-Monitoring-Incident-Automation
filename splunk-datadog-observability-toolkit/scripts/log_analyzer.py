#!/usr/bin/env python3
"""
log_analyzer.py
----------------
Parses JSON-line application logs (as produced by log_generator.py or
collected by the Datadog Agent / Splunk forwarder) and computes the
core observability signals used across the dashboards and alerts in
this repo:

    - Request volume per service
    - Error rate (%) per service (5xx + 4xx)
    - p50 / p95 / p99 latency per service
    - A simple threshold-based alert check that mirrors the Datadog
      monitor logic in datadog/monitors.json, so alert rules can be
      unit tested locally before being pushed to Datadog.

Usage:
    python3 log_analyzer.py --file sample-logs/app.log
"""

import argparse
import json
from collections import defaultdict
from statistics import quantiles


def load_events(path: str):
    events = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def analyze(events):
    by_service = defaultdict(lambda: {"total": 0, "errors": 0, "latencies": []})

    for e in events:
        svc = e.get("service", "unknown")
        stats = by_service[svc]
        stats["total"] += 1
        stats["latencies"].append(e.get("latency_ms", 0))
        if int(e.get("status_code", 200)) >= 400:
            stats["errors"] += 1

    report = {}
    for svc, stats in by_service.items():
        lat = sorted(stats["latencies"])
        p50 = p95 = p99 = 0
        if len(lat) >= 2:
            q = quantiles(lat, n=100, method="inclusive")
            p50, p95, p99 = q[49], q[94], q[98]
        elif lat:
            p50 = p95 = p99 = lat[0]

        error_rate = (stats["errors"] / stats["total"] * 100) if stats["total"] else 0
        report[svc] = {
            "total_requests": stats["total"],
            "errors": stats["errors"],
            "error_rate_pct": round(error_rate, 2),
            "p50_ms": round(p50, 2),
            "p95_ms": round(p95, 2),
            "p99_ms": round(p99, 2),
        }
    return report


def check_alerts(report, error_rate_threshold=5.0, p95_threshold_ms=500.0):
    """Mirrors the thresholds defined in datadog/monitors.json"""
    triggered = []
    for svc, stats in report.items():
        if stats["error_rate_pct"] > error_rate_threshold:
            triggered.append(f"[CRITICAL] {svc}: error rate {stats['error_rate_pct']}% > {error_rate_threshold}%")
        if stats["p95_ms"] > p95_threshold_ms:
            triggered.append(f"[WARN] {svc}: p95 latency {stats['p95_ms']}ms > {p95_threshold_ms}ms")
    return triggered


def main():
    parser = argparse.ArgumentParser(description="Analyze JSON-line logs for error rate and latency SLOs")
    parser.add_argument("--file", type=str, default="sample-logs/app.log", help="Path to the log file")
    parser.add_argument("--error-threshold", type=float, default=5.0, help="Error rate %% alert threshold")
    parser.add_argument("--p95-threshold", type=float, default=500.0, help="p95 latency (ms) alert threshold")
    args = parser.parse_args()

    events = load_events(args.file)
    if not events:
        print(f"No events found in {args.file}. Run log_generator.py first.")
        return

    report = analyze(events)

    print(f"\n=== Service Health Report ({len(events)} events) ===\n")
    for svc, stats in report.items():
        print(f"{svc}")
        print(f"  requests     : {stats['total_requests']}")
        print(f"  error rate   : {stats['error_rate_pct']}%")
        print(f"  latency p50  : {stats['p50_ms']} ms")
        print(f"  latency p95  : {stats['p95_ms']} ms")
        print(f"  latency p99  : {stats['p99_ms']} ms\n")

    alerts = check_alerts(report, args.error_threshold, args.p95_threshold)
    if alerts:
        print("=== Triggered Alerts ===")
        for a in alerts:
            print(a)
    else:
        print("No thresholds breached.")


if __name__ == "__main__":
    main()
