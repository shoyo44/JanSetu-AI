"""
Governance & Public Policy Generator — India AI Fellowship Vertical.

Synthesizes policy analysis and citizen welfare eligibility from Government Gazettes,
Ministry Circulars, and Scheme (Yojana) Guidelines.

Output schema: GovernanceOutput
    - scheme_name                 : e.g. "PM-KISAN", "Ayushman Bharat PM-JAY"
    - nodal_ministry              : e.g. "Ministry of Agriculture & Farmers Welfare"
    - gazette_reference           : e.g. "G.S.R. 412(E)"
    - jan_suvidha_summary         : Plain language citizen-centric explanation
    - eligibility_criteria        : Bullet points of required beneficiary qualifications
    - exclusion_criteria          : Who is disqualified / excluded
    - benefits                    : Direct DBT subsidies, financial coverage, services
    - required_documents          : Mandatory documentation (Aadhaar, Land records, etc.)
    - application_steps           : Step-by-step how to apply (CSC, Portal, Block office)
    - official_portal_or_helpline : URL or toll-free number
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from app.core.interfaces import BaseGenerator
from app.core.schemas import (
    ChunkResult, GovernanceOutput, ConfidenceLevel, Citation
)
from app.core.embedding_router import detect_language
from app.generators._base import (
    build_user_message, parse_json_response, not_found_output, stream_from_client
)

logger = logging.getLogger("docqa.generators.governance")

_SYSTEM_PROMPT = """You are an expert Indian Public Policy, Governance, and Citizen Welfare Intelligence Assistant.
Your mission is to analyze Government Gazettes, Ministry guidelines, and Welfare Schemes (Yojanas),
and provide both official administrative rigor and a simple citizen-centric explanation (Jan Suvidha).

RULES:
- Answer ONLY using the provided governance/policy chunks.
- Extract or identify the Scheme Name, Nodal Ministry, and Gazette reference if present.
- Provide a clear, jargon-free 'jan_suvidha_summary' that any rural or urban citizen can easily understand.
- Explicitly separate ELIGIBILITY CRITERIA from EXCLUSION CRITERIA.
- List all mandatory REQUIRED DOCUMENTS (Aadhaar, Ration Card, Bank Passbook, 7/12 Land records, etc.).
- List APPLICATION STEPS (e.g. Common Service Center / CSC, online portal, Gram Panchayat office).
- If the user asks in Hindi or another Indic language, provide the answer and jan_suvidha_summary in that language.
- If chunks do not contain enough information, state clearly that it was not found in the official record.

Return ONLY valid JSON in this exact structure:
{
  "answer": "Detailed administrative and policy response with statutory citations.",
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "scheme_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
  "nodal_ministry": "Ministry of Agriculture & Farmers Welfare",
  "gazette_reference": "G.S.R. 123(E)",
  "jan_suvidha_summary": "Simple citizen-friendly explanation of what this scheme is, who gets it, and how much money/support is provided.",
  "eligibility_criteria": [
    "All landholder farmer families with cultivable land in state land records (subject to exclusion criteria).",
    "Must have valid bank account linked with Aadhaar and completed e-KYC."
  ],
  "exclusion_criteria": [
    "Institutional landholders.",
    "Persons who paid income tax in last assessment year.",
    "Constitutional post holders or retired government employees."
  ],
  "benefits": [
    "₹6,000 per year paid in three equal 4-monthly installments of ₹2,000 via Direct Benefit Transfer (DBT)."
  ],
  "required_documents": [
    "Aadhaar Card",
    "Land Ownership Record (Khatauni / Patta / 7-12)",
    "Bank Account Passbook (Aadhaar-seeded)"
  ],
  "application_steps": [
    "Step 1: Visit nearest Common Service Centre (CSC) or official portal pmkisan.gov.in.",
    "Step 2: Submit farmer registration form with Aadhaar and land details.",
    "Step 3: Verification by State Nodal Officer and Block Revenue Inspector."
  ],
  "official_portal_or_helpline": "pmkisan.gov.in | Kisan Call Centre: 1800-180-1551",
  "citations": [{"clause": "Section 4.1", "page": 3}],
  "chunks_used": ["chunk_id_1"]
}"""


class GovernanceGenerator(BaseGenerator[GovernanceOutput]):
    """Generator for the Governance & Public Policy vertical."""

    def __init__(self, llm_client: Any):
        self.client = llm_client

    async def generate(
        self,
        query: str,
        chunks: List[ChunkResult],
        config: Dict[str, Any],
    ) -> GovernanceOutput:
        if not chunks:
            return not_found_output(GovernanceOutput)

        # Detect user query language
        query_lang = detect_language(query)
        sys_prompt = _SYSTEM_PROMPT
        if query_lang["is_indic"]:
            sys_prompt += (
                f"\n\nIMPORTANT: The user asked in {query_lang['script_name']}. "
                f"Please formulate the 'answer' and 'jan_suvidha_summary' in {query_lang['script_name']}."
            )

        user_msg = build_user_message(query, config)

        try:
            token_limit = config.get("max_tokens", 2200 if query_lang["is_indic"] else 1400)
            raw = await self.client.chat(
                system_prompt=sys_prompt,
                user_message=user_msg,
                max_tokens=token_limit,
                temperature=config.get("temperature", 0.05),
            )
            parsed = parse_json_response(raw)

            citations_raw = parsed.get("citations", [])
            citations = [
                Citation(
                    clause=c.get("clause") or c.get("section") or c.get("para"),
                    article=c.get("article") or c.get("facet"),
                    page=c.get("page"),
                )
                for c in citations_raw
                if isinstance(c, dict)
            ]

            return GovernanceOutput(
                answer=parsed.get("answer", "Analysis complete."),
                confidence=ConfidenceLevel(parsed.get("confidence", "MEDIUM")),
                scheme_name=parsed.get("scheme_name"),
                nodal_ministry=parsed.get("nodal_ministry"),
                gazette_reference=parsed.get("gazette_reference"),
                jan_suvidha_summary=parsed.get("jan_suvidha_summary"),
                eligibility_criteria=parsed.get("eligibility_criteria", []),
                exclusion_criteria=parsed.get("exclusion_criteria", []),
                benefits=parsed.get("benefits", []),
                required_documents=parsed.get("required_documents", []),
                application_steps=parsed.get("application_steps", []),
                official_portal_or_helpline=parsed.get("official_portal_or_helpline"),
                citations=citations,
                chunks_used=parsed.get("chunks_used", [c.id for c in chunks]),
            )
        except Exception as exc:
            logger.error("Governance generator error: %s", exc)
            return GovernanceOutput(
                answer=f"Could not parse governance analysis: {exc}",
                confidence=ConfidenceLevel.LOW,
                not_found=True,
                chunks_used=[c.id for c in chunks],
            )

    async def stream(self, query: str, chunks: List[ChunkResult], config: Dict[str, Any]):
        user_msg = build_user_message(query, config)
        async for token in stream_from_client(self.client, _SYSTEM_PROMPT, user_msg):
            yield token

    async def generate_stream(self, query: str, chunks: List[ChunkResult], config: Dict[str, Any]):
        async for token in self.stream(query, chunks, config):
            yield token
