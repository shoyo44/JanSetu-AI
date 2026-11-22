"""
Pipeline Factory — assembles a RAGPipeline for a given vertical.

KEY FIX over original:
    build_pipeline() now accepts pre-built singleton objects (reranker, llm_client)
    instead of constructing them internally on every call.

    Original bug:
        CrossEncoderReranker() was constructed INSIDE build_pipeline() →
        the ~80MB sentence-transformer model was loaded on EVERY request.
        At ~2–5s load time, this made every query feel cold.

    Fix:
        Reranker and LLM client are loaded ONCE in main.py lifespan,
        stored on app.state, and passed in here as singletons.

Wiring table:
    vertical    indexer            retriever        reranker             generator
    ───────────────────────────────────────────────────────────────────────────────────
    governance  GovernanceIndexer  HybridRetriever  CrossEncoderReranker GovernanceGenerator
    judgment    JudgmentIndexer    HybridRetriever  CrossEncoderReranker JudgmentGenerator
    law         ClauseIndexer      GraphRetriever   VerticalReranker     RiskGenerator
"""
from __future__ import annotations

import logging
from typing import Any

from app.core.pipeline import RAGPipeline
from app.config.verticals import VERTICAL_CONFIGS, SUPPORTED_VERTICALS

from app.indexers   import ClauseIndexer, JudgmentIndexer, GovernanceIndexer
from app.retrievers import GraphRetriever, HybridRetriever
from app.rerankers.vertical      import VerticalReranker
from app.rerankers.cross_encoder import CrossEncoderReranker
from app.generators import RiskGenerator, JudgmentGenerator, GovernanceGenerator

logger = logging.getLogger("docqa.factory")


def build_pipeline(
    vertical:    str,
    llm_client:  Any,   # CloudflareAI singleton — passed in, NOT created here
    reranker:    Any,   # CrossEncoderReranker singleton for compliance/university
) -> RAGPipeline:
    """
    Assemble a fully wired RAGPipeline for the given vertical.

    Args:
        vertical:   One of: law, compliance, hr, startup, university
        llm_client: CloudflareAI singleton (from app.state.cf_client)
        reranker:   CrossEncoderReranker singleton (from app.state.reranker)
                    Only used for compliance and university verticals.
                    Law/startup use VerticalReranker, hr uses NoReranker.

    Returns:
        RAGPipeline ready to handle queries.

    Raises:
        ValueError: if vertical is not supported.
    """
    if vertical not in SUPPORTED_VERTICALS:
        raise ValueError(
            f"Unsupported vertical: '{vertical}'. Supported: {SUPPORTED_VERTICALS}"
        )

    # Resolve any legacy aliases to core fellowship verticals
    resolved_vertical = "law" if vertical in ("compliance", "startup") else ("governance" if vertical in ("university", "hr") else vertical)
    config = {**VERTICAL_CONFIGS[resolved_vertical], "vertical": resolved_vertical}

    chunk_size    = config["chunk_size"]
    chunk_overlap = config["chunk_overlap"]
    token_budget  = config.get("token_budget", 4096)

    # ── India AI Fellowship Vertical Wiring ───────────────────────────────────

    if resolved_vertical == "governance":
        indexer   = GovernanceIndexer(chunk_size, chunk_overlap)
        retriever = HybridRetriever()
        _reranker = reranker if reranker is not None else CrossEncoderReranker()
        generator = GovernanceGenerator(llm_client)

    elif resolved_vertical == "judgment":
        indexer   = JudgmentIndexer(chunk_size, chunk_overlap)
        retriever = HybridRetriever()
        _reranker = reranker if reranker is not None else CrossEncoderReranker()
        generator = JudgmentGenerator(llm_client)

    elif resolved_vertical == "law":
        indexer   = ClauseIndexer(chunk_size, chunk_overlap)
        retriever = GraphRetriever()
        _reranker = VerticalReranker(vertical="law")
        generator = RiskGenerator(llm_client)

    else:
        raise ValueError(f"No pipeline config for: '{resolved_vertical}'")

    logger.info("Built pipeline: vertical=%s token_budget=%d", vertical, token_budget)

    return RAGPipeline(
        indexer      = indexer,
        retriever    = retriever,
        reranker     = _reranker,
        generator    = generator,
        config       = config,
        token_budget = token_budget,
    )
