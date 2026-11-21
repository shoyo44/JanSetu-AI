"""
Citation Entailment Verification — post-generation grounding check.

Decomposes the LLM-generated answer into individual sentences/claims,
then verifies each claim against the cited document chunks using an
NLI (Natural Language Inference) cross-encoder model.

Singleton loading mirrors the pattern established by CrossEncoderReranker.

Usage:
    verifier = CitationVerifier.get_instance()
    result = await verifier.verify(answer_text, chunks_used)
    # result.grounding_score, result.verified_claims, result.unverified_claims, ...
"""
from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.core.schemas import ChunkResult

logger = logging.getLogger("docqa.citation_verifier")

# ── Boilerplate patterns to skip during verification ─────────────────────────

_BOILERPLATE_PATTERNS: List[re.Pattern[str]] = [
    re.compile(r"^based on (the|these) (documents?|chunks?|sources?|provided)", re.IGNORECASE),
    re.compile(r"^according to (the|these) (documents?|chunks?|sources?|provided)", re.IGNORECASE),
    re.compile(r"^(here is|here's|the following is) (a |an )?(summary|overview|answer)", re.IGNORECASE),
    re.compile(r"^I (could not|couldn't|was unable to|cannot) find", re.IGNORECASE),
    re.compile(r"^(please note|note that|it should be noted)", re.IGNORECASE),
    re.compile(r"^(in summary|to summarize|overall|in conclusion)", re.IGNORECASE),
    re.compile(r"^(let me|I will|I'll) (explain|summarize|break down|describe)", re.IGNORECASE),
    re.compile(r"^(yes|no|sure)[,.]?\s*$", re.IGNORECASE),
]

_MIN_CLAIM_LENGTH = 10  # sentences shorter than this are skipped


# ── Verification result ──────────────────────────────────────────────────────

@dataclass
class VerificationResult:
    """Result of citation entailment verification for a generated answer."""

    grounding_score: float                       # 0.0–1.0, fraction of verified claims
    total_claims: int                            # number of substantive claims found
    verified_claims: List[str] = field(default_factory=list)    # sentences that passed entailment
    unverified_claims: List[str] = field(default_factory=list)  # sentences that failed entailment
    claim_details: List[Dict] = field(default_factory=list)     # per-claim breakdown
    citation_verified: bool = False              # True if grounding_score >= 0.70


# ── Citation Verifier (singleton) ────────────────────────────────────────────

