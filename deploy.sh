#!/bin/bash
set -eo pipefail

TARGET=$1

if [ "$TARGET" != "localhost" ] && [ "$TARGET" != "aws" ]; then
    echo "Usage: $0 [localhost|aws]"
    exit 1
fi

echo "Deploying to $TARGET..."

if [ "$TARGET" == "localhost" ]; then
    docker compose -f docker-compose.local.yml up -d --build
    
    echo "Waiting for health check..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health | grep -q '"status":"ok"'; then
            echo "Deployment healthy!"
            exit 0
        fi
        echo "Waiting..."
        sleep 2
    done
    
    echo "Health check failed! Rolling back..."
    docker compose -f docker-compose.local.yml down
    exit 1

elif [ "$TARGET" == "aws" ]; then
    echo "[SIMULATION] Validating environment variables..."
    if [ -z "$AWS_REGION" ]; then export AWS_REGION="us-east-1"; fi
    if [ -z "$AWS_ACCOUNT_ID" ]; then export AWS_ACCOUNT_ID="123456789012"; fi
    
    echo "[SIMULATION] Building and pushing Docker image..."
    export GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "latest")
    echo "docker build -t ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/tabular-analytics:${GIT_SHA} ."
    
    echo "[SIMULATION] Deploying via Docker Compose to EC2 target..."
    # Normally we would scp the compose file and run docker-compose up on the instance
    echo "docker compose -f docker-compose.aws.yml up -d"
    
    echo "[SIMULATION] Deployment successful."
fi
