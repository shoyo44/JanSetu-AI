# DocsAI DevOps & DevSecOps Architecture & Deployment Guide

This document specifies the operational, deployment, and security hardening procedures for the **DocsAI Enterprise RAG Knowledge Graph Platform**.

---

## 1. System & Security Architecture

DocsAI supports two primary operational topologies:

```mermaid
flowchart TD
    subgraph Client Tier
        Browser["User Browser / Legal Workbench"]
    end

    subgraph Edge & Ingress Tier
        Nginx["Hardened Nginx Reverse Proxy\n(Port 80/3000)\n• Security Headers (CSP, HSTS)\n• Rate Limiting & SSL"]
    end

    subgraph Application Tier
        API["FastAPI Backend Engine\n(Non-root user: docqa 10001)\n• Magic Byte Validation\n• Indirect Prompt Injection Scanner\n• Calibrated Abstention Engine\n• Citation Entailment Verification"]
    end

    subgraph Data & Storage Tier
        Graph["In-Process GraphStore & FAISS\n(Persistent Volume: graph_data)"]
        Redis["Redis Cache & Ingestion Queue\n(Persistent Volume: redis_data)"]
    end

    subgraph AI Backends
        Cloudflare["Cloudflare Workers AI\n(Cloud Mode)"]
        Ollama["Local Ollama Daemon\n(On-Prem / Air-Gapped Mode)"]
    end

    Browser --> Nginx
    Nginx --> API
    API --> Graph
    API --> Redis
    API -.->|LLM_BACKEND=cloudflare| Cloudflare
    API -.->|LLM_BACKEND=ollama| Ollama
```

---

## 2. DevSecOps & Security Pipeline (CI/CD)

The GitHub Actions pipeline (`.github/workflows/ci.yml`) runs on every `push` and `pull_request` against `main`:

| Stage | Tool | Purpose | Failure Condition |
|---|---|---|---|
| **SAST** | Bandit | Python AST security analysis (hardcoded secrets, insecure subprocess calls, unsafe tempfiles) | Any High/Medium severity alert |
| **Dependency Audit** | `pip-audit` & `npm audit` | CVE scanning against Python and Node dependency manifests | Known critical vulnerabilities |
| **Linting & Quality** | `ruff` | Enforces code formatting and static correctness | Any syntax or lint regression |
| **Grounding Smoke Test** | `eval/test_phase4_security.py` | Automated testing of injection scanner, file validator, and rate limiter | Any assertion failure |
| **Container Scan** | Aqua Security Trivy | Container image CVE and misconfiguration scanner | Unfixed Critical/High OS vulnerabilities |

---

## 3. Production Deployment via Docker Compose

### Prerequisites
- Docker Engine 24.0+ and Docker Compose v2.20+
- `.env` file configured (see `.env.example`)

### Quick Start (Standard Cloud Deployment)
```bash
# 1. Clone the repository
git clone https://github.com/shoyo44/DocsAI.git
cd DocsAI

# 2. Configure environment
cp .env.example .env
# Edit .env with your Cloudflare / Nomic credentials

# 3. Build and launch services in background
docker compose up -d --build

# 4. Verify service health
docker compose ps
curl http://localhost:8000/health
```

### Air-Gapped / On-Premise Data Sovereignty Deployment (Ollama)
For legal and government clients who cannot transmit confidential documents to external clouds:

```bash
# 1. Set environment to use Ollama
echo "LLM_BACKEND=ollama" >> .env
echo "OLLAMA_HOST=http://ollama:11434" >> .env
echo "OLLAMA_LLM_MODEL=qwen2.5:7b" >> .env

# 2. Start all services including local Ollama daemon
docker compose --profile onprem up -d --build

# 3. Pull required local models into Ollama container
docker compose exec ollama ollama pull qwen2.5:7b
docker compose exec ollama ollama pull nomic-embed-text
```

---

## 4. Container & Operating System Hardening

1. **Non-Root Execution:** The backend container runs as dedicated user `docqa` (`UID 10001`, `GID 10001`). If a process vulnerability is exploited, the attacker has zero host or root privileges.
2. **Read-Only / Principle of Least Privilege:** State directories (`/app/backend/data` and `/app/backend/temp`) are explicitly isolated with minimal read/write permissions.
3. **Multi-Stage Builds:** Development compilers (`gcc`, `g++`) are discarded in the builder stage, drastically reducing attack surface and image size.
4. **Binary Magic Byte File Validation:** Files uploaded via `/upload` are inspected by raw byte signatures (preventing `.exe` renamed to `.pdf`).
5. **Document-Level Indirect Injection Defense:** Adversarial instructions embedded in uploaded files are quarantined before FAISS indexing.
6. **Sliding-Window Tenant Rate Limiting:** Enforces strict hourly quotas per tenant (20 uploads/hr, 150 queries/hr) returning HTTP 429 when exceeded.

---

## 5. Health Checks & Monitoring

The backend exposes a comprehensive healthcheck at `/health`:

```json
{
  "status": "healthy",
  "timestamp": 1732171200.0,
  "database": {
    "graph_store": "connected",
    "redis": "connected",
    "mongodb": "connected"
  }
}
```

Docker Compose automatically probes this endpoint every 20 seconds. If degraded, the container is marked unhealthy and restarted.
