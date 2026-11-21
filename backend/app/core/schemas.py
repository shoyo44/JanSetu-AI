"""
Pydantic v2 Output Schemas — one typed model per vertical.

Every generator must return one of these models (not raw dicts).
Enables automatic validation, serialization, and OpenAPI documentation.

Hierarchy:
    VerticalOutput          ← base for all verticals
    ├── RiskOutput          ← law + startup
    ├── ComplianceOutput    ← compliance
    ├── FriendlyOutput      ← hr
    └── AcademicOutput      ← university
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


# ─── Shared Enums ────────────────────────────────────────────────────────────

class RiskLevel(str, Enum):
    HIGH   = "HIGH"
    MEDIUM = "MEDIUM"
    LOW    = "LOW"


class ConfidenceLevel(str, Enum):
    HIGH   = "HIGH"
    MEDIUM = "MEDIUM"
    LOW    = "LOW"


class ComplianceStatus(str, Enum):
    COMPLIANT     = "COMPLIANT"
    NON_COMPLIANT = "NON-COMPLIANT"
    UNCLEAR       = "UNCLEAR"


# ─── Shared Sub-Models ───────────────────────────────────────────────────────

class Citation(BaseModel):
    """A reference to a specific clause, article, or page in a document."""
    clause:  Optional[str] = None
    article: Optional[str] = None
    page:    Optional[int] = None


class AcademicCitation(BaseModel):
    """A reference to a specific paper, section, and author."""
    author:  str
    year:    str
    section: str


class ChunkResult(BaseModel):
    """
    A single retrieved chunk from the Neo4j graph.
    Produced by all retrievers and consumed by the reranker → context manager → generator.
    """
    id:            str
    text:          str
    enriched_text: Optional[str]  = None   # OCR / visual description overlay
    page:          Optional[int]  = None
    doc_id:        Optional[str]  = None
    doc_name:      Optional[str]  = None
    chunk_type:    Optional[str]  = None   # clause / article / topic / term / section
    clause_ref:    Optional[str]  = None   # law vertical
    article_ref:   Optional[str]  = None   # compliance vertical
    section:       Optional[str]  = None   # university vertical
    employee_type: Optional[str]  = None   # hr vertical
    defined_term:  Optional[str]  = None   # startup vertical
    superseded:    Optional[bool] = False
    score:         float          = 0.0    # vector similarity score
    rerank_score:  Optional[float] = None  # CrossEncoder score (overrides score)

    @property
    def best_score(self) -> float:
        """Returns rerank_score if available, else raw vector score."""
        return self.rerank_score if self.rerank_score is not None else self.score


# ─── Base Output ─────────────────────────────────────────────────────────────

class VerticalOutput(BaseModel):
    """Base class for all vertical output schemas. Never instantiate directly."""
    answer:      str
    confidence:  ConfidenceLevel = ConfidenceLevel.LOW
    chunks_used: List[str]       = Field(default_factory=list)
    not_found:   bool            = False
    abstained:              bool            = False
    abstention_reason:      Optional[str]   = None
    abstention_diagnostics: Optional[Dict[str, Any]] = None
    nearest_topics:         List[str]       = Field(default_factory=list)
    grounding_score:        Optional[float] = None
    unverified_claims:      List[str]       = Field(default_factory=list)
    citation_verified:      Optional[bool]  = None

    model_config = {"use_enum_values": True}


# ─── Law / Startup Vertical ──────────────────────────────────────────────────

class RiskOutput(VerticalOutput):
    """Output schema for law and startup verticals."""
    citations:       List[Citation]    = Field(default_factory=list)
    risk_level:      RiskLevel         = RiskLevel.LOW
    red_flags:       List[str]         = Field(default_factory=list)
    # Startup-specific extras (optional for law)
    plain_english:   Optional[str]     = None
    founder_risk:    Optional[RiskLevel] = None
    market_standard: Optional[str]    = None
    related_terms:   List[str]         = Field(default_factory=list)


# ─── Compliance Vertical ─────────────────────────────────────────────────────

class ComplianceOutput(VerticalOutput):
    """Output schema for the compliance vertical."""
    regulation_id:     Optional[str]      = None
    section:           Optional[str]      = None
    compliance_status: ComplianceStatus   = ComplianceStatus.UNCLEAR
    version_warning:   bool               = False
    citations:         List[Citation]     = Field(default_factory=list)


# ─── HR Vertical ─────────────────────────────────────────────────────────────

class FriendlyOutput(VerticalOutput):
    """Output schema for the HR vertical."""
    policy_section:    Optional[str] = None
    applies_to:        List[str]     = Field(default_factory=list)
    related_policies:  List[str]     = Field(default_factory=list)


# ─── University Vertical ─────────────────────────────────────────────────────

class AcademicOutput(VerticalOutput):
    """Output schema for the university / research paper vertical."""
    paper_title:      Optional[str]         = None
    authors:          List[str]             = Field(default_factory=list)
    abstract_summary: Optional[str]         = None
    citations:        List[AcademicCitation] = Field(default_factory=list)
    contradictions:   List[str]             = Field(default_factory=list)
    related_papers:   List[str]             = Field(default_factory=list)

    @field_validator("authors", "contradictions", "related_papers", mode="before")
    @classmethod
    def coerce_null_to_list(cls, v: Any) -> List[str]:
        """If the LLM returns the string 'null' or None, return an empty list."""
        if v is None or v == "null" or v == "None":
            return []
        if isinstance(v, list):
            return v
        return []


# ─── Judgment Vertical (India AI / Law & Justice) ────────────────────────────

class JudgmentOutput(VerticalOutput):
    """Output schema for the Indian Court Judgment / Case Law vertical."""
    case_title:        Optional[str]   = None
    court_name:        Optional[str]   = None
    neutral_citation:  Optional[str]   = None
    bench:             List[str]       = Field(default_factory=list)
    acts_cited:        List[str]       = Field(default_factory=list)
    ratio_decidendi:   Optional[str]   = None
    obiter_dicta:      Optional[str]   = None
    disposition:       Optional[str]   = None
    citations:         List[Citation]  = Field(default_factory=list)
    language:          str             = "en"

    @field_validator("bench", "acts_cited", mode="before")
    @classmethod
    def coerce_null_lists(cls, v: Any) -> List[str]:
        if v is None or v == "null" or v == "None":
            return []
        if isinstance(v, list):
            return v
        return []


# ─── Governance Vertical (India AI / Public Policy & Schemes) ─────────────────

class GovernanceOutput(VerticalOutput):
    """Output schema for the Indian Governance, Public Policy & Welfare Schemes vertical."""
    scheme_name:                  Optional[str]   = None
    nodal_ministry:               Optional[str]   = None
    gazette_reference:            Optional[str]   = None
    jan_suvidha_summary:          Optional[str]   = None   # Plain language explanation for common citizens
    eligibility_criteria:         List[str]       = Field(default_factory=list)
    exclusion_criteria:           List[str]       = Field(default_factory=list)
    benefits:                     List[str]       = Field(default_factory=list)
    required_documents:           List[str]       = Field(default_factory=list)
    application_steps:            List[str]       = Field(default_factory=list)
    official_portal_or_helpline:  Optional[str]   = None
    citations:                    List[Citation]  = Field(default_factory=list)

    @field_validator(
        "eligibility_criteria", "exclusion_criteria", "benefits",
        "required_documents", "application_steps", mode="before"
    )
    @classmethod
    def coerce_null_gov_lists(cls, v: Any) -> List[str]:
        if v is None or v == "null" or v == "None":
            return []
        if isinstance(v, list):
            return v
        return []