class CitationVerifier:
    """
    NLI-based citation entailment verifier.

    Loads ``cross-encoder/nli-deberta-v3-xsmall`` once on first use.
    Falls back to n-gram heuristic overlap when the model is unavailable.
    """

    _instance: Optional[CitationVerifier] = None
    _NLI_MODEL_NAME = "cross-encoder/nli-deberta-v3-xsmall"

    # NLI label indices for DeBERTa NLI models:
    #   0 = contradiction, 1 = neutral, 2 = entailment
    _ENTAILMENT_IDX = 2

    def __init__(self) -> None:
        self._model = None
        self._use_heuristic = False
        self._load_model()

    # ── Singleton accessor ────────────────────────────────────────────────────

    @classmethod
    def get_instance(cls) -> CitationVerifier:
        """Return the singleton verifier instance, creating it on first call."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── Model loading ─────────────────────────────────────────────────────────

    def _load_model(self) -> None:
        """Attempt to load the NLI cross-encoder; fall back to heuristic."""
        try:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(self._NLI_MODEL_NAME)
            logger.info(
                "✅ CitationVerifier loaded NLI model: %s", self._NLI_MODEL_NAME
            )
        except Exception as exc:
            logger.warning(
                "⚠️ Failed to load NLI model (%s). "
                "Using n-gram heuristic fallback for citation verification.",
                exc,
            )
            self._use_heuristic = True

    # ── Public API ────────────────────────────────────────────────────────────

    async def verify(
        self,
        answer: str,
        chunks: List[ChunkResult],
        threshold: float = 0.65,
    ) -> VerificationResult:
        """
        Verify that each claim in *answer* is entailed by at least one chunk.

        Args:
            answer:    The LLM-generated answer text.
            chunks:    The chunks cited / used during generation.
            threshold: Minimum entailment score for a claim to be "verified".

        Returns:
            A ``VerificationResult`` with per-claim breakdown and overall score.
        """
        claims = self._split_claims(answer)

        if not claims:
            return VerificationResult(
                grounding_score=1.0,
                total_claims=0,
                citation_verified=True,
            )

        if not chunks:
            return VerificationResult(
                grounding_score=0.0,
                total_claims=len(claims),
                unverified_claims=list(claims),
                claim_details=[
                    {"claim": c, "best_chunk_id": None, "entailment_score": 0.0, "verified": False}
                    for c in claims
                ],
                citation_verified=False,
            )

        # Run scoring (CPU-heavy) in a worker thread
        claim_details = await asyncio.to_thread(
            self._score_claims, claims, chunks, threshold
        )

        verified = [d["claim"] for d in claim_details if d["verified"]]
        unverified = [d["claim"] for d in claim_details if not d["verified"]]
        grounding = len(verified) / len(claims) if claims else 1.0

        return VerificationResult(
            grounding_score=round(grounding, 4),
            total_claims=len(claims),
            verified_claims=verified,
            unverified_claims=unverified,
            claim_details=claim_details,
            citation_verified=grounding >= 0.70,
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _split_claims(self, text: str) -> List[str]:
        """
        Split answer text into individual claim sentences.

        Filters out very short fragments and common LLM boilerplate.
        """
        raw_sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        claims: List[str] = []
        for sent in raw_sentences:
            sent = sent.strip()
            if len(sent) < _MIN_CLAIM_LENGTH:
                continue
            if any(pat.search(sent) for pat in _BOILERPLATE_PATTERNS):
                continue
            claims.append(sent)
        return claims

    def _score_claims(
        self,
        claims: List[str],
        chunks: List[ChunkResult],
        threshold: float,
    ) -> List[Dict]:
        """
        Score every claim against every chunk. Returns per-claim detail dicts.

        Uses the NLI cross-encoder when available, otherwise falls back to
        n-gram heuristic.
        """
        chunk_texts = [c.text for c in chunks]
        chunk_ids = [c.id for c in chunks]
        details: List[Dict] = []

        for claim in claims:
            best_score = 0.0
            best_chunk_id: Optional[str] = None

            if self._model is not None and not self._use_heuristic:
                # ── NLI cross-encoder scoring ──
                # Each pair is (premise=chunk_text, hypothesis=claim)
                pairs = [[chunk_text, claim] for chunk_text in chunk_texts]
                try:
                    logits = self._model.predict(pairs)
                    # logits shape: (n_chunks, 3) — [contradiction, neutral, entailment]
                    for idx, logit_row in enumerate(logits):
                        # softmax not needed if we just compare the entailment logit,
                        # but let's normalise for a clean 0-1 score
                        entailment_score = self._softmax_entailment(logit_row)
                        if entailment_score > best_score:
                            best_score = entailment_score
                            best_chunk_id = chunk_ids[idx]
                except Exception as exc:
                    logger.error(
                        "NLI inference failed for claim, falling back to heuristic: %s",
                        exc,
                    )
                    # fall through to heuristic below
                    best_score, best_chunk_id = self._heuristic_best_match(
                        claim, chunk_texts, chunk_ids
                    )
            else:
                # ── Heuristic fallback ──
                best_score, best_chunk_id = self._heuristic_best_match(
                    claim, chunk_texts, chunk_ids
                )

            details.append(
                {
                    "claim": claim,
                    "best_chunk_id": best_chunk_id,
                    "entailment_score": round(best_score, 4),
                    "verified": best_score >= threshold,
                }
            )

        return details

    @staticmethod
    def _softmax_entailment(logits) -> float:
        """
        Compute softmax probability of the entailment class (index 2).

        Works with both numpy arrays and plain lists.
        """
        import math

        vals = [float(v) for v in logits]
        max_v = max(vals)
        exps = [math.exp(v - max_v) for v in vals]
        total = sum(exps)
        return exps[CitationVerifier._ENTAILMENT_IDX] / total

    @staticmethod
    def _heuristic_best_match(
        claim: str,
        chunk_texts: List[str],
        chunk_ids: List[str],
    ) -> tuple[float, Optional[str]]:
        """Find the chunk with the highest heuristic entailment score."""
        best_score = 0.0
        best_id: Optional[str] = None
        for cid, ctext in zip(chunk_ids, chunk_texts):
            score = CitationVerifier._heuristic_entailment(claim, ctext)
            if score > best_score:
                best_score = score
                best_id = cid
        return best_score, best_id

    @staticmethod
    def _heuristic_entailment(claim: str, chunk_text: str) -> float:
        """
        Lightweight directional entailment proxy (claim coverage in chunk).

        Computes the fraction of substantive claim terms and character
        trigrams that are supported by the premise chunk.

        Returns a float in [0.0, 1.0].
        """
        # 1. Word-level containment with morphological root matching
        words = [w for w in re.findall(r"\b\w+\b", claim.lower()) if len(w) > 2]
        if not words:
            return 0.0
        chunk_lower = chunk_text.lower()
        matched_words = 0
        for w in words:
            if w in chunk_lower:
                matched_words += 1
            elif len(w) >= 5 and w[:len(w) - 2] in chunk_lower:
                # Suffix variation match (e.g., governed -> govern / governing)
                matched_words += 1
        word_containment = matched_words / len(words)

        # 2. Trigram containment: fraction of claim trigrams present in chunk
        def _trigrams(text: str) -> set[str]:
            t = text.lower()
            return {t[i : i + 3] for i in range(max(len(t) - 2, 0))}

        claim_ng = _trigrams(claim)
        chunk_ng = _trigrams(chunk_text)
        if not claim_ng:
            return word_containment

        trigram_containment = len(claim_ng & chunk_ng) / len(claim_ng)

        # Blend: 60% substantive word containment, 40% sequence-order trigram support
        return round(0.6 * word_containment + 0.4 * trigram_containment, 4)
