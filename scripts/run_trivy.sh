#!/usr/bin/env bash
# JanSetu AI — Trivy DevSecOps Security Scanner
# Scans filesystem, secrets, configurations, and container images using Aqua Security Trivy.
set -euo pipefail

echo "=========================================================="
echo "      JanSetu AI DevSecOps: Trivy Vulnerability Scan      "
echo "=========================================================="

if ! command -v docker &> /dev/null; then
    echo "[!] Docker is required to run Trivy in containerized mode."
    exit 1
fi

echo "[1/3] Scanning Repository Filesystem for CVEs, Secrets & Misconfigurations..."
docker run --rm \
    -v "$PWD":/app \
    -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy:latest fs \
    --scanners vuln,secret,config \
    --severity HIGH,CRITICAL \
    --ignore-unfixed \
    /app

echo ""
echo "[2/3] Scanning Backend Container Image..."
if docker image inspect jansetu-ai-backend:latest &> /dev/null; then
    docker run --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        aquasec/trivy:latest image \
        --severity HIGH,CRITICAL \
        --ignore-unfixed \
        jansetu-ai-backend:latest
else
    echo "[*] Building backend image for scanning..."
    docker build -t jansetu-ai-backend:scan -f Dockerfile .
    docker run --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        aquasec/trivy:latest image \
        --severity HIGH,CRITICAL \
        --ignore-unfixed \
        jansetu-ai-backend:scan
fi

echo ""
echo "[3/3] Scanning Frontend Container Image..."
if docker image inspect jansetu-ai-frontend:latest &> /dev/null; then
    docker run --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        aquasec/trivy:latest image \
        --severity HIGH,CRITICAL \
        --ignore-unfixed \
        jansetu-ai-frontend:latest
else
    echo "[*] Building frontend image for scanning..."
    docker build -t jansetu-ai-frontend:scan -f frontend/Dockerfile frontend
    docker run --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        aquasec/trivy:latest image \
        --severity HIGH,CRITICAL \
        --ignore-unfixed \
        jansetu-ai-frontend:scan
fi

echo ""
echo "[✓] Trivy DevSecOps scan completed successfully."
