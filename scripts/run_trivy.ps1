# JanSetu AI — Trivy DevSecOps Security Scanner (Windows PowerShell)
# Scans filesystem, secrets, configurations, and container images using Aqua Security Trivy.
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "      JanSetu AI DevSecOps: Trivy Vulnerability Scan      " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$CurrentDir = (Get-Location).Path

Write-Host "`n[1/3] Scanning Repository Filesystem for CVEs, Secrets & Misconfigurations..." -ForegroundColor Yellow
docker run --rm `
    -v "${CurrentDir}:/app" `
    -v //var/run/docker.sock:/var/run/docker.sock `
    aquasec/trivy:latest fs `
    --scanners vuln,secret,config `
    --severity HIGH,CRITICAL `
    --ignore-unfixed `
    /app

Write-Host "`n[2/3] Scanning Backend Container Image..." -ForegroundColor Yellow
docker run --rm `
    -v //var/run/docker.sock:/var/run/docker.sock `
    aquasec/trivy:latest image `
    --severity HIGH,CRITICAL `
    --ignore-unfixed `
    jansetu-ai-backend:latest

Write-Host "`n[3/3] Scanning Frontend Container Image..." -ForegroundColor Yellow
docker run --rm `
    -v //var/run/docker.sock:/var/run/docker.sock `
    aquasec/trivy:latest image `
    --severity HIGH,CRITICAL `
    --ignore-unfixed `
    jansetu-ai-frontend:latest

Write-Host "`n[✓] Trivy DevSecOps scan completed." -ForegroundColor Green
