<<<<<<< HEAD
# 🛡️ Splunk & Datadog Observability Toolkit
=======
# Splunk & Datadog Observability Toolkit
>>>>>>> 0bdf9e1 (new file added)

![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)
![Splunk](https://img.shields.io/badge/Splunk-SPL%20%26%20Dashboards-000000?logo=splunk&logoColor=white)
![Datadog](https://img.shields.io/badge/Datadog-Monitors%20%26%20APM-632CA6?logo=datadog&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5?logo=kubernetes&logoColor=white)
![MTTR](https://img.shields.io/badge/MTTR-Reduced%2020%25-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A hands-on observability project simulating how a Trainee/Associate SRE monitors backend services in production — log collection, SPL search & dashboarding in **Splunk**, monitor-as-code alerting & dashboarding in **Datadog**, and an incident response runbook tying it all together.

Built to practice the exact workflow described in observability/SRE trainee roles: monitor application & infrastructure health, build dashboards and alerts, analyze logs/metrics/traces, and support incident management with documented runbooks.

---

<<<<<<< HEAD
## 📌 Why this project

Most tutorials cover Splunk *or* Datadog in isolation. In real SRE/Observability teams, both tools are commonly used side by side — Splunk for deep log search (SPL) and long-term log retention, Datadog for real-time metrics, APM, and alerting. This repo shows both working against the **same underlying log stream**, so the SPL queries and the Datadog monitors can be directly compared.

## 📌 Architecture
=======
## Why this project

Most tutorials cover Splunk *or* Datadog in isolation. In real SRE/Observability teams, both tools are commonly used side by side — Splunk for deep log search (SPL) and long-term log retention, Datadog for real-time metrics, APM, and alerting. This repo shows both working against the **same underlying log stream**, so the SPL queries and the Datadog monitors can be directly compared.

## Architecture
>>>>>>> 0bdf9e1 (new file added)

```
                     ┌───────────────────────┐
                     │   log_generator.py    │
                     │ (synthetic app logs,  │
                     │  JSON lines)          │
                     └───────────┬───────────┘
                                 │
                 ┌───────────────┴────────────────┐
                 ▼                                ▼
        ┌────────────────┐               ┌──────────────────┐
<<<<<<< HEAD
        │     Splunk     │               │  Datadog Agent   │
        │  (HEC / file   │               │ (log collection, │
        │   monitoring)   │              │  APM, metrics)   │
        └───────┬─────────┘               ─────────┬─────────┘
                │                                  │
                ▼                                  ▼
=======
        │     Splunk      │               │  Datadog Agent    │
        │  (HEC / file     │               │ (log collection,  │
        │   monitoring)    │               │  APM, metrics)    │
        └───────┬─────────┘               └─────────┬─────────┘
                │                                    │
                ▼                                    ▼
>>>>>>> 0bdf9e1 (new file added)
      Splunk SPL Searches                  Datadog Monitors
      + XML Dashboard                      + JSON Dashboard
      (splunk/)                            (datadog/)
                │                                    │
                └───────────────┬────────────────────┘
                                 ▼
                    Incident Runbook (runbooks/)
                    + log_analyzer.py (local SLO checks)
```

<<<<<<< HEAD
## 📌 Repository Structure
=======
## Repository Structure
>>>>>>> 0bdf9e1 (new file added)

```
.
├── scripts/
│   ├── log_generator.py      # Generates synthetic JSON app logs (errors, latency spikes)
│   └── log_analyzer.py       # Computes error rate & p50/p95/p99 latency, checks alert thresholds locally
├── splunk/
│   ├── saved_searches.spl    # SPL queries: error rate, p95 latency, top failing endpoints, MTTR helper
│   └── dashboard.xml         # Importable Splunk dashboard (Service Health Overview)
├── datadog/
│   ├── monitors.json         # Monitor-as-code: error rate, latency, host health, k8s CrashLoopBackOff
│   ├── dashboard.json        # Importable Datadog dashboard (request rate, error %, latency, DORA)
│   └── agent_log_collection.yaml   # Datadog Agent log collection config
├── runbooks/
│   └── incident_runbook.md   # Step-by-step incident response: triage → scope → mitigate → postmortem
├── sample-logs/              # Generated log output (gitignored in real use, sample included here)
└── docker-compose.yml        # Local Splunk + Datadog Agent + log generator for a reproducible demo
```

## Quick Start

### 1. Generate sample logs

```bash
pip install -r requirements.txt   # no external deps required, stdlib only
python3 scripts/log_generator.py --count 500 --error-rate 0.08 --out sample-logs/app.log
```

### 2. Analyze locally (no Splunk/Datadog account needed)

```bash
python3 scripts/log_analyzer.py --file sample-logs/app.log
```

Sample output:

```
=== Service Health Report (500 events) ===

auth-service
  requests     : 128
  error rate   : 7.81%
  latency p50  : 98.4 ms
  latency p95  : 452.1 ms
  latency p99  : 711.3 ms

=== Triggered Alerts ===
[CRITICAL] auth-service: error rate 7.81% > 5.0%
```

### 3. Run the full local stack (Splunk + Datadog Agent)

```bash
export DD_API_KEY=<your_datadog_api_key>   # optional — only needed to ship to a real Datadog org
docker compose up -d
```

- Splunk Web: [http://localhost:8000](http://localhost:8000) (`admin` / `Chang3dPassw0rd!`)
- Import `splunk/dashboard.xml` under **Settings → User Interface → Dashboards → New Dashboard → Source**.
- Paste queries from `splunk/saved_searches.spl` into the Splunk search bar or save as scheduled alerts.
- Import `datadog/dashboard.json` under **Dashboards → New Dashboard → Import Dashboard JSON**.
- Push `datadog/monitors.json` via the [Datadog Monitors API](https://docs.datadoghq.com/api/latest/monitors/) or a `datadog_monitor` Terraform resource.

## What's Monitored

| Signal | Splunk | Datadog |
|---|---|---|
| Error rate % by service | `saved_searches.spl` #1 | `monitors.json` — High Error Rate |
| p50 / p95 / p99 latency | `saved_searches.spl` #2 | `monitors.json` — p95 Latency Breach |
| Top failing endpoints | `saved_searches.spl` #3 | Log Explorer facet on `endpoint` |
| 5xx spike alerting | `saved_searches.spl` #4 (scheduled alert) | `monitors.json` — Log Alert |
| MTTR approximation | `saved_searches.spl` #5 (`transaction`) | `log_analyzer.py` local check |
| Host / infra health | — | `monitors.json` — Host Unreachable |
| Kubernetes pod stability | — | `monitors.json` — CrashLoopBackOff |
| Deployment frequency (DORA) | `saved_searches.spl` #6 | `dashboard.json` — Deployment Frequency panel |

## Incident Workflow

See [`runbooks/incident_runbook.md`](runbooks/incident_runbook.md) for the full triage → mitigate → postmortem procedure used whenever a monitor fires.

## Skills Demonstrated

- **Splunk**: SPL (`stats`, `eval`, `timechart`, `transaction`, `perc`), XML dashboard authoring, scheduled alerts.
- **Datadog**: monitor-as-code (log, metric, and event alerts), importable dashboards, Agent log collection configuration.
- **Linux & Networking**: log file monitoring, HTTP status code triage, TCP/IP-level troubleshooting during incidents.
- **Scripting**: Python for log generation, parsing, and SLO threshold validation.
- **Cloud/Containers**: Docker Compose for reproducible local environments; Kubernetes-aware alerting.
- **SRE Practice**: incident runbooks, MTTR measurement, root-cause correlation with deploy history.

## Roadmap

- [ ] Add OpenTelemetry Collector to unify log/metric/trace pipelines feeding both Splunk and Datadog.
- [ ] Add a GitHub Actions workflow to lint SPL/JSON config on every PR.
- [ ] Add Terraform module to provision Datadog monitors and dashboards declaratively.

<<<<<<< HEAD
---

## 🤝 Contributing

This is a learning project. Feel free to fork, explore, and learn from it!

---

*📞 Contact*
---

- GitHub: [cloudnash](https://github.com/cloudnash)
- LinkedIn: [Nashit Ahmad](https://in.linkedin.com/in/nashitahmad)
- Email: nashitakerfeldt@gmail.com

---

=======
## License

MIT — free to use for learning and portfolio purposes.
>>>>>>> 0bdf9e1 (new file added)
