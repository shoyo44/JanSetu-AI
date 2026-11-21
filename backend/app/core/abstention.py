"""
Calibrated Abstention Engine — decides when the pipeline should refuse to answer.

Uses per-vertical confidence thresholds on retrieval scores to determine
whether retrieved chunks are relevant enough to generate a trustworthy answer.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.core.schemas import ChunkResult


# ── Per-vertical abstention thresholds ────────────────────────────────────────

ABSTENTION_THRESHOLDS: Dict[str, Dict[str, Any]] = {
    "governance": {"min_top_score": 0.50, "min_qualified_count": 2, "min_mean_score": 0.42},
    "judgment":   {"min_top_score": 0.50, "min_qualified_count": 2, "min_mean_score": 0.42},
    "law":        {"min_top_score": 0.50, "min_qualified_count": 2, "min_mean_score": 0.42},
    "generic":    {"min_top_score": 0.45, "min_qualified_count": 2, "min_mean_score": 0.38},
}


def should_abstain(
    chunks: List[ChunkResult],
    vertical: str,
) -> Tuple[bool, str, Dict[str, Any]]:
    """Decide whether the pipeline should refuse to answer.

    Returns:
        (should_abstain, reason, diagnostics)
        *diagnostics* always contains ``top_score``, ``mean_score``,
        ``qualified_count``, and ``threshold_used``.
    """
    thresholds = ABSTENTION_THRESHOLDS.get(vertical, ABSTENTION_THRESHOLDS["generic"])

    min_top_score      = thresholds["min_top_score"]
    min_qualified_count = thresholds["min_qualified_count"]
    min_mean_score     = thresholds["min_mean_score"]

    scores = [c.best_score for c in chunks] if chunks else []
    top_score  = max(scores) if scores else 0.0
    mean_score = sum(scores) / len(scores) if scores else 0.0

    # "qualified" here means chunks whose score meets the mean-score bar
    qualified_count = sum(1 for s in scores if s >= min_mean_score)

    diagnostics: Dict[str, Any] = {
        "top_score":        round(top_score, 4),
        "mean_score":       round(mean_score, 4),
        "qualified_count":  qualified_count,
        "threshold_used":   thresholds,
    }

    # Abstain if top score is too low
    if top_score < min_top_score:
        reason = (
            f"Top retrieval score ({top_score:.3f}) is below the "
            f"{vertical} threshold ({min_top_score:.2f})."
        )
        return True, reason, diagnostics

    # Abstain if not enough chunks qualify
    effective_min_count = min(min_qualified_count, len(chunks)) if chunks else min_qualified_count
    if qualified_count < effective_min_count:
        reason = (
            f"Only {qualified_count} chunk(s) met the quality bar "
            f"(need {effective_min_count} with score >= {min_mean_score:.2f})."
        )
        return True, reason, diagnostics

    return False, "", diagnostics


def build_abstention_response(
    reason: str,
    diagnostics: Dict[str, Any],
    chunks: List[ChunkResult],
    vertical: str,
) -> Dict[str, Any]:
    """Build a structured response dict for an abstention event.

    Includes pointers to the nearest topics found in the top-3 chunks so the
    caller can suggest what *was* available.
    """
    nearest_topics: List[str] = []
    for chunk in chunks[:3]:
        for attr in ("chunk_type", "clause_ref", "article_ref", "section"):
            value = getattr(chunk, attr, None)
            if value and value not in nearest_topics:
                nearest_topics.append(value)

    return {
        "answer": (
            "The information you requested was not found in the provided documents. "
            "The system's confidence in the available context was insufficient to "
            "generate a reliable answer."
        ),
        "confidence":              "LOW",
        "not_found":               True,
        "abstained":               True,
        "abstention_reason":       reason,
        "abstention_diagnostics":  diagnostics,
        "nearest_topics":          nearest_topics,
        "chunks_used":             [],
    }
