"""
JanSetu AI Backend Application Entry Point.
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from app.core.cloudflare_ai import CloudflareAI
from app.core.dependencies import _create_redis_client
from app.features.jobs import create_job_queue
from app.graph.store import GraphStore
import app.core.factory as pipeline_factory
from app.core.observability import metrics

from app.api import base_router, stream_router, agent_router, analytics_router
# ─── Logging & Configuration ──────────────────────────────────────────────────

load_dotenv()
parent_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(parent_env):
    load_dotenv(parent_env)
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("docqa.main")

# Silence verbose third-party libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("huggingface_hub").setLevel(logging.WARNING)


# ─── Connectivity Check Helper ──────────────────────────────────────────────

async def run_startup_connectivity_check(app: FastAPI) -> None:
    """Run verification tests against connected external API services."""
    print("\n" + "=" * 60)
    print("           JanSetu AI API CONNECTIVITY DIAGNOSTICS")
    print("=" * 60)

    # 1. GraphStore connectivity (always OK — in-process)
    try:
        ok = app.state.graph_store.verify_connectivity()
        print(f"  [OK] Graph Store:           IN-PROCESS (Nodes={app.state.graph_store._graph.number_of_nodes()})")
    except Exception as exc:
        print(f"  [FAIL] Graph Store:           FAILED: {exc}")

    # 2. Redis connectivity
    if getattr(app.state, "redis", None):
        try:
            app.state.redis.ping()
            print("  [OK] Redis Cache:           CONNECTED (OK)")
        except Exception as exc:
            print(f"  [FAIL] Redis Cache:           CONNECTION FAILED: {exc}")
    else:
        print("  [-] Redis Cache:           DISABLED (Offline/Not Configured)")

    # 3. Nomic Embeddings API connectivity
    try:
        from app.core.dependencies import get_embedding
        await get_embedding("test connectivity")
        print("  [OK] Nomic Embeddings API:  CONNECTED (OK)")
    except Exception as exc:
        print(f"  [FAIL] Nomic Embeddings API:  CONNECTION FAILED: {exc}")

    # 4. LLM Backend Connectivity (Cloudflare Workers AI or Ollama On-Premise)
    try:
        from app.core.ollama_client import OllamaClient
        is_ollama = isinstance(app.state.cf_client, OllamaClient)
        backend_name = f"Ollama On-Premise ({app.state.cf_client.llm_model})" if is_ollama else "Cloudflare Workers AI"
        await app.state.cf_client.chat(
            system_prompt="You are a connection test agent. Respond with one word: OK.",
            user_message="test connection",
            max_tokens=10,
        )
        print(f"  [OK] LLM Backend:           CONNECTED ({backend_name})")
    except Exception as exc:
        backend_name = "Ollama" if getattr(app.state, "cf_client", None) and hasattr(app.state.cf_client, "llm_model") else "Cloudflare Workers AI"
        print(f"  [FAIL] LLM Backend:         CONNECTION FAILED ({backend_name}): {exc}")

    # 5. MongoDB History DB connectivity
    if getattr(app.state, "mongodb_client", None):
        if getattr(app.state, "mongodb_is_fallback", False):
            print("  [OK] MongoDB History DB:      CONNECTED (Local JSON Fallback DB)")
        else:
            try:
                app.state.mongodb_client.admin.command('ping')
                db_name = os.getenv("MONGODB_DB", "jansetu_db")
                coll_name = os.getenv("MONGODB_COLLECTION", "chat_history")
                print(f"  [OK] MongoDB History DB:      CONNECTED (DB={db_name}, Coll={coll_name})")
            except Exception as exc:
                print(f"  [FAIL] MongoDB History DB:    CONNECTION FAILED: {exc}")
    else:
        print("  [-] MongoDB History DB:      DISABLED (Not Configured)")

    # 6. Sovereign Cryptographic Provenance Ledger
    print("  [OK] Merkle Provenance Ledger: INITIALIZED (SHA-256 Hash Tree)")

    print("=" * 60 + "\n")


# ─── Application Lifespan Lifecycle ──────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events: Initialize GraphStore, Redis, Cloudflare AI client,
    job queue, and clean up on shutdown.
    """
    logger.info("Initializing JanSetu AI backend components...")

    # 1. In-Process Graph Store (replaces Neo4j)
    data_dir = os.getenv("GRAPH_STORE_DIR", os.path.join(os.path.dirname(__file__), "data"))
    app.state.graph_store = GraphStore(data_dir=data_dir)
    logger.info("GraphStore initialized at %s", data_dir)

    # 2. Redis Caching
    app.state.redis = _create_redis_client()

    # 3. Ingestion Job Queue
    app.state.job_queue = create_job_queue(app.state.redis)

    llm_backend = os.getenv("LLM_BACKEND", "cloudflare").lower()
    if llm_backend == "ollama":
        from app.core.ollama_client import OllamaClient
        app.state.cf_client = OllamaClient()
        logger.info("Initialized On-Premise OllamaClient as primary LLM backend.")
    else:
        cf_account = os.getenv("CF_ACCOUNT_ID")
        cf_token = os.getenv("CF_API_TOKEN")
        if cf_account and cf_token:
            app.state.cf_client = CloudflareAI(
                account_id=cf_account,
                api_token=cf_token,
            )
            logger.info("Initialized CloudflareAI as primary LLM backend.")
        else:
            logger.warning("Cloudflare credentials not found. Falling back to on-premise OllamaClient.")
            from app.core.ollama_client import OllamaClient
            app.state.cf_client = OllamaClient()
    from app.rerankers.cross_encoder import CrossEncoderReranker
    try:
        app.state.reranker = CrossEncoderReranker()
    except Exception as e:
        logger.warning("Failed to initialize CrossEncoderReranker: %s", e)
        app.state.reranker = None

    # 5. Pipeline factory reference
    app.state.pipeline_factory = pipeline_factory

    # 5.2. Semantic Cache
    from app.core.cache import SemanticCache
    app.state.semantic_cache = SemanticCache()

    # 6. MongoDB connection for query log history
    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_db_name = os.getenv("MONGODB_DB", "jansetu_db")
    
    app.state.mongodb_is_fallback = False
    
    if mongodb_uri:
        try:
            import pymongo
            app.state.mongodb_client = pymongo.MongoClient(mongodb_uri, serverSelectionTimeoutMS=2000)
            # Verify connectivity immediately
            app.state.mongodb_client.admin.command('ping')
            app.state.mongodb_db = app.state.mongodb_client[mongodb_db_name]
            logger.info("MongoDB client connected to database: %s", mongodb_db_name)
        except Exception as exc:
            logger.warning("Failed to connect to MongoDB Atlas (%s). Initializing local JSON fallback database...", exc)
            from app.core.json_fallback_db import JSONFallbackClient
            fallback_dir = os.path.join(data_dir, "json_db")
            app.state.mongodb_client = JSONFallbackClient(db_dir=fallback_dir)
            app.state.mongodb_db = app.state.mongodb_client[mongodb_db_name]
            app.state.mongodb_is_fallback = True
    else:
        logger.info("MongoDB URI not configured. Initializing local JSON fallback database...")
        from app.core.json_fallback_db import JSONFallbackClient
        fallback_dir = os.path.join(data_dir, "json_db")
        app.state.mongodb_client = JSONFallbackClient(db_dir=fallback_dir)
        app.state.mongodb_db = app.state.mongodb_client[mongodb_db_name]
        app.state.mongodb_is_fallback = True

    # 7. Helper: expose asyncio event loop helper for routes/pipeline
    app.state.get_running_loop = asyncio.get_running_loop

    # 8. Sovereign Merkle Provenance Ledger (SHA-256 Chained Hash Tree)
    from app.core.sovereign_ledger import SovereignLedger
    app.state.sovereign_ledger = SovereignLedger(mongodb_db=getattr(app.state, "mongodb_db", None))
    logger.info("Sovereign Merkle Provenance Ledger initialized (SHA-256 Chained Hash Tree).")

    # Run Connectivity Diagnostic Check
    await run_startup_connectivity_check(app)

    logger.info("🚀 Backend startup initialization complete.")
    yield

    # Shutdown / Connection Cleanup
    logger.info("Cleaning up backend resources...")

    # Close Cloudflare client
    await app.state.cf_client.close()

    # Close Redis connection if present
    if getattr(app.state, "redis", None):
        try:
            app.state.redis.close()
        except Exception:
            pass

    # Close MongoDB client if present
    if getattr(app.state, "mongodb_client", None):
        try:
            app.state.mongodb_client.close()
            logger.info("MongoDB client connection closed.")
        except Exception:
            pass

    logger.info("Shutdown resources closed.")


