# Incident Runbook — Elevated Error Rate / Latency

**Scope:** Applies to alerts fired from `datadog/monitors.json` ("High Error Rate", "p95 Latency Breach") or the Splunk saved search `5xx spike detection`.

## 1. Acknowledge & Triage (target: < 5 min)

- Acknowledge the page in Datadog / Slack (`@slack-sre-oncall`).
- Open the **Service Health & Delivery Overview** Datadog dashboard (`datadog/dashboard.json`) and confirm which service and endpoint are affected.
- Cross-check in Splunk using the **Service Health Overview** dashboard (`splunk/dashboard.xml`) — filter by the affected service.

## 2. Establish Scope

Run the following to determine blast radius:

- Splunk: `splunk/saved_searches.spl` search #3 (Top failing endpoints, last 1 hour).
- Datadog: Log Explorer filtered on `service:<name> status_code:>=400`, grouped by `endpoint`.
- `kubectl get pods -n <namespace>` and `kubectl describe pod <pod>` if Kubernetes-related alert (CrashLoopBackOff monitor).

## 3. Correlate With Recent Changes

- Check the CI/CD pipeline history (Jenkins / GitLab CI) for deploys in the last 60 minutes.
- Compare against the **Deployment Frequency** panel on the Datadog dashboard to see if the incident lines up with a recent release.
- If a recent deploy correlates, prefer **rollback** over forward-fix.

## 4. Mitigate

Common mitigations, in order of speed:

1. Roll back the last deployment (Blue-Green / Canary rollback via CI/CD pipeline).
2. Scale the affected deployment (`kubectl scale deployment <name> --replicas=<n>`) if the issue is load-related.
3. Restart the affected pods (`kubectl rollout restart deployment <name>`) if the issue looks like a transient crash.
4. Disable a misbehaving feature flag / integration if identified.

## 5. Capture Evidence Before It Rotates

Run `scripts/log_analyzer.py` against the current log window to snapshot error rate and latency at the time of incident:

```bash
python3 scripts/log_analyzer.py --file /var/log/app/app.log
```

Save the output alongside the Datadog monitor notification and the Splunk search results for the postmortem.

## 6. Confirm Recovery

- Error rate back under 5% for 3 consecutive 5-minute windows.
- p95 latency back under 500ms.
- Datadog monitor auto-resolves (`is_recovery` message fires).

## 7. Postmortem

Document within 24 hours:

- Timeline (detection time, mitigation time, resolution time → feeds MTTR).
- Root cause.
- Action items with owners (link to tracking ticket).
- Update this runbook if a new failure mode was discovered.
