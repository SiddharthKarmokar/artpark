# Deployment

## Overview
The platform uses Docker Compose for both local and cloud deployments, ensuring consistency across environments.

## Deployment Targets

### Local Environment
For development and testing:
```bash
./deploy.sh localhost
```
This spins up PostgreSQL, Redis, Prometheus, Grafana, Traefik, and the FastAPI application.

### AWS (Production)
The production deployment utilizes ECS or an EC2 instance running Docker Compose:
```bash
./deploy.sh aws
```
- Uses `docker-compose.aws.yml`.
- Automates TLS certificate provisioning via Let's Encrypt and Traefik.
- Pulls immutable Docker images tagged with the latest Git SHA.

## Rollback Strategy
The `deploy.sh` script monitors the `/health` endpoint after deployment. If the application fails to become healthy within the designated timeout, it automatically initiates a rollback by reverting the container deployment.
