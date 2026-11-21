"""
Indian Court Judgment Indexer — India AI / Law & Justice Vertical.

Customized for Indian Supreme Court, High Courts, and Appellate Tribunals.
Segments judgments into structured judicial components:
    - FACTS / BACKGROUND
    - ISSUES / QUESTIONS OF LAW
    - STATUTES & ACTS CITED (IPC/BNS, CrPC/BNSS, Constitution, etc.)
    - RATIO DECIDENDI (binding precedent & legal holding)
    - OBITER DICTA (judicial observations)
    - ORDER / DISPOSITION (Allowed, Dismissed, Remanded, Bail Granted)

Metadata extracted per chunk:
    - citation_ref : Indian law citation (AIR, SCC, INSC, SCR, etc.)
    - case_title   : Inferred or detected case title (e.g. Appellant v. Respondent)
    - acts_cited   : List of Indian statutory acts and sections invoked
    - section_type : ratio / facts / issue / statute / disposition
    - lang         : "en" | "hi" | ...
    - chunk_type   : "judgment"
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from app.core.interfaces import BaseIndexer
from app.core.embedding_router import detect_language
from app.indexers._base import split_into_chunks, build_chunk_record

logger = logging.getLogger("docqa.indexers.judgment")

# ── Indian Legal Citation Patterns ───────────────────────────────────────────
_CITATION_PATTERNS = [
    re.compile(r"\b\d{4}\s+INSC\s+\d+\b", re.IGNORECASE),                         # 2024 INSC 123 (Neutral Citation)
    re.compile(r"\b\(\d{4}\)\s+\d+\s+SCC\s+\d+\b", re.IGNORECASE),               # (2023) 4 SCC 120
    re.compile(r"\b\d{4}\s+SCC\s+OnLine\s+[A-Za-z\s]+\d+\b", re.IGNORECASE),     # 2022 SCC OnLine SC 45
    re.compile(r"\bAIR\s+\d{4}\s+(?:SC|Del|Bom|Cal|Mad|All)\s+\d+\b", re.IGNORECASE), # AIR 2021 SC 890
    re.compile(r"\b\[\d{4}\]\s+\d+\s+SCR\s+\d+\b", re.IGNORECASE),               # [2020] 2 SCR 450
    re.compile(r"\b(?:Criminal|Civil)\s+Appeal\s+No[s]?\.\s+[\d\/]+\s+of\s+\d{4}\b", re.IGNORECASE),
    re.compile(r"\bSpecial\s+Leave\s+Petition\s+\([A-Za-z]+\)\s+No[s]?\.\s+[\d\/]+\s+of\s+\d{4}\b", re.IGNORECASE),
    re.compile(r"\bWrit\s+Petition\s+\([A-Za-z]+\)\s+No[s]?\.\s+[\d\/]+\s+of\s+\d{4}\b", re.IGNORECASE),
]

# ── Indian Acts & Statutes Patterns ──────────────────────────────────────────
_ACT_PATTERNS = [
    (re.compile(r"\b(?:Section|Sec\.?)\s+\d+[A-Z]?\s+(?:of\s+)?(?:the\s+)?(?:IPC|Indian\s+Penal\s+Code)\b", re.IGNORECASE), "Indian Penal Code (IPC)"),
    (re.compile(r"\b(?:Section|Sec\.?)\s+\d+[A-Z]?\s+(?:of\s+)?(?:the\s+)?(?:BNS|Bharatiya\s+Nyaya\s+Sanhita)\b", re.IGNORECASE), "Bharatiya Nyaya Sanhita (BNS)"),
    (re.compile(r"\b(?:Section|Sec\.?)\s+\d+[A-Z]?\s+(?:of\s+)?(?:the\s+)?(?:CrPC|Code\s+of\s+Criminal\s+Procedure)\b", re.IGNORECASE), "Code of Criminal Procedure (CrPC)"),
    (re.compile(r"\b(?:Section|Sec\.?)\s+\d+[A-Z]?\s+(?:of\s+)?(?:the\s+)?(?:BNSS|Bharatiya\s+Nagarik\s+Suraksha\s+Sanhita)\b", re.IGNORECASE), "Bharatiya Nagarik Suraksha Sanhita (BNSS)"),
    (re.compile(r"\bArticle\s+\d+[A-Z]?\s+(?:of\s+)?(?:the\s+)?Constitution\b", re.IGNORECASE), "Constitution of India"),
    (re.compile(r"\bSection\s+138\s+(?:of\s+)?(?:the\s+)?(?:NI\s+Act|Negotiable\s+Instruments\s+Act)\b", re.IGNORECASE), "Negotiable Instruments Act (Sec 138)"),
    (re.compile(r"\bArbitration\s+and\s+Conciliation\s+Act(?:,\s*\d{4})?\b", re.IGNORECASE), "Arbitration & Conciliation Act 1996"),
    (re.compile(r"\bInsolvency\s+and\s+Bankruptcy\s+Code|IBC(?:,\s*\d{4})?\b", re.IGNORECASE), "Insolvency and Bankruptcy Code (IBC)"),
    (re.compile(r"\bRight\s+to\s+Information\s+Act|RTI\s+Act(?:,\s*\d{4})?\b", re.IGNORECASE), "RTI Act 2005"),
    (re.compile(r"\bIndian\s+Contract\s+Act(?:,\s*\d{4})?\b", re.IGNORECASE), "Indian Contract Act 1872"),
]

# ── Case Title Pattern (e.g. Appellant Versus Respondent) ───────────────────
_TITLE_PATTERN = re.compile(
    r"""(?:\b([A-Z][A-Za-z\s\.,&]+?)\s+(?:versus|vs\.?|v\.)\s+([A-Z][A-Za-z\s\.,&]+))""",
    re.IGNORECASE,
)


def _detect_citations(text: str) -> List[str]:
    """Extract all Indian law citations found in text."""
    found: List[str] = []
    for pat in _CITATION_PATTERNS:
        for match in pat.finditer(text):
            val = match.group(0).strip()
            if val not in found:
                found.append(val)
    return found


def _detect_acts(text: str) -> List[str]:
    """Detect Indian statutory acts and sections cited in text."""
    acts: List[str] = []
    for pat, label in _ACT_PATTERNS:
        match = pat.search(text)
        if match and label not in acts:
            acts.append(f"{label}: {match.group(0).strip()}")
    return acts


def _classify_judgment_segment(text: str) -> str:
    """Classify the judicial role of this chunk."""
    t_lower = text.lower()

    if any(k in t_lower for k in ["appeal is allowed", "appeal is dismissed", "bail is granted", "bail rejected", "matter is remanded", "ordered accordingly"]):
        return "disposition"
    if any(k in t_lower for k in ["we hold that", "the question of law is answered", "the ratio of", "settled position of law", "it is held that"]):
        return "ratio_decidendi"
    if any(k in t_lower for k in ["the question that arises", "issues for consideration", "whether the high court", "point for determination"]):
        return "issue"
    if any(k in t_lower for k in ["prosecution case is", "factual matrix", "brief facts", "the appellant was charged"]):
        return "facts"
    return "general_reasoning"


class JudgmentIndexer(BaseIndexer):
    """
    Indexer specialized for Indian court judgments and legal orders.

    Vertical: judgment
    Chunk type: judgment
    Retriever: HybridRetriever (RRF combining FAISS vector search + Indian case citation traversal)
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split judgment text into semantically labeled judicial chunks."""
        if not text or not text.strip():
            return []

        raw_chunks = split_into_chunks(text, self.chunk_size, self.chunk_overlap)
        records: List[Dict[str, Any]] = []

        lang_info = detect_language(text)

        # Detect case title if present on this page
        case_title = None
        title_match = _TITLE_PATTERN.search(text[:600])
        if title_match:
            case_title = f"{title_match.group(1).strip()} v. {title_match.group(2).strip()}"

        for i, chunk_text in enumerate(raw_chunks):
            citations = _detect_citations(chunk_text)
            acts = _detect_acts(chunk_text)
            segment_type = _classify_judgment_segment(chunk_text)

            record = build_chunk_record(
                text=chunk_text,
                page=metadata.get("page", 0),
                chunk_type="judgment",
                doc_id=metadata.get("doc_id", ""),
                tenant_id=metadata.get("tenant_id", ""),
                order=metadata.get("chunk_offset", 0) + i,
                extra={
                    "citation_ref": citations[0] if citations else None,
                    "all_citations": citations,
                    "acts_cited": acts,
                    "section_type": segment_type,
                    "case_title": case_title or metadata.get("doc_name", "Unknown Case"),
                    "lang": lang_info["lang"],
                    "is_indic": lang_info["is_indic"],
                },
            )
            records.append(record)

        logger.debug(
            "JudgmentIndexer: page %s -> %d chunks (lang=%s).",
            metadata.get("page"), len(records), lang_info["lang"]
        )
        return records

    def index(self, chunks: List[Dict[str, Any]], store: Any) -> None:
        """Persist judgment chunks and entity relationships to GraphStore."""
        for chunk in chunks:
            store.add_chunk(chunk)
            doc_id = chunk.get("doc_id")
            chunk_id = chunk.get("id")

            # Link judgment entities (citations & statutory acts) into the knowledge graph
            for act in chunk.get("acts_cited", []):
                store.add_entity_relation(
                    source_id=chunk_id,
                    target_id=f"act_{act.split(':')[0].strip().replace(' ', '_')}",
                    relation="CITED_ACT",
                    metadata={"act_name": act}
                )

            for citation in chunk.get("all_citations", []):
                store.add_entity_relation(
                    source_id=chunk_id,
                    target_id=f"cite_{citation.replace(' ', '_')}",
                    relation="CITED_PRECEDENT",
                    metadata={"citation": citation}
                )
