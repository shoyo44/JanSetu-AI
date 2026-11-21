"""
Governance & Public Policy Vertical Indexer.

Designed for Central & State Government Gazettes, Welfare Schemes (Yojanas),
Ministry guidelines, and Government Orders (G.O.s).

Chunks documents by structural governance facets:
  - ELIGIBILITY: Income ceiling, age, landholding, gender, category
  - EXCLUSIONS: Tax payers, institutional holders, existing beneficiaries
  - BENEFITS: DBT subsidy, cash grant, health coverage, pension, loan subvention
  - REQUIRED_DOCS: Aadhaar, Ration Card, Land records, Income Certificate
  - APPLICATION_PROCEDURE: CSC portal, Panchayat/Block office, Nodal officer
  - GRIEVANCE_REDRESSAL: CPGRAMS, helpline, RTI provisions
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("docqa.indexers.governance")

# Nodal Ministries across Government of India
KNOWN_MINISTRIES = [
    "Ministry of Agriculture & Farmers Welfare",
    "Ministry of Health and Family Welfare",
    "Ministry of Rural Development",
    "Ministry of Electronics and Information Technology",
    "Ministry of Social Justice and Empowerment",
    "Ministry of Women and Child Development",
    "Ministry of Housing and Urban Affairs",
    "Ministry of Finance",
    "Ministry of Education",
    "Ministry of Labour and Employment",
]

# Section headers frequently found in Government Scheme Guidelines
GOVERNANCE_FACET_PATTERNS = [
    (r"(?i)(?:eligibility\s+criteria|who\s+can\s+apply|beneficiary\s+criteria|target\s+beneficiaries)", "eligibility"),
    (r"(?i)(?:exclusion\s+criteria|who\s+cannot\s+apply|ineligib\w+|exceptions)", "exclusions"),
    (r"(?i)(?:benefits?\s+provided|quantum\s+of\s+assistance|pattern\s+of\s+assistance|financial\s+assistance|entitlements?)", "benefits"),
    (r"(?i)(?:documents?\s+required|mandatory\s+documents|check-?list\s+of\s+documents|enclosures)", "required_documents"),
    (r"(?i)(?:how\s+to\s+apply|application\s+procedure|submission\s+process|implementation\s+mechanism)", "application_procedure"),
    (r"(?i)(?:grievance\s+redressal|helpline|dispute\s+resolution|cpgrams|nodal\s+officer|monitoring)", "grievance_redressal"),
]


class GovernanceIndexer:
    """
    Semantic chunker for public policy and government welfare scheme guidelines.
    """

    def __init__(self, target_chunk_size: int = 500, overlap: int = 60):
        self.target_chunk_size = target_chunk_size
        self.overlap = overlap

    def _detect_facet(self, text: str) -> str:
        """Categorize a chunk into a governance facet."""
        for pattern, facet in GOVERNANCE_FACET_PATTERNS:
            if re.search(pattern, text):
                return facet
        return "general_guideline"

    def _extract_scheme_name(self, text: str) -> Optional[str]:
        """Detect common scheme name or acronym."""
        patterns = [
            r"(?:Pradhan\s+Mantri\s+[A-Za-z\s]+(?:Yojana|Scheme))",
            r"(?:PM-[A-Z]+|PM[A-Z]+)",
            r"(?:Ayushman\s+Bharat|PM-JAY|PM-KISAN|PMAY|MGNREGA|PMFBY)",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return m.group(0).strip()
        return None

    def _extract_gazette_ref(self, text: str) -> Optional[str]:
        """Extract Gazette Notification Number (e.g. G.S.R. 123(E), S.O. 456(E))."""
        match = re.search(r"(?:G\.?\s*S\.?\s*R\.?|S\.?\s*O\.?|Notification\s+No\.?)\s*[\d\w\.\(\)\/\-]+", text, re.IGNORECASE)
        return match.group(0).strip() if match else None

    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Splits policy text into structured governance chunks with facet tags.
        """
        if not text or not text.strip():
            return []

        metadata = metadata or {}
        doc_id = metadata.get("doc_id", "")
        page = metadata.get("page", 1)
        tenant_id = metadata.get("tenant_id", "")

        scheme_name = self._extract_scheme_name(text)
        gazette_ref = self._extract_gazette_ref(text)

        # Split text into paragraphs / structural blocks
        paragraphs = re.split(r"\n\s*\n|\r\n\s*\r\n", text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        chunks: List[Dict[str, Any]] = []
        current_text = ""
        current_facet = "general_guideline"

        for para in paragraphs:
            para_facet = self._detect_facet(para)
            if para_facet != "general_guideline":
                current_facet = para_facet

            if len(current_text) + len(para) > self.target_chunk_size and current_text:
                chunks.append({
                    "text": current_text.strip(),
                    "page": page,
                    "doc_id": doc_id,
                    "tenant_id": tenant_id,
                    "chunk_type": current_facet,
                    "facet": current_facet,
                    "scheme_name": scheme_name,
                    "gazette_ref": gazette_ref,
                })
                # Maintain overlap
                words = current_text.split()
                current_text = " ".join(words[-self.overlap:]) + " " + para
            else:
                current_text = (current_text + "\n" + para).strip()

        if current_text:
            chunks.append({
                "text": current_text.strip(),
                "page": page,
                "doc_id": doc_id,
                "tenant_id": tenant_id,
                "chunk_type": current_facet,
                "facet": current_facet,
                "scheme_name": scheme_name,
                "gazette_ref": gazette_ref,
            })

        return chunks
