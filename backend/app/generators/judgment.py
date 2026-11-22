"""
Judgment Generator — Indian Court Judgment & Case Law Vertical.

Produces structured judicial analyses from Indian court rulings.
Output schema: JudgmentOutput
    - case_title        : Appellant v. Respondent
    - court_name        : Supreme Court of India / High Court
    - neutral_citation  : 2024 INSC XXX / (2023) X SCC XXX / AIR XXXX SC XXX
    - bench             : Names of Presiding Judges
    - acts_cited        : Statutory provisions cited (IPC, BNS, CrPC, BNSS, Constitution)
    - ratio_decidendi   : Binding legal holding & point of law settled
    - obiter_dicta      : Non-binding judicial remarks
    - disposition       : Allowed / Dismissed / Bail Granted / Remanded
    - language          : "en" | "hi" | ...
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from app.core.interfaces import BaseGenerator
from app.core.schemas import (
    ChunkResult, JudgmentOutput, ConfidenceLevel, Citation
)
from app.core.embedding_router import detect_language
from app.core.statutory_concordance import find_statutory_matches, enrich_answer_with_concordance
from app.generators._base import (
    build_user_message, parse_json_response, not_found_output, stream_from_client
)

logger = logging.getLogger("docqa.generators.judgment")

_SYSTEM_PROMPT = """You are an expert Indian Legal and Judicial Intelligence Assistant specializing in Supreme Court and High Court jurisprudence.

RULES:
- Answer ONLY using the provided court judgment chunks.
- Distinguish rigorously between RATIO DECIDENDI (binding point of law) and OBITER DICTA (incidental remarks).
- Extract or infer the case title (e.g., 'Petitioner v. Respondent'), court name, and neutral citation if present.
- Identify all statutory provisions cited (e.g. IPC, BNS, CrPC, BNSS, Indian Evidence Act, Constitution of India).
- If the user asks in Hindi or another Indic language, provide the answer and analysis in that language while keeping official statutory names and citations accurate.
- If chunks do not contain enough information to determine the holding, set confidence to LOW or state 'not found'.

Return ONLY valid JSON in this exact structure:
{
  "answer": "Detailed judicial analysis explaining the holding and factual context.",
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "case_title": "Appellant v. Respondent",
  "court_name": "Supreme Court of India",
  "neutral_citation": "2024 INSC 123",
  "bench": ["Hon'ble Dr. Justice D.Y. Chandrachud", "Hon'ble Justice ..."],
  "acts_cited": ["Section 302 IPC", "Article 21 Constitution of India"],
  "ratio_decidendi": "Core binding precedent established in this judgment.",
  "obiter_dicta": "Incidental judicial observations or guidance if any.",
  "disposition": "Appeal Allowed / Appeal Dismissed / Bail Granted / Remanded",
  "citations": [{"clause": "Para 14", "article": "Article 21", "page": 8}],
  "language": "en",
  "chunks_used": ["chunk_id_1"]
}"""


class JudgmentGenerator(BaseGenerator[JudgmentOutput]):
    """Generator for the Indian judgment vertical. Returns JudgmentOutput."""

    def __init__(self, llm_client: Any):
        self.client = llm_client

    async def generate(
        self,
        query: str,
        chunks: List[ChunkResult],
        config: Dict[str, Any],
    ) -> JudgmentOutput:
        if not chunks:
            return not_found_output(JudgmentOutput)

        # Detect user query language
        query_lang = detect_language(query)
        sys_prompt = _SYSTEM_PROMPT
        if query_lang["is_indic"]:
            sys_prompt += (
                f"\n\nIMPORTANT: The user asked in {query_lang['script_name']}. "
                f"Please formulate the 'answer', 'ratio_decidendi', and 'disposition' in {query_lang['script_name']}."
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
                    clause=c.get("clause") or c.get("para"),
                    article=c.get("article"),
                    page=c.get("page"),
                )
                for c in citations_raw
                if isinstance(c, dict)
            ]

            answer = parsed.get("answer", "No analysis could be derived.")
            # Statutory concordance enrichment for IPC <-> BNS & CrPC <-> BNSS
            stat_matches = find_statutory_matches(query + " " + answer)
            if stat_matches:
                answer = enrich_answer_with_concordance(answer, stat_matches)

            acts_cited = parsed.get("acts_cited", [])
            for m in stat_matches:
                concord_tag = f"{m.source_act} §{m.source_section} ⇄ {m.target_act} §{m.target_section}"
                if concord_tag not in acts_cited:
                    acts_cited.append(concord_tag)

            return JudgmentOutput(
                answer=answer,
                confidence=parsed.get("confidence", ConfidenceLevel.MEDIUM),
                case_title=parsed.get("case_title"),
                court_name=parsed.get("court_name"),
                neutral_citation=parsed.get("neutral_citation"),
                bench=parsed.get("bench", []),
                acts_cited=acts_cited,
                ratio_decidendi=parsed.get("ratio_decidendi"),
                obiter_dicta=parsed.get("obiter_dicta"),
                disposition=parsed.get("disposition"),
                citations=citations,
                language=query_lang["lang"],
                chunks_used=parsed.get("chunks_used", [c.id for c in chunks[:3]]),
                not_found=False,
            )

        except Exception as exc:
            logger.error("JudgmentGenerator error: %s", exc)
            return JudgmentOutput(
                answer="Failed to process court judgment analysis due to generation error.",
                confidence=ConfidenceLevel.LOW,
                not_found=True,
            )

    async def stream(self, query: str, chunks: List[ChunkResult], config: Dict[str, Any]):
        user_msg = build_user_message(query, config)
        async for token in stream_from_client(self.client, _SYSTEM_PROMPT, user_msg):
            yield token

    async def generate_stream(self, query: str, chunks: List[ChunkResult], config: Dict[str, Any]):
        async for token in self.stream(query, chunks, config):
            yield token