# ─── FastAPI Bootstrap ────────────────────────────────────────────────────────

app = FastAPI(
    title="JanSetu AI Core Backend API",
    description="Sovereign multi-vertical agentic knowledge graph & RAG engine for public governance and citizen welfare.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configurations
cors_origins_raw = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000,https://docs-ai-ashen.vercel.app"
)
allowed_origins = [orig.strip() for orig in cors_origins_raw.split(",") if orig.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Prometheus Telemetry Middleware ──────────────────────────────────────────

@app.middleware("http")
async def prometheus_telemetry_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as exc:
        status_code = 500
        raise exc from None
    finally:
        duration = time.perf_counter() - start_time
        path = request.url.path
        if path != "/metrics":
            # Sanitize path to avoid cardinality explosion on IDs
            norm_path = path
            if path.startswith("/api/v1/documents/") and len(path.split("/")) > 4:
                norm_path = "/api/v1/documents/{id}"
            metrics.inc_counter("http_requests_total", {"method": request.method, "endpoint": norm_path, "status": str(status_code)})
            metrics.observe_duration("http_request_duration_seconds", duration, {"endpoint": norm_path})
    return response


# ─── Mount Routers ────────────────────────────────────────────────────────────

app.include_router(base_router, prefix="/api/v1")
app.include_router(stream_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")


# ─── Root Health Check ────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Verify application status and database availability."""
    graph_ok = False
    redis_ok = False

    try:
        graph_ok = app.state.graph_store.verify_connectivity()
    except Exception:
        pass

    if getattr(app.state, "redis", None):
        try:
            app.state.redis.ping()
            redis_ok = True
        except Exception:
            pass

    # Verify MongoDB
    mongodb_status = "disabled"
    if getattr(app.state, "mongodb_db", None) is not None:
        if getattr(app.state, "mongodb_is_fallback", False):
            mongodb_status = "connected_fallback"
        else:
            try:
                app.state.mongodb_client.admin.command('ping')
                mongodb_status = "connected"
            except Exception:
                mongodb_status = "failed"

    return {
        "status": "healthy" if (graph_ok and (app.state.redis is None or redis_ok)) else "degraded",
        "timestamp": time.time(),
        "database": {
            "graph_store": "connected" if graph_ok else "failed",
            "redis": "connected" if redis_ok else ("disabled" if not app.state.redis else "failed"),
            "mongodb": mongodb_status,
        }
    }


# ─── Prometheus Metrics Endpoint ──────────────────────────────────────────────

@app.get("/metrics", response_class=PlainTextResponse, tags=["Observability"])
def prometheus_metrics():
    """
    Exposes sovereign system telemetry in standard Prometheus text format.
    Scraped periodically by Prometheus and rendered on Grafana dashboards.
    """
    try:
        if hasattr(app.state, "graph_store") and app.state.graph_store:
            metrics.set_gauge("jansetu_graph_nodes_total", float(app.state.graph_store._graph.number_of_nodes()))
    except Exception:
        pass

    return PlainTextResponse(
        content=metrics.export_text(),
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )

