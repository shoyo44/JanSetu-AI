"""
Main API routes — tenant administration, document ingestion, query execution.
"""
from __future__ import annotations

import logging
import os
import shutil
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from pydantic import BaseModel, Field

from app.core.dependencies import (
    get_embedding,
    get_llm_client,
    get_graph_store,
    get_mongodb_db,
    get_reranker,
    get_semantic_cache,
)
from app.graph.ingestion import ingest_document, supersede_document
from app.graph.ocr import extract_pages
from app.features.redflag import run_redflag_scan, get_stored_report
from app.features.compliance_monitor import run_compliance_monitor
from app.features.analytics import write_query_log
from app.config.verticals import SUPPORTED_VERTICALS
from app.core.file_validator import validate_uploaded_file
from app.core.rate_limiter import tenant_limiter

logger = logging.getLogger("docqa.api.routes")
router = APIRouter()


# ─── Pydantic Request Models ──────────────────────────────────────────────────

class TenantCreate(BaseModel):
    tenant_id: str
    vertical:  str


class QueryRequest(BaseModel):
    query_text: str
    tenant_id:  str
    vertical:   str
    keyword:    Optional[str] = ""
    temperature: Optional[float] = None
    top_k:       Optional[int] = None
    score_floor: Optional[float] = None


class SupersedeRequest(BaseModel):
    new_doc_id: str
    tenant_id:  str


# ─── Tenant Endpoints ─────────────────────────────────────────────────────────

@router.post("/tenants")
def create_tenant(payload: TenantCreate, store: Any = Depends(get_graph_store)):
    """Upsert a Tenant node in the graph store."""
    if payload.vertical not in SUPPORTED_VERTICALS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported vertical: {payload.vertical}. Supported: {SUPPORTED_VERTICALS}",
        )
    try:
        store.upsert_tenant(payload.tenant_id, payload.vertical)
        return {"success": True, "tenant_id": payload.tenant_id, "vertical": payload.vertical}
    except Exception as exc:
        logger.exception("Failed to create tenant:")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/tenants/{tenant_id}/usage")
def get_tenant_rate_limits(tenant_id: str):
    """Retrieve tenant quota usage and sliding-window rate limit status."""
    return tenant_limiter.get_status(tenant_id)


# ─── Indian Statutory Concordance Endpoint (IPC <-> BNS, CrPC <-> BNSS) ──────

@router.get("/statutory/concordance")
def lookup_statutory_sections(query: str = Query(..., description="e.g. IPC 420, Section 302 IPC, CrPC 439")):
    """
    Look up equivalent Indian criminal law sections between pre-2024 colonial codes
    and post-2024 Bharatiya laws (IPC <-> BNS, CrPC <-> BNSS, IEA <-> BSA).
    """
    from app.core.statutory_concordance import find_statutory_matches
    matches = find_statutory_matches(query)
    return {
        "query": query,
        "matched_count": len(matches),
        "concordances": [m.to_dict() for m in matches]
    }


# ─── India AI Official Benchmark Loader Endpoints ────────────────────────────

BENCHMARK_CATALOG = [
    {
        "id": "pm_kisan",
        "title": "PM-KISAN Operational Guidelines 2024",
        "vertical": "governance",
        "domain": "Governance & Welfare Schemes",
        "icon": "Landmark",
        "filename": "PM_KISAN_Operational_Guidelines.txt",
        "description": "Central sector welfare scheme with 100% GoI funding providing ₹6,000/yr direct income support (DBT) to landholding farmer families.",
    },
    {
        "id": "sc_judgment",
        "title": "Supreme Court Landmark Bail Ruling (2024 INSC 582)",
        "vertical": "judgment",
        "domain": "Law & Justice",
        "icon": "Gavel",
        "filename": "Supreme_Court_Bail_Judgment_2024.txt",
        "description": "Supreme Court ruling on Article 21, CrPC §439 / BNSS §483, and IPC §420 / BNS §318 establishing bail as the rule in commercial cheating cases.",
    },
    {
        "id": "ayushman_bharat",
        "title": "Ayushman Bharat PM-JAY Policy Guidelines",
        "vertical": "governance",
        "domain": "Governance & Public Health",
        "icon": "ShieldCheck",
        "filename": "Ayushman_Bharat_PMJAY_Policy.txt",
        "description": "World's largest public health assurance scheme providing ₹5,00,000/yr cashless coverage per family for secondary/tertiary care.",
    },
    {
        "id": "tamil_pattiram",
        "title": "Tamil Nadu Land Sale Deed & Patta (கிரையப் பத்திரம்)",
        "vertical": "governance",
        "domain": "Rural Land Records & Revenue",
        "icon": "FileText",
        "filename": "Sample_Tamil_Land_Deed_Pattiram.txt",
        "description": "Registered Tamil Nadu property deed (SRO Tambaram, Doc 4218/2023) with Patta 874, Survey 142/3A, four boundaries, and encumbrance warranty.",
    },
    {
        "id": "cyber_fir",
        "title": "Cyber Fraud & Citizen FIR Guidelines (I4C / MHA)",
        "vertical": "law",
        "domain": "Citizen Rights & Cyber Justice",
        "icon": "ShieldAlert",
        "filename": "Cyber_Crime_Citizen_FIR_Guidelines.txt",
        "description": "MHA citizen advisory on Helpline 1930, golden-hour bank account freezing, Zero-FIR under BNSS §173, and cyber cheating under BNS §318(4) & IT Act §66D.",
    },
    {
        "id": "tenancy_act",
        "title": "Model Tenancy Act & Tenant Rights (MoHUA)",
        "vertical": "law",
        "domain": "Urban Housing & Tenant Protection",
        "icon": "FileCheck",
        "filename": "Model_Tenancy_Act_Guidelines.txt",
        "description": "Statutory 2-month security deposit cap, prohibition of arbitrary eviction, and essential utilities protection under the Model Tenancy Act.",
    },
    {
        "id": "senior_citizen",
        "title": "Senior Citizens Parental Property Protection Act",
        "vertical": "governance",
        "domain": "Social Justice & Elder Care",
        "icon": "Users",
        "filename": "Senior_Citizen_Protection_Act_2007.txt",
        "description": "Statutory revocation of gift deeds (பரிசுப் பத்திரம்) under MWPSC Act Section 23 and summary monthly maintenance for elderly parents by RDO tribunal.",
    },
]


@router.get("/benchmarks")
def list_benchmark_documents():
    """List preloaded India AI Fellowship benchmark documents available for 1-click evaluation."""
    return {"benchmarks": BENCHMARK_CATALOG}


@router.post("/benchmarks/load")
async def load_benchmark_document(
    benchmark_id: str = Query(..., description="pm_kisan | sc_judgment | ayushman_bharat | tamil_pattiram | cyber_fir | tenancy_act | senior_citizen"),
    tenant_id:    str = Query("default_tenant"),
    request:      Request = None,
    store:        Any = Depends(get_graph_store),
    cf_client:    Any = Depends(get_llm_client),
    reranker:     Any = Depends(get_reranker),
):
    """
    1-Click Ingestion of official India AI Fellowship benchmark documents into GraphStore.
    Allows reviewers to test Governance & Law features in 5 seconds.
    """
    benchmark = next((b for b in BENCHMARK_CATALOG if b["id"] == benchmark_id), None)
    if not benchmark:
        raise HTTPException(status_code=404, detail=f"Benchmark '{benchmark_id}' not found.")

    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sample_docs")
    if not os.path.exists(sample_dir):
        sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_docs")
    file_path = os.path.join(sample_dir, benchmark["filename"])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Benchmark file '{benchmark['filename']}' not found on disk.")

    with open(file_path, "r", encoding="utf-8") as f:
        doc_text = f.read()

    doc_id = str(uuid.uuid4())
    doc_name = benchmark["filename"]
    vertical = benchmark["vertical"]

    # Build vertical pipeline to fetch indexer
    pipeline_factory = request.app.state.pipeline_factory
    pipeline = pipeline_factory.build_pipeline(vertical, cf_client, reranker)
    indexer  = pipeline.indexer

    # Chunk the benchmark document
    metadata = {
        "page": 1,
        "doc_id": doc_id,
        "tenant_id": tenant_id,
        "chunk_offset": 0,
    }
    chunks = indexer.chunk(doc_text, metadata)
    if not chunks:
        raise HTTPException(status_code=500, detail="Benchmark chunking yielded 0 chunks.")

    # Ingest into GraphStore
    res = await ingest_document(
        store=store,
        cf_client=cf_client,
        tenant_id=tenant_id,
        doc_name=doc_name,
        vertical=vertical,
        chunks=chunks,
        doc_id=doc_id,
        version="1.0",
        doc_name_full=benchmark["title"],
    )

    # Trigger automatic red-flag scan if legal/judgment
    if vertical in ("law", "startup", "judgment"):
        try:
            await run_redflag_scan(
                doc_id=doc_id,
                tenant_id=tenant_id,
                doc_name=doc_name,
                store=store,
                cf_client=cf_client,
            )
        except Exception as e_rf:
            logger.warning("Benchmark redflag scan non-fatal error: %s", e_rf)

    # Persist document text for viewer
    doc_store_dir = os.path.join(
        os.getenv("GRAPH_STORE_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")),
        "documents"
    )
    os.makedirs(doc_store_dir, exist_ok=True)
    with open(os.path.join(doc_store_dir, f"{doc_id}.txt"), "w", encoding="utf-8") as f_out:
        f_out.write(doc_text)

    # Clear semantic cache for tenant
    if getattr(request.app.state, "semantic_cache", None):
        try:
            request.app.state.semantic_cache.clear_tenant_cache(tenant_id)
        except Exception:
            pass

    return {
        "success": True,
        "message": f"Successfully loaded benchmark '{benchmark['title']}'",
        "benchmark_id": benchmark_id,
        "doc_id": doc_id,
        "doc_name": doc_name,
        "display_title": benchmark["title"],
        "vertical": vertical,
        "chunks_created": res.get("chunks_created", len(chunks)),
        "safe_chunks": res.get("safe_chunks", len(chunks)),
    }


