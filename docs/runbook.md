# Runbook

## Overview
This runbook provides operational instructions for the Financial Analytics Platform.

## Common Operations

### Restarting Services
To restart the application or infrastructure services:
```bash
./deploy.sh localhost
```
For AWS deployment restarts, trigger the CI/CD pipeline or manually scale the Auto Scaling Group (ASG) or ECS service.

### Debugging Failed Requests
1. Check the `/metrics` endpoint for elevated error rates.
2. Locate the `trace_id` returned in the failed response or within the structured logs.
3. Query the Loki backend using the `trace_id` to inspect the full request lifecycle.

### Handling Data Ingestion Failures
If ingestion fails:
- Ensure the CSVs in `/data/finance` are well-formed.
- Check the `ingestion_service` logs for parsing errors.
- Trigger manual ingestion via the `/ingest` API endpoint.
