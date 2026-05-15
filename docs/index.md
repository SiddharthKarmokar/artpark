# Financial Analytics Platform

Welcome to the internal platform engineering documentation for the Tabular Analytics system.

## Overview
This service provides natural-language analytics over financial datasets. It combines the flexibility of LLM intent parsing with the determinism of a traditional analytics engine.

## Quickstart

### Prerequisites
- Docker & Docker Compose
- `uv` (for local Python dependency management)

### Running Locally
```bash
./deploy.sh localhost
```

### Running Tests
```bash
make test
```

## Architecture Summary
The application is built on FastAPI, using PostgreSQL for persistence and lineage tracking, and Redis for caching and dataset-version-aware invalidation.
It exposes structured metrics to Prometheus, traces to Tempo (via OpenTelemetry), and logs to Loki.