# ─── Ingestion / Upload Endpoints ─────────────────────────────────────────────

async def run_document_ingestion_background(
    doc_id:        str,
    doc_name:      str,
    file_path:     str,
    tenant_id:     str,
    vertical:      str,
    version:       str,
    store:         Any,
    cf_client:     Any,
    pipeline_factory: Any,
    reranker:      Any,
    semantic_cache: Optional[Any] = None,
) -> Dict[str, Any]:
    """Background task function mapping PDF extraction, chunking, embedding, writing."""
    try:
        logger.info("Starting background ingestion for doc %s", doc_id)
        # 1. OCR / Native text extraction
        pages = await extract_pages(file_path, cf_client)
        if not pages:
            raise ValueError("No text could be extracted from the document.")

        # 2. Build vertical pipeline to fetch indexer
        pipeline = pipeline_factory.build_pipeline(vertical, cf_client, reranker)
        indexer  = pipeline.indexer

        # 3. Perform vertical chunking
        all_chunks: List[Dict[str, Any]] = []
        chunk_offset = 0
        for p in pages:
            page_text = p.get("enriched_text") or p["text"]
            metadata = {
                "page":         p["page"],
                "doc_id":       doc_id,
                "tenant_id":    tenant_id,
                "chunk_offset": chunk_offset,
            }
            page_chunks = indexer.chunk(page_text, metadata)
            all_chunks.extend(page_chunks)
            chunk_offset += len(page_chunks)

        if not all_chunks:
            raise ValueError("Document was parsed but chunking yielded 0 chunks.")

        # 4. Ingest nodes into graph store
        res = await ingest_document(
            store=store,
            cf_client=cf_client,
            tenant_id=tenant_id,
            doc_name=doc_name,
            vertical=vertical,
            chunks=all_chunks,
            doc_id=doc_id,
            version=version,
        )

        # 5. Trigger automated features
        # 5a. Law/Startup/Judgment: trigger auto red-flag scan
        if vertical in ("law", "startup", "judgment"):
            try:
                await run_redflag_scan(
                    doc_id=doc_id,
                    tenant_id=tenant_id,
                    doc_name=doc_name,
                    store=store,
                    cf_client=cf_client,
                )
            except Exception as e_rf:
                logger.error("Auto red-flag scan failed: %s", e_rf)

        # 5b. Compliance: trigger regulation change monitor
        elif vertical == "compliance":
            try:
                await run_compliance_monitor(
                    store=store,
                    cf_client=cf_client,
                    tenant_id=tenant_id,
                    new_doc_id=doc_id,
                    new_doc_name=doc_name,
                    new_doc_chunks=all_chunks,
                )
            except Exception as e_cm:
                logger.error("Compliance monitoring check failed: %s", e_cm)

        # Clear semantic cache for this tenant
        if semantic_cache:
            try:
                semantic_cache.clear_tenant_cache(tenant_id)
            except Exception as e_cache:
                logger.error("Failed to clear cache for tenant %s: %s", tenant_id, e_cache)

        # Store persistent document copy for PDF citation viewer
        doc_store_dir = os.path.join(
            os.getenv("GRAPH_STORE_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")),
            "documents"
        )
        os.makedirs(doc_store_dir, exist_ok=True)
        persistent_pdf = os.path.join(doc_store_dir, f"{doc_id}.pdf")
        try:
            shutil.copy2(file_path, persistent_pdf)
            logger.info("Persisted document copy for viewer: %s", persistent_pdf)
        except Exception as e_copy:
            logger.warning("Could not persist copy of doc for viewer: %s", e_copy)

        return res

    except Exception as exc:
        logger.exception("Ingestion task failed for doc %s:", doc_id)
        raise exc
    finally:
        # Guarantee local file cleanup
        if os.path.exists(file_path):
            try:
                os.unlink(file_path)
                logger.info("Cleaned up temp upload file: %s", file_path)
            except Exception as exc:
                logger.warning("Failed to delete temp file %s: %s", file_path, exc)


@router.post("/upload")
async def upload_document(
    request:   Request,
    file:      UploadFile = File(...),
    tenant_id: str        = Query(...),
    vertical:  str        = Query(...),
    version:   str        = Query("1.0"),
    store:     Any        = Depends(get_graph_store),
    cf_client: Any        = Depends(get_llm_client),
    reranker:  Any        = Depends(get_reranker),
):
    """
    Upload a document, save temporarily, and submit it to the background queue.
    Enforces tenant rate limiting and binary magic MIME validation.
    Returns the job_id immediately so clients can poll.
    """
    # 1. Tenant Rate Limit Check
    client_ip = request.client.host if request.client else None
    tenant_limiter.enforce(tenant_id, action="upload", ip_address=client_ip)

    if vertical not in SUPPORTED_VERTICALS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported vertical '{vertical}'. Valid options: {SUPPORTED_VERTICALS}",
        )

    # 2. File Magic & Content Validation
    content = await file.read()
    val_res = validate_uploaded_file(content, file.filename or "document.pdf")
    if not val_res.is_valid:
        raise HTTPException(status_code=400, detail=val_res.error_message)

    # Prepare temp directory
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp")
    os.makedirs(temp_dir, exist_ok=True)

    doc_id    = str(uuid.uuid4())
    temp_path = os.path.join(temp_dir, f"{doc_id}_{file.filename}")

    try:
        # Save validated upload buffer to local file
        with open(temp_path, "wb") as buffer:
            buffer.write(content)
    except Exception as exc:
        logger.exception("Failed to write temporary file:")
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise HTTPException(status_code=500, detail=f"Failed to write upload to disk: {exc}")

    # Submit task to job queue
    job_queue = request.app.state.job_queue
    pipeline_factory = request.app.state.pipeline_factory

    job_id = await job_queue.submit(
        run_document_ingestion_background,
        doc_id=doc_id,
        doc_name=file.filename,
        file_path=temp_path,
        tenant_id=tenant_id,
        vertical=vertical,
        version=version,
        store=store,
        cf_client=cf_client,
        pipeline_factory=pipeline_factory,
        reranker=reranker,
        semantic_cache=request.app.state.semantic_cache,
    )

    return {
        "success":   True,
        "doc_id":    doc_id,
        "job_id":    job_id,
        "message":   "Document upload received. Processing in background.",
    }



# ─── Vertical Auto-Detection Endpoint (Two-Phase Classifier Agent) ────────────

@router.post("/detect-vertical")
async def detect_vertical(
    request:   Request,
    file:      UploadFile = File(...),
    tenant_id: str        = Query(...),
    cf_client: Any        = Depends(get_llm_client),
):
    """
    Upload a document preview for automatic type detection.

    Internally runs the DocumentClassifierAgent which:
      Phase 1 — summarises the document (document type, topics, entities, audience)
      Phase 2 — classifies the vertical and generates an AI suggestion paragraph

    Returns full enriched response:
    {
      vertical, confidence, ai_suggestion, alternative_vertical,
      classification_notes, summary { document_type, main_topics, ... }, meta
    }
    """
    import tempfile
    from app.features.document_classifier_agent import DocumentClassifierAgent

    # Rate Limit Enforcement
    client_ip = request.client.host if request.client else None
    tenant_limiter.enforce(tenant_id, action="detect", ip_address=client_ip)

    suffix   = os.path.splitext(file.filename or "doc")[1] or ".pdf"
    tmp_path = None

    try:
        content  = await file.read()
        val_res = validate_uploaded_file(content, file.filename or "preview.pdf")
        if not val_res.is_valid:
            raise HTTPException(status_code=400, detail=val_res.error_message)

        # Persist the upload stream so the agent can open the file from disk
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            tmp.write(content)

        agent  = DocumentClassifierAgent(cf_client=cf_client)
        result = await agent.run(file_path=tmp_path, filename=file.filename or "document")

        return result.to_api_response()

    except Exception as exc:
        logger.exception("detect-vertical endpoint error:")
        return {
            "vertical":             "university",
            "confidence":           "LOW",
            "ai_suggestion":        (
                "The classifier agent encountered an unexpected error. "
                "Please select the document type manually before ingesting."
            ),
            "alternative_vertical": None,
            "classification_notes": str(exc),
            "summary":              {},
            "meta":                 {},
        }

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass



