"""
Evaluation metrics for the DocsAI RAG pipeline.

All functions are **pure Python + math** (numpy is optional — the module
falls back to pure-Python implementations if numpy is unavailable).

Metric catalogue
─────────────────
Retrieval quality:
    recall_at_k              Fraction of gold IDs in top-k retrieved
    mrr                      Mean Reciprocal Rank
    ndcg_at_k                Normalised Discounted Cumulative Gain @ k
    compute_all_retrieval_metrics   Bundles the three above

Generation quality:
    citation_precision       % of cited chunks that are truly supporting
    refusal_accuracy         Correct / false refusal / false answer rates
    faithfulness_heuristic   n-gram overlap proxy for faithfulness
"""
from __future__ import annotations

import logging
import math
from collections import Counter
from typing import Dict, List, Set

logger = logging.getLogger("docsai.eval.metrics")

# ── helpers ──────────────────────────────────────────────────────────────────

def _to_set(ids: List[str]) -> Set[str]:
    """Deduplicate while preserving order-independence for set operations."""
    return set(ids)


# ═══════════════════════════════════════════════════════════════════════════════
# Retrieval metrics
# ═══════════════════════════════════════════════════════════════════════════════

def recall_at_k(retrieved_ids: List[str], gold_ids: List[str], k: int) -> float:
    """Fraction of gold IDs found in the top-*k* retrieved results.

    Args:
        retrieved_ids: Ordered list of chunk IDs returned by the retriever.
        gold_ids:      Ground-truth relevant chunk IDs.
        k:             Cut-off rank.

    Returns:
        A float in [0.0, 1.0].  Returns 0.0 when *gold_ids* is empty.
    """
    if not gold_ids:
        return 0.0
    top_k_set = _to_set(retrieved_ids[:k])
    gold_set = _to_set(gold_ids)
    return len(top_k_set & gold_set) / len(gold_set)


def mrr(retrieved_ids: List[str], gold_ids: List[str]) -> float:
    """Mean Reciprocal Rank — reciprocal of the rank of the *first* relevant hit.

    Args:
        retrieved_ids: Ordered list of chunk IDs (most-relevant first).
        gold_ids:      Ground-truth relevant chunk IDs.

    Returns:
        A float in (0.0, 1.0], or 0.0 if no gold ID appears in *retrieved_ids*.
    """
    gold_set = _to_set(gold_ids)
    for rank, rid in enumerate(retrieved_ids, start=1):
        if rid in gold_set:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved_ids: List[str], gold_ids: List[str], k: int) -> float:
    """Normalised Discounted Cumulative Gain @ *k*.

    Relevance is binary: 1 if the chunk ID is in *gold_ids*, else 0.

    Args:
        retrieved_ids: Ordered list of chunk IDs (most-relevant first).
        gold_ids:      Ground-truth relevant chunk IDs.
        k:             Cut-off rank.

    Returns:
        A float in [0.0, 1.0].  Returns 0.0 when *gold_ids* is empty.
    """
    if not gold_ids:
        return 0.0

    gold_set = _to_set(gold_ids)

    # DCG for the actual ranking
    dcg = 0.0
    for i, rid in enumerate(retrieved_ids[:k]):
        rel = 1.0 if rid in gold_set else 0.0
        dcg += rel / math.log2(i + 2)  # i+2 because rank starts at 1

    # Ideal DCG — all gold docs ranked first
    ideal_hits = min(len(gold_set), k)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal_hits))

    if idcg == 0.0:
        return 0.0
    return dcg / idcg


