#!/usr/bin/env python3
"""
log_generator.py
----------------
Generates realistic, structured application log events (JSON lines) to
simulate a production service. Used to feed sample data into Splunk
(via HTTP Event Collector / file monitoring) and Datadog (via the
Datadog Agent log collection) for dashboarding, alerting, and SPL
practice without needing a live production workload.

Usage:
    python3 log_generator.py --count 500 --error-rate 0.08 --out sample-logs/app.log
"""

import argparse
import json
import random
import time
import uuid
from datetime import datetime, timezone

SERVICES = ["auth-service", "payments-service", "orders-service", "notifications-service"]
ENDPOINTS = ["/api/login", "/api/orders", "/api/payments/charge", "/api/notify", "/api/health"]
STATUS_POOL_OK = [200, 201, 204]
STATUS_POOL_ERR = [400, 401, 404, 500, 502, 503]
LOG_LEVELS_OK = ["INFO", "DEBUG"]
LOG_LEVELS_ERR = ["ERROR", "WARN"]


def make_event(force_error: bool) -> dict:
    status = random.choice(STATUS_POOL_ERR) if force_error else random.choice(STATUS_POOL_OK)
    level = random.choice(LOG_LEVELS_ERR) if force_error else random.choice(LOG_LEVELS_OK)
    latency_ms = round(random.uniform(120, 900), 2) if force_error else round(random.uniform(10, 180), 2)

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "service": random.choice(SERVICES),
        "endpoint": random.choice(ENDPOINTS),
        "status_code": status,
        "latency_ms": latency_ms,
        "trace_id": str(uuid.uuid4()),
        "host": f"ip-10-0-{random.randint(1,4)}-{random.randint(1,254)}",
        "message": "request failed" if force_error else "request completed",
    }
    return event


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic app logs for Splunk/Datadog ingestion")
    parser.add_argument("--count", type=int, default=200, help="Number of log lines to generate")
    parser.add_argument("--error-rate", type=float, default=0.05, help="Fraction of events that are errors (0-1)")
    parser.add_argument("--out", type=str, default="sample-logs/app.log", help="Output file path (JSON lines)")
    parser.add_argument("--stream", action="store_true", help="Write continuously (tail -f style) instead of a batch")
    parser.add_argument("--interval", type=float, default=0.5, help="Seconds between events when --stream is set")
    args = parser.parse_args()

    with open(args.out, "a", buffering=1) as f:
        if args.stream:
            print(f"Streaming logs to {args.out} (Ctrl+C to stop)...")
            try:
                while True:
                    is_error = random.random() < args.error_rate
                    f.write(json.dumps(make_event(is_error)) + "\n")
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\nStopped.")
        else:
            for _ in range(args.count):
                is_error = random.random() < args.error_rate
                f.write(json.dumps(make_event(is_error)) + "\n")
            print(f"Wrote {args.count} log events to {args.out}")


if __name__ == "__main__":
    main()