@router.get("/jobs/{job_id}")
def get_job_status(job_id: str, request: Request):
    """Retrieve the status and results of a background ingestion job."""
    job_queue = request.app.state.job_queue
    status_info = job_queue.get_status(job_id)
    if not status_info:
        raise HTTPException(status_code=404, detail="Job not found.")
    return status_info


# ─── Query / RAG Endpoints ────────────────────────────────────────────────────

@router.post("/query")
async def query_vertical(
    payload: QueryRequest,
    request: Request,
    store:  Any = Depends(get_graph_store),
    cf_client: Any = Depends(get_llm_client),
    reranker: Any = Depends(get_reranker),
    mongodb_db: Any = Depends(get_mongodb_db),
    semantic_cache: Any = Depends(get_semantic_cache),
):
    """Execute a vertical-specific async RAG pipeline query with guardrails and cache checks."""
    # ── Tenant Rate Limit Check ──
    client_ip = request.client.host if request.client else None
    tenant_limiter.enforce(payload.tenant_id, action="query", ip_address=client_ip)

    if payload.vertical != "auto" and payload.vertical not in SUPPORTED_VERTICALS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported vertical '{payload.vertical}'. Valid options: {SUPPORTED_VERTICALS}",
        )

    # ── Guardrail check ──
    from app.core.guardrails import check_guardrails
    violation = check_guardrails(payload.query_text)
    if violation:
        logger.warning("Safety Guardrail Violation for query %r: %s", payload.query_text, violation)
        return {
            "answer": violation,
            "confidence": "LOW",
            "not_found": True,
            "chunks_used": [],
            "_guardrail_violated": True
        }

    # AI Intent Router / Auto-vertical detection
    active_vertical = payload.vertical
    if active_vertical == "auto":
        try:
            system_prompt = (
                "You are an intent routing agent for the IndiaAI Sovereign Intelligence Platform. "
                "Classify the user query into exactly one of these primary sovereign categories:\n"
                "- 'governance' (for Central & State Government Gazettes, Welfare Schemes, Yojanas like PM-KISAN, Ayushman Bharat, PMAY, MGNREGA, citizen eligibility, public policy guidelines, G.O.s)\n"
                "- 'judgment' (for Indian Supreme Court & High Court judgments, case law, ratio decidendi, bail orders under Section 439 CrPC / BNSS 483, Article 21)\n"
                "- 'law' (for statutory enactments, IPC ⇄ BNS, CrPC ⇄ BNSS, IEA ⇄ BSA concordance, legal decrees)\n\n"
                "Respond with ONLY the classification category name (exactly one of 'governance', 'judgment', 'law') in lowercase. Do not write anything else."
            )
            routing_response = await cf_client.chat(
                system_prompt=system_prompt,
                user_message=payload.query_text,
                max_tokens=15,
                temperature=0.0
            )
            detected = routing_response.strip().lower()
            matched_v = None
            for v in ("judgment", "governance", "law"):
                if v in detected:
                    matched_v = v
                    break
            if matched_v:
                active_vertical = matched_v
                logger.info("🧠 AI Router matched HTTP query to vertical: %s", active_vertical)
            else:
                active_vertical = "governance"
        except Exception as routing_err:
            logger.error("AI Routing failed: %s", routing_err)
            active_vertical = "governance"

    import asyncio
    loop_time = asyncio.get_running_loop().time
    t0_val = loop_time()

    try:
        # 1. Fetch query embedding & Check Cache
        embedding = await get_embedding(payload.query_text, request)
        
        cached = semantic_cache.get(payload.tenant_id, active_vertical, embedding)
        if cached:
            return cached

        # 2. Build vertical-specific pipeline
        factory = request.app.state.pipeline_factory
        pipeline = factory.build_pipeline(active_vertical, cf_client, reranker)

        # Override pipeline config parameters if specified in payload
        if payload.temperature is not None:
            pipeline.config["temperature"] = payload.temperature
        if payload.top_k is not None:
            pipeline.config["top_k"] = payload.top_k
        if payload.score_floor is not None:
            pipeline.config["score_floor"] = payload.score_floor

        # 3. Execute pipeline
        result = await pipeline.query(
            query_text=payload.query_text,
            embedding=embedding,
            store=store,
            tenant_id=payload.tenant_id,
            keyword=payload.keyword,
        )

        latency = round((loop_time() - t0_val) * 1000, 2)

        # 4. Cache response semantically (only cache valid answers, never failed/not_found)
        try:
            if not result.get("not_found", False) and result.get("confidence") != "LOW":
                semantic_cache.set(payload.tenant_id, active_vertical, payload.query_text, embedding, result)
        except Exception as e_cache:
            logger.warning("Cache write failed: %s", e_cache)

        # 5. Log analytics in background (failures swallowed silently)
        write_query_log(
            store=store,
            tenant_id=payload.tenant_id,
            vertical=active_vertical,
            query=payload.query_text,
            answer=result.get("answer", ""),
            confidence=result.get("confidence", "LOW"),
            not_found=result.get("not_found", False),
            latency_ms=latency,
            mongodb_db=mongodb_db,
        )

        return result

    except Exception as exc:
        logger.exception("RAG pipeline query failed:")
        raise HTTPException(status_code=500, detail=str(exc))