def compute_all_retrieval_metrics(
    retrieved_ids: List[str],
    gold_ids: List[str],
    k: int = 10,
) -> Dict[str, float]:
    """Bundle recall@k, MRR, and nDCG@k into one dict.

    Args:
        retrieved_ids: Ordered list of chunk IDs (most-relevant first).
        gold_ids:      Ground-truth relevant chunk IDs.
        k:             Cut-off rank (default 10).

    Returns:
        ``{"recall@k": …, "mrr": …, "ndcg@k": …}``
    """
    return {
        f"recall@{k}": recall_at_k(retrieved_ids, gold_ids, k),
        "mrr":         mrr(retrieved_ids, gold_ids),
        f"ndcg@{k}":   ndcg_at_k(retrieved_ids, gold_ids, k),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Generation / citation metrics
# ═══════════════════════════════════════════════════════════════════════════════

def citation_precision(
    cited_chunk_ids: List[str],
    supporting_chunk_ids: List[str],
) -> float:
    """Percentage of cited chunks that are genuinely supporting (precision).

    Args:
        cited_chunk_ids:      Chunk IDs the generator cited in its answer.
        supporting_chunk_ids: Ground-truth supporting chunk IDs.

    Returns:
        A float in [0.0, 1.0].  Returns 1.0 when *cited_chunk_ids* is empty
        (vacuous truth — nothing was cited, so nothing was wrong).
    """
    if not cited_chunk_ids:
        return 1.0  # vacuous truth
    cited_set = _to_set(cited_chunk_ids)
    support_set = _to_set(supporting_chunk_ids)
    return len(cited_set & support_set) / len(cited_set)


def refusal_accuracy(
    predictions: List[dict],
    gold: List[dict],
) -> Dict[str, float]:
    """Evaluate how well the model handles unanswerable questions.

    Each entry in *predictions* and *gold* is a dict with at least:
        - ``"id"``         : question identifier (used to match pred ↔ gold)
        - ``"answerable"`` : bool (gold) — whether the question is answerable
        - ``"not_found"``  : bool (pred) — whether the model refused to answer

    Returns:
        A dict with three rates (each in [0.0, 1.0]):
        - ``correct_refusal_rate`` : fraction of unanswerable Qs correctly refused
        - ``false_refusal_rate``   : fraction of answerable Qs incorrectly refused
        - ``false_answer_rate``    : fraction of unanswerable Qs incorrectly answered
    """
    has_ids = all("id" in g for g in gold) and all("id" in p for p in predictions)
    if has_ids:
        gold_map: Dict[str, dict] = {g["id"]: g for g in gold}
        pairs = [(p, gold_map.get(p.get("id"))) for p in predictions if p.get("id") in gold_map]
    else:
        pairs = list(zip(predictions, gold))

    unanswerable_total = 0
    unanswerable_refused = 0  # correct refusal
    unanswerable_answered = 0  # false answer

    answerable_total = 0
    answerable_refused = 0  # false refusal

    for pred, g in pairs:
        if g is None:
            continue

        is_answerable = g.get("answerable", True)
        model_refused = pred.get("not_found", False) or pred.get("abstained", False)

        if is_answerable:
            answerable_total += 1
            if model_refused:
                answerable_refused += 1
        else:
            unanswerable_total += 1
            if model_refused:
                unanswerable_refused += 1
            else:
                unanswerable_answered += 1

    return {
        "correct_refusal_rate": (
            unanswerable_refused / unanswerable_total if unanswerable_total else 0.0
        ),
        "false_refusal_rate": (
            answerable_refused / answerable_total if answerable_total else 0.0
        ),
        "false_answer_rate": (
            unanswerable_answered / unanswerable_total if unanswerable_total else 0.0
        ),
    }


def faithfulness_heuristic(answer: str, context: str, n: int = 3) -> float:
    """Simple n-gram overlap proxy for faithfulness (before RAGAS integration).

    Computes the fraction of *answer* n-grams that also appear in *context*.
    Higher values suggest the answer is better grounded in the retrieved text.

    Args:
        answer:  Generated answer text.
        context: Concatenated context string fed to the generator.
        n:       n-gram size (default 3 — trigrams).

    Returns:
        A float in [0.0, 1.0].  Returns 1.0 when the answer has no n-grams
        (e.g. very short text).
    """
    def _ngrams(text: str, n: int) -> List[str]:
        tokens = text.lower().split()
        if len(tokens) < n:
            return tokens if tokens else []
        return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]

    answer_ngrams = _ngrams(answer, n)
    if not answer_ngrams:
        return 1.0

    context_ngrams_set = set(_ngrams(context, n))
    answer_counter = Counter(answer_ngrams)
    total = sum(answer_counter.values())
    matched = sum(
        count for ng, count in answer_counter.items() if ng in context_ngrams_set
    )
    return matched / total
