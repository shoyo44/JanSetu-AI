"""
Integration helper — adds citation verification as Stage 6 of the RAG pipeline.

This module provides a wrapper function that the pipeline can call after generation
to verify and annotate the response with grounding scores.

Usage inside RAGPipeline.query() (after Stage 5 Generate):

    from app.core.verification_integration import verify_and_annotate
    result = await verify_and_annotate(result, qualified, trace)
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List

from app.core.citation_verifier import CitationVerifier
from app.core.schemas import ChunkResult

logger = logging.getLogger("docqa.verification_integration")


async def verify_and_annotate(
    result: Dict[str, Any],
    chunks: List[ChunkResult],
    trace: Any,
) -> Dict[str, Any]:
    """
    Run citation entailment verification and annotate the pipeline result.

    Takes a pipeline result dict (the ``model_dump()`` of a ``VerticalOutput``)
    and the chunks used during generation, runs the ``CitationVerifier``, and
    adds grounding metadata to the result.

    Added / modified fields on *result*:
        - ``grounding_score``    (float)       — 0.0–1.0
        - ``unverified_claims``  (List[str])   — claims not entailed by any chunk
        - ``citation_verified``  (bool)        — True when grounding_score ≥ 0.70
        - ``_trace.stages.verification_ms`` (float) — wall-clock time for this stage

    Args:
        result: The mutable pipeline result dict to annotate.
        chunks: The ``ChunkResult`` objects used in context packing / generation.
        trace:  The ``PipelineTrace`` instance for the current query.

    Returns:
        The same *result* dict, now annotated with grounding fields.
    """
    loop = asyncio.get_running_loop()
    t0 = loop.time()

    answer = result.get("answer", "")

    # Skip verification for not-found / abstained responses
    if result.get("not_found") or result.get("abstained"):
        result["grounding_score"] = None
        result["unverified_claims"] = []
        result["citation_verified"] = None
        trace.record("verification_ms", (loop.time() - t0) * 1000)
        logger.debug("Skipping verification for not-found / abstained response.")
        return result

    try:
        verifier = CitationVerifier.get_instance()
        vr = await verifier.verify(answer, chunks)

        result["grounding_score"] = vr.grounding_score
        result["unverified_claims"] = vr.unverified_claims
        result["citation_verified"] = vr.citation_verified

        # Calibrated grounding guard: if citation verification fails, downgrade confidence to LOW
        if not vr.citation_verified and vr.grounding_score is not None and vr.grounding_score < 0.50:
            result["confidence"] = "LOW"
            logger.info("Calibrated confidence to LOW due to insufficient grounding (score=%.2f)", vr.grounding_score)

        # Attach detailed breakdown to trace metadata for diagnostics
        trace.add_meta("verification_total_claims", vr.total_claims)
        trace.add_meta("verification_verified_count", len(vr.verified_claims))
        trace.add_meta("verification_unverified_count", len(vr.unverified_claims))
        trace.add_meta("verification_claim_details", vr.claim_details)

        logger.info(
            "Citation verification complete: score=%.2f, verified=%d/%d, passed=%s",
            vr.grounding_score,
            len(vr.verified_claims),
            vr.total_claims,
            vr.citation_verified,
        )

    except Exception as exc:
        logger.error("Citation verification failed: %s", exc, exc_info=True)
        # On failure, don't block the response — mark as unverified
        result["grounding_score"] = None
        result["unverified_claims"] = []
        result["citation_verified"] = None
        trace.add_meta("verification_error", str(exc))

    elapsed_ms = (loop.time() - t0) * 1000
    trace.record("verification_ms", elapsed_ms)

    return result