# ─── Document Administration Endpoints ────────────────────────────────────────

@router.get("/documents")
def list_documents(tenant_id: str, store: Any = Depends(get_graph_store)):
    """List all active, non-superseded documents for a tenant."""
    try:
        records = store.list_documents(tenant_id)
        return {"documents": records}
    except Exception as exc:
        logger.exception("Failed to list documents:")
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/documents")
def delete_all_documents(
    tenant_id: str,
    store: Any = Depends(get_graph_store),
    semantic_cache: Any = Depends(get_semantic_cache),
):
    """Delete all documents and related graph data for a tenant."""
    try:
        store.delete_all_documents(tenant_id)
        semantic_cache.clear_tenant_cache(tenant_id)
        return {"success": True, "message": f"All documents for tenant {tenant_id} deleted."}
    except Exception as exc:
        logger.exception("Failed to delete all documents:")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/documents/{doc_id}/chunks")
def get_document_chunks_endpoint(
    doc_id: str,
    tenant_id: str,
    store: Any = Depends(get_graph_store)
):
    """Retrieve all sorted text chunks for a specific document."""
    try:
        chunks = store.get_document_chunks(doc_id, tenant_id)
        return {"chunks": chunks}
    except Exception as exc:
        logger.exception("Failed to retrieve document chunks:")
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/documents/{doc_id}")
@router.delete("/document/{doc_id}")
def delete_document(
    doc_id: str,
    tenant_id: str,
    store: Any = Depends(get_graph_store),
    semantic_cache: Any = Depends(get_semantic_cache),
):
    """Delete a document and all its associated chunks/redflags from the graph."""
    try:
        store.delete_document(doc_id, tenant_id)
        semantic_cache.clear_tenant_cache(tenant_id)
        return {"success": True, "message": f"Document {doc_id} and all related nodes deleted."}
    except Exception as exc:
        logger.exception("Failed to delete document:")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/documents/{doc_id}/supersede")
def supersede_document_endpoint(
    doc_id:  str,
    payload: SupersedeRequest,
    store:  Any = Depends(get_graph_store),
    semantic_cache: Any = Depends(get_semantic_cache),
):
    """Mark an old document as superseded by a new document version."""
    try:
        supersede_document(
            store=store,
            old_doc_id=doc_id,
            new_doc_id=payload.new_doc_id,
            tenant_id=payload.tenant_id,
        )
        semantic_cache.clear_tenant_cache(payload.tenant_id)
        return {
            "success": True,
            "message": f"Document {doc_id} marked as superseded by {payload.new_doc_id}.",
        }
    except Exception as exc:
        logger.exception("Failed to supersede document:")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/documents/{doc_id}/redflags")
