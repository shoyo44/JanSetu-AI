"""
Ablation configuration matrix for DocsAI evaluation experiments.

Each config specifies a retriever strategy, whether HyDE query expansion
is enabled, and the reranking strategy.  The runner (run.py) iterates
over these configs to produce a comparison table.

Retriever options : "vector" | "graph" | "hybrid"
Rerank options    : "none"  | "cross_encoder"
HyDE              : True  | False
"""
from __future__ import annotations

import os
from typing import Dict, Any

# ── Ablation configurations ──────────────────────────────────────────────────

CONFIGS: Dict[str, Dict[str, Any]] = {
    "baseline_vector": dict(retriever="vector", hyde=False, rerank="none"),
    "graph_only":      dict(retriever="graph",  hyde=False, rerank="none"),
    "hybrid_rrf":      dict(retriever="hybrid", hyde=False, rerank="none"),
    "hybrid_hyde":     dict(retriever="hybrid", hyde=True,  rerank="none"),
    "hybrid_ce":       dict(retriever="hybrid", hyde=False, rerank="cross_encoder"),
    "full_pipeline":   dict(retriever="hybrid", hyde=True,  rerank="cross_encoder"),
}

# ── Gold-set paths (relative to project root) ───────────────────────────────

_EVAL_DIR = os.path.dirname(os.path.abspath(__file__))

GOLD_SETS: Dict[str, str] = {
    "legal":        os.path.join(_EVAL_DIR, "gold", "legal_gold.jsonl"),
    "unanswerable": os.path.join(_EVAL_DIR, "gold", "unanswerable.jsonl"),
}

# ── Defaults ─────────────────────────────────────────────────────────────────

DEFAULT_TOP_K: int = 10
