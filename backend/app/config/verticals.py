"""
Vertical Configuration Registry — India AI Fellowship Platform.

Calibrated strictly for sovereign public governance, justice delivery, and statutory law.
Primary Verticals:
    - governance : Government Gazettes, Welfare Schemes (Yojanas), Jan Suvidha citizen delivery.
    - judgment   : Indian Supreme Court & High Court judgments, ratio decidendi, bail precedents.
    - law        : Statutory enactments, IPC ⇄ BNS, CrPC ⇄ BNSS concordance, contracts, property deeds.
"""
from __future__ import annotations
from typing import Any, Dict

VERTICAL_CONFIGS: Dict[str, Dict[str, Any]] = {

    # ── Governance & Public Policy (India AI Fellowship / Schemes) ───────────
    "governance": {
        "chunk_size":              500,
        "chunk_overlap":           100,
        "top_k":                   12,
        "token_budget":            4500,
        "score_floor":             0.38,
        "citizen_simplification":  True,
        "system_prompt": (
            "You are an expert Indian Public Policy, Governance, and Citizen Welfare Assistant. "
            "Analyze Government Gazettes, Ministry circulars, and Welfare Scheme (Yojana) guidelines. "
            "Separate eligibility criteria from disqualifications. "
            "Extract mandatory documents and application procedures. "
            "Provide a simple, jargon-free Jan Suvidha explanation for citizens. "
            "If asked in an Indic language, formulate the citizen summary in that language."
        ),
        "output_schema": "GovernanceOutput",
    },

    # ── Court Judgment (India AI / Law & Justice) ─────────────────────────────
    "judgment": {
        "chunk_size":              500,
        "chunk_overlap":           100,
        "top_k":                   15,
        "token_budget":            5000,
        "score_floor":             0.42,
        "precedent_tracking":      True,
        "system_prompt": (
            "You are an expert Indian Legal Intelligence Assistant. "
            "Analyze court judgments with strict judicial precision. "
            "Distinguish binding Ratio Decidendi from Obiter Dicta. "
            "Cite Indian statutory sections (IPC, BNS, CrPC, BNSS, Constitution) and case citations accurately. "
            "If asked in Hindi or regional language, formulate your judicial analysis in that language."
        ),
        "output_schema": "JudgmentOutput",
    },

    # ── Statutory Law & Criminal Concordance ─────────────────────────────────
    "law": {
        "chunk_size":    400,
        "chunk_overlap": 80,
        "top_k":         15,
        "token_budget":  4096,
        "score_floor":   0.40,
        "system_prompt": (
            "You are an expert Indian statutory legal analyst. Answer ONLY from retrieved clauses. "
            "Always cite the clause number and page. "
            "Cross-reference colonial codes (IPC, CrPC, IEA) with new Bharatiya Sanhitas (BNS, BNSS, BSA). "
            "Assign every answer a risk level: HIGH / MEDIUM / LOW. "
            "Never interpret beyond what is explicitly written in the document."
        ),
        "output_schema": "RiskOutput",
    },
}

# Legacy aliases mapped to core fellowship verticals
_LEGACY_ALIASES: Dict[str, str] = {
    "compliance": "law",
    "startup": "law",
    "university": "governance",
    "hr": "governance",
}

for _legacy_key, _target_key in _LEGACY_ALIASES.items():
    VERTICAL_CONFIGS[_legacy_key] = VERTICAL_CONFIGS[_target_key]

# Supported verticals for validation
SUPPORTED_VERTICALS = list(VERTICAL_CONFIGS.keys())
PRIMARY_FELLOWSHIP_VERTICALS = ["governance", "judgment", "law"]