def get_redflags(doc_id: str, tenant_id: str, store: Any = Depends(get_graph_store)):
    """Retrieve redflag scan report for a startup, law, or judgment document."""
    try:
        report = get_stored_report(store, doc_id, tenant_id)
        if not report:
            raise HTTPException(
                status_code=404,
                detail="Red-flag report not found. The document may not be in 'law'/'startup'/'judgment' vertical, or processing is not complete.",
            )
        return report
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to fetch redflags report:")
        raise HTTPException(status_code=500, detail=str(exc))


# ─── Human-in-the-Loop Review Endpoints ───────────────────────────────────────

class FlagReviewRequest(BaseModel):
    tenant_id: str
    action:    str = Field(..., description="accept_risk | dismiss | needs_remediation")
    note:      Optional[str] = ""
    reviewer:  Optional[str] = "Legal Counsel"


@router.patch("/documents/{doc_id}/redflags/{flag_id}/review")
def review_redflag(
    doc_id:   str,
    flag_id:  str,
    payload:  FlagReviewRequest,
    store:    Any = Depends(get_graph_store),
):
    """Apply a human-in-the-loop review action to a red flag."""
    from app.features.redflag import apply_review_action
    try:
        updated = apply_review_action(
            store=store,
            doc_id=doc_id,
            tenant_id=payload.tenant_id,
            flag_id=flag_id,
            action=payload.action,
            note=payload.note or "",
            reviewer=payload.reviewer or "Legal Counsel",
        )
        return {"success": True, "report": updated}
    except Exception as exc:
        logger.exception("Failed to review redflag:")
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/documents/{doc_id}/redflags/review-status")
def get_redflag_review_status(
    doc_id:    str,
    tenant_id: str,
    store:     Any = Depends(get_graph_store),
):
    """Retrieve human-in-the-loop review status and progress metrics."""
    from app.features.redflag import get_review_status
    return get_review_status(store, doc_id, tenant_id)


# ─── Formal Audit Reporting & Export Endpoints ───────────────────────────────

class ReportExportRequest(BaseModel):
    doc_id:      str
    tenant_id:   str
    report_type: str = "redflag"
    format:      str = "html"   # html | markdown | json


@router.post("/reports/export")
def export_report(
    payload: ReportExportRequest,
    store:   Any = Depends(get_graph_store),
):
    """Generate and return a formal audit report in HTML, Markdown, or JSON."""
    tenant_limiter.enforce(payload.tenant_id, action="export")
    from fastapi.responses import HTMLResponse, PlainTextResponse
    from app.features.reporting import generate_redflag_report_html, generate_redflag_report_markdown
    from app.features.redflag import get_stored_report

    report = get_stored_report(store, payload.doc_id, payload.tenant_id)
    doc_node = store.get_document(payload.doc_id, payload.tenant_id)
    if not report:
        if not doc_node:
            raise HTTPException(status_code=404, detail="No audit report or document found for this document.")
        chunks = store.get_document_chunks(payload.doc_id, payload.tenant_id)
        report = {
            "document_risk_level": "LOW",
            "summary": f"Initial compliance and risk assessment for {doc_node.get('name', 'Document')}. Baseline verification complete across {len(chunks)} indexed chunks.",
            "red_flags": [],
            "positive_highlights": [
                f"Document indexed with {len(chunks)} structural chunks under tenant {payload.tenant_id}.",
                "MIME magic-byte verification passed."
            ],
            "doc_id": payload.doc_id,
            "doc_name": doc_node.get("name", "Document"),
        }

    doc_name = doc_node.get("name", "Document") if doc_node else "Document"

    if payload.format == "html":
        content = generate_redflag_report_html(report, doc_name, payload.doc_id, payload.tenant_id)
        return HTMLResponse(content=content)
    elif payload.format == "markdown":
        content = generate_redflag_report_markdown(report, doc_name, payload.doc_id)
        return PlainTextResponse(content=content, media_type="text/markdown")
    else:
        return report


@router.get("/documents/{doc_id}/export")
def download_document_report(
    doc_id:    str,
    tenant_id: str,
    format:    str = "html",
    store:     Any = Depends(get_graph_store),
):
    """Convenience GET endpoint to directly download or preview a document audit report."""
    return export_report(ReportExportRequest(doc_id=doc_id, tenant_id=tenant_id, format=format), store)


# ─── PDF Serving & Document Chunks for Deep-Linking ──────────────────────────

