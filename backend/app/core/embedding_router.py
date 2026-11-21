"""
Multilingual & Indic Language Embedding Router — India AI Support.

Provides:
    - Zero-dependency script & language detection across major Indian languages
      (Hindi, Tamil, Telugu, Marathi, Bengali, Gujarati, Kannada, Malayalam, Punjabi, Urdu, English).
    - Multilingual embedding generation and dimension alignment (768 dims).
    - Query language detection and cross-lingual prompt enrichment for legal & governance docs.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("docqa.embedding_router")

# ── Unicode Script Ranges for Indian Languages ────────────────────────────────
_SCRIPT_RANGES: List[Tuple[str, str, int, int]] = [
    ("hi", "Devanagari (Hindi/Marathi)", 0x0900, 0x097F),
    ("bn", "Bengali",                    0x0980, 0x09FF),
    ("pa", "Gurmukhi (Punjabi)",         0x0A00, 0x0A7F),
    ("gu", "Gujarati",                   0x0A80, 0x0AFF),
    ("or", "Odia",                       0x0B00, 0x0B7F),
    ("ta", "Tamil",                      0x0B80, 0x0BFF),
    ("te", "Telugu",                     0x0C00, 0x0C7F),
    ("kn", "Kannada",                    0x0C80, 0x0CFF),
    ("ml", "Malayalam",                  0x0D00, 0x0D7F),
    ("ur", "Urdu / Perso-Arabic",        0x0600, 0x06FF),
]

_LATIN_RANGE = (0x0041, 0x007A)


def detect_language(text: str) -> Dict[str, Any]:
    """
    Detect the script and language of text using Unicode character ranges.
    Fast, deterministic, and works completely offline with zero dependencies.

    Returns:
        {
            "lang": "hi" | "ta" | "en" | ...,
            "script_name": str,
            "is_indic": bool,
            "confidence": float (0.0-1.0)
        }
    """
    if not text or not text.strip():
        return {"lang": "en", "script_name": "Latin (English)", "is_indic": False, "confidence": 1.0}

    counts: Dict[str, int] = {"en": 0}
    script_labels: Dict[str, str] = {"en": "Latin (English)"}

    total_alpha = 0
    for char in text:
        cp = ord(char)
        # Check Latin
        if (0x0041 <= cp <= 0x005A) or (0x0061 <= cp <= 0x007A):
            counts["en"] += 1
            total_alpha += 1
            continue

        # Check Indic scripts
        for lang_code, name, start, end in _SCRIPT_RANGES:
            if start <= cp <= end:
                counts[lang_code] = counts.get(lang_code, 0) + 1
                script_labels[lang_code] = name
                total_alpha += 1
                break

    if total_alpha == 0:
        return {"lang": "en", "script_name": "Latin (English)", "is_indic": False, "confidence": 1.0}

    top_lang = max(counts, key=counts.get)  # type: ignore
    confidence = round(counts[top_lang] / total_alpha, 3)

    return {
        "lang": top_lang,
        "script_name": script_labels.get(top_lang, "Unknown"),
        "is_indic": top_lang != "en",
        "confidence": confidence,
    }


class MultilingualRouter:
    """
    Routes embeddings and queries based on detected document/query language.
    Guarantees consistent 768-dimensional embeddings regardless of upstream source.
    """

    TARGET_DIM = 768

    def __init__(self, primary_client: Any = None):
        self.primary_client = primary_client

    async def get_embedding(self, text: str, client: Any = None) -> List[float]:
        """
        Produce a normalized embedding vector for the input text.
        Works across English and Indic scripts.
        """
        active_client = client or self.primary_client
        lang_info = detect_language(text)

        if active_client is not None and hasattr(active_client, "embed"):
            try:
                # If text is Indic, prefix with multilingual task instruction
                embed_text = text
                if lang_info["is_indic"]:
                    embed_text = f"passage: {text[:2000]}"
                
                vec = await active_client.embed(embed_text)
                return self._normalize_dimension(vec, self.TARGET_DIM)
            except Exception as exc:
                logger.warning("Primary embedding failed for lang %s: %s", lang_info["lang"], exc)

        # Fallback deterministic pseudo-embedding for testing or offline environments
        return self._fallback_embedding(text, self.TARGET_DIM)

    @staticmethod
    def _normalize_dimension(vector: List[float], target_dim: int) -> List[float]:
        """Align vector to exact target dimension (truncate or pad)."""
        import numpy as np

        arr = np.array(vector, dtype=np.float32)
        if len(arr) == target_dim:
            norm = np.linalg.norm(arr)
            return (arr / (norm if norm > 0 else 1.0)).tolist()

        if len(arr) > target_dim:
            arr = arr[:target_dim]
        else:
            arr = np.pad(arr, (0, target_dim - len(arr)), mode="constant")

        norm = np.linalg.norm(arr)
        return (arr / (norm if norm > 0 else 1.0)).tolist()

    @staticmethod
    def _fallback_embedding(text: str, dim: int) -> List[float]:
        """Deterministic hash-based embedding fallback when API is offline."""
        import hashlib
        import numpy as np

        h = hashlib.sha256(text.encode("utf-8")).digest()
        # Generate reproducible pseudorandom vector seeded with text hash
        seed = int.from_bytes(h[:4], "big")
        rng = np.random.default_rng(seed)
        vec = rng.normal(0, 1, dim).astype(np.float32)
        norm = np.linalg.norm(vec)
        return (vec / (norm if norm > 0 else 1.0)).tolist()