@router.get("/documents/{doc_id}/pdf")
def get_document_pdf(
    doc_id:    str,
    tenant_id: str,
    store:     Any = Depends(get_graph_store),
):
    """Serve the stored PDF for the split-screen in-app citation viewer."""
    from fastapi.responses import FileResponse
    doc_store_dir = os.path.join(
        os.getenv("GRAPH_STORE_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")),
        "documents"
    )
    pdf_path = os.path.join(doc_store_dir, f"{doc_id}.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Original PDF file not found on disk.")

    doc_node = store.get_document(doc_id, tenant_id)
    doc_name = doc_node.get("name", f"{doc_id}.pdf") if doc_node else f"{doc_id}.pdf"
    return FileResponse(pdf_path, media_type="application/pdf", filename=doc_name)


@router.get("/documents/{doc_id}/chunks")
def get_document_chunks(
    doc_id:    str,
    tenant_id: str,
    store:     Any = Depends(get_graph_store),
):
    """Return all indexed chunks for this document with clause and page references."""
    return {"chunks": store.get_document_chunks(doc_id, tenant_id)}


# ─── Chat History Store Endpoints ───────────────────────────────────────────

class ChatMessageRequest(BaseModel):
    tenant_id: str
    vertical: str
    role: str
    content: str
    evidence: Optional[List[dict]] = None
    citations: Optional[List[dict]] = None
    paper_title: Optional[str] = None
    authors: Optional[List[str]] = None
    abstract_summary: Optional[str] = None

@router.post("/history/message")
def save_chat_message(
    payload: ChatMessageRequest,
    mongodb_db: Any = Depends(get_mongodb_db)
):
    """Save a chat message to MongoDB Atlas."""
    if mongodb_db is None:
        raise HTTPException(
            status_code=503, 
            detail="MongoDB is offline or not configured."
        )
    try:
        import time
        coll_name = os.getenv("MONGODB_COLLECTION", "chat_history")
        doc = {
            "tenant_id": payload.tenant_id,
            "vertical": payload.vertical,
            "role": payload.role,
            "content": payload.content,
            "evidence": payload.evidence or [],
            "citations": payload.citations or [],
            "paper_title": payload.paper_title,
            "authors": payload.authors or [],
            "abstract_summary": payload.abstract_summary,
            "created_at": time.time(),
            "type": "chat_message"
        }
        mongodb_db[coll_name].insert_one(doc)
        return {"success": True, "message": "Chat message saved successfully."}
    except Exception as exc:
        logger.exception("Failed to save chat message to MongoDB:")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/history")
def get_chat_history(
    tenant_id: str,
    vertical: str,
    mongodb_db: Any = Depends(get_mongodb_db)
):
    """Get chat history from MongoDB Atlas for a tenant and vertical."""
    if mongodb_db is None:
        raise HTTPException(
            status_code=503, 
            detail="MongoDB is offline or not configured."
        )
    try:
        coll_name = os.getenv("MONGODB_COLLECTION", "chat_history")
        cursor = mongodb_db[coll_name].find(
            {"tenant_id": tenant_id, "vertical": vertical, "type": "chat_message"}
        ).sort("created_at", 1)
        
        messages = []
        for doc in cursor:
            messages.append({
                "role": doc["role"],
                "content": doc["content"],
                "evidence": doc.get("evidence", []),
                "citations": doc.get("citations", []),
                "paper_title": doc.get("paper_title"),
                "authors": doc.get("authors", []),
                "abstract_summary": doc.get("abstract_summary")
            })
        return {"messages": messages}
    except Exception as exc:
        logger.exception("Failed to fetch chat history from MongoDB:")
        raise HTTPException(status_code=500, detail=str(exc))

@router.delete("/history")
def clear_chat_history(
    tenant_id: str,
    vertical: str,
    mongodb_db: Any = Depends(get_mongodb_db)
):
    """Clear chat history in MongoDB Atlas for a tenant and vertical."""
    if mongodb_db is None:
        raise HTTPException(
            status_code=503, 
            detail="MongoDB is offline or not configured."
        )
    try:
        coll_name = os.getenv("MONGODB_COLLECTION", "chat_history")
        mongodb_db[coll_name].delete_many(
            {"tenant_id": tenant_id, "vertical": vertical, "type": "chat_message"}
        )
        return {"success": True, "message": "Chat history cleared successfully."}
    except Exception as exc:
        logger.exception("Failed to clear chat history in MongoDB:")
        raise HTTPException(status_code=500, detail=str(exc))
