"""
Document-Level Indirect Prompt Injection Scanner.

Scans extracted document chunks prior to vector embedding and FAISS indexing
to detect and quarantine adversarial jailbreak, override, and data exfiltration patterns.

Attack vectors defended against:
1. Direct Instruction Overrides: "Ignore all previous instructions", "Disregard the above"
2. Role/Persona Hijacking: "You are now in DAN/unrestricted mode", "Act as a jailbroken AI"
3. ChatML & Special Delimiter Injections: "<|im_start|>", "[INST]", "### SYSTEM", "<<SYS>>"
4. System Prompt Exfiltration: "Reveal your system prompt", "Print initial instructions"
5. Delimiter Evasion & Instruction Masquerading: "--- BEGIN ADMIN OVERRIDE ---", "[SYSTEM NOTE: ...]"
6. Steganographic / ASCII Smuggling: Excessive zero-width spaces (\u200b, \u200c, \u200d, \ufeff)
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("docqa.security.doc_injection")

# ─── Threat Signatures ────────────────────────────────────────────────────────

# Critical patterns: Direct jailbreaks and instruction overrides -> Quarantine
CRITICAL_INJECTION_PATTERNS: List[Tuple[str, str]] = [
    (
        r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|directives|prompts|rules)",
        "DIRECT_INSTRUCTION_OVERRIDE",
    ),
    (
        r"disregard\s+(all\s+)?(previous|prior|above|the\s+system)\s+(instructions|directives|prompts|rules)",
        "DISREGARD_INSTRUCTION_OVERRIDE",
    ),
    (
        r"you\s+are\s+now\s+(in\s+)?(developer|god|unrestricted|jailbreak|jailbroken|dan)\s+mode",
        "PERSONA_JAILBREAK",
    ),
    (
        r"act\s+as\s+(a\s+)?(jailbroken|dan|unrestricted|adversary|malicious)\s+(ai|assistant|model|agent)",
        "PERSONA_HIJACK",
    ),
    (
        r"(reveal|print|leak|output|dump|echo)\s+(your\s+)?(full\s+)?(system\s+)?(prompt|instructions|rules|preprompt)",
        "PROMPT_EXFILTRATION",
    ),
    (
        r"<\|im_start\|>|<\|im_end\|>|<\|endoftext\|>",
        "CHATML_DELIMITER_INJECTION",
    ),
    (
        r"\[INST\]|\[\/INST\]|<<SYS>>|<\/SYS>>",
        "LLAMA_DELIMITER_INJECTION",
    ),
    (
        r"###\s*(SYSTEM|INSTRUCTION|HUMAN|ASSISTANT)\s*:",
        "PROMPT_TEMPLATE_SPOOFING",
    ),
    (
        r"---+\s*BEGIN\s+(ADMIN|SYSTEM|DEVELOPER)\s+(OVERRIDE|INSTRUCTION)",
        "ADMIN_OVERRIDE_DELIMITER",
    ),
    (
        r"you\s+are\s+no\s+longer\s+bound\s+by\s+(any\s+)?(rules|safety|guidelines|policies)",
        "POLICY_BYPASS_CLAIM",
    ),
    (
        r"do\s+not\s+follow\s+(the\s+)?(original|standard|safety)\s+protocol",
        "PROTOCOL_OVERRIDE",
    ),
]

# Suspicious patterns: Instruction-like phrasing embedded in text -> Sanitize
SUSPICIOUS_INJECTION_PATTERNS: List[Tuple[str, str]] = [
    (
        r"important\s+(note|instruction)\s+to\s+(the\s+)?(ai|assistant|model|llm)\s*:",
        "INSTRUCTION_MASQUERADING",
    ),
    (
        r"\[system\s*note\s*:.*?\]",
        "SYSTEM_NOTE_TAG",
    ),
    (
        r"ai\s+override\s*:",
        "AI_OVERRIDE_PREFIX",
    ),
    (
        r"please\s+ignore\s+what\s+was\s+written\s+before",
        "POLITE_OVERRIDE_ATTEMPT",
    ),
]

# Steganography / Zero-width characters for ASCII smuggling
ZERO_WIDTH_CHARS = ["\u200b", "\u200c", "\u200d", "\ufeff", "\u2060", "\u200e", "\u200f"]


@dataclass
class InjectionScanResult:
    is_suspicious: bool = False
    quarantined: bool = False
    threat_level: str = "SAFE"       # SAFE, SUSPICIOUS, CRITICAL
    risk_score: float = 0.0          # 0.0 - 1.0
    matched_patterns: List[str] = field(default_factory=list)
    sanitized_text: str = ""
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_suspicious": self.is_suspicious,
            "quarantined": self.quarantined,
            "threat_level": self.threat_level,
            "risk_score": round(self.risk_score, 3),
            "matched_patterns": self.matched_patterns,
            "reasons": self.reasons,
        }


def _strip_zero_width_chars(text: str) -> Tuple[str, int]:
    """Removes invisible zero-width unicode characters and counts occurrences."""
    total_stripped = 0
    cleaned = text
    for zwc in ZERO_WIDTH_CHARS:
        count = cleaned.count(zwc)
        if count > 0:
            total_stripped += count
            cleaned = cleaned.replace(zwc, "")
    return cleaned, total_stripped


def scan_chunk(
    text: str,
    quarantine_threshold: float = 0.6,
) -> InjectionScanResult:
    """
    Scans a single document chunk for indirect prompt injection indicators.

    Returns InjectionScanResult with quarantine flag and sanitized text.
    """
    if not text:
        return InjectionScanResult(sanitized_text="")

    matched_patterns: List[str] = []
    reasons: List[str] = []
    risk_score = 0.0

    # 1. Zero-width character inspection (ASCII Smuggling / Steganography)
    cleaned_text, zwc_count = _strip_zero_width_chars(text)
    if zwc_count >= 10:
        matched_patterns.append("ZERO_WIDTH_STEGANOGRAPHY")
        reasons.append(f"Detected {zwc_count} invisible zero-width unicode characters.")
        risk_score += 0.55
    elif zwc_count > 0:
        reasons.append(f"Stripped {zwc_count} zero-width characters.")

    # 2. Check Critical Patterns (Jailbreaks & Direct Overrides)
    cleaned_lower = cleaned_text.lower()
    for pattern, name in CRITICAL_INJECTION_PATTERNS:
        match = re.search(pattern, cleaned_lower, re.IGNORECASE)
        if match:
            matched_patterns.append(name)
            reasons.append(f"Matched critical injection pattern: '{match.group(0)}'")
            risk_score += 0.75

    # 3. Check Suspicious Patterns (Instruction masquerading)
    for pattern, name in SUSPICIOUS_INJECTION_PATTERNS:
        match = re.search(pattern, cleaned_lower, re.IGNORECASE)
        if match:
            matched_patterns.append(name)
            reasons.append(f"Matched suspicious pattern: '{match.group(0)}'")
            risk_score += 0.35

    # Cap risk score at 1.0
    risk_score = min(risk_score, 1.0)

    # Determine Threat Level
    if risk_score >= quarantine_threshold:
        threat_level = "CRITICAL"
        quarantined = True
        is_suspicious = True
        # For quarantined chunks, we retain text for auditing but flag it
        sanitized_text = f"[QUARANTINED CONTENT - THREAT DETECTED: {', '.join(matched_patterns)}]"
    elif risk_score >= 0.3:
        threat_level = "SUSPICIOUS"
        quarantined = False
        is_suspicious = True
        # Sanitize suspicious text by neutralizing markdown and wrapping in strict context tags
        sanitized_text = re.sub(r"[<>]", "", cleaned_text)
    else:
        threat_level = "SAFE"
        quarantined = False
        is_suspicious = False
        sanitized_text = cleaned_text

    return InjectionScanResult(
        is_suspicious=is_suspicious,
        quarantined=quarantined,
        threat_level=threat_level,
        risk_score=risk_score,
        matched_patterns=matched_patterns,
        sanitized_text=sanitized_text,
        reasons=reasons,
    )


def scan_document_chunks(
    chunks: List[Dict[str, Any]],
    quarantine_threshold: float = 0.6,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Scans all chunks of a document before indexing.

    Args:
        chunks: List of chunk dictionaries (must contain "text").
        quarantine_threshold: Risk score threshold for quarantining a chunk.

    Returns:
        (safe_chunks, quarantined_chunks, scan_summary)
    """
    safe_chunks: List[Dict[str, Any]] = []
    quarantined_chunks: List[Dict[str, Any]] = []
    critical_count = 0
    suspicious_count = 0
    all_matched_patterns: List[str] = []

    for chunk in chunks:
        raw_text = chunk.get("text", "")
        scan_res = scan_chunk(raw_text, quarantine_threshold=quarantine_threshold)

        if scan_res.quarantined:
            critical_count += 1
            all_matched_patterns.extend(scan_res.matched_patterns)
            quarantined_record = {
                **chunk,
                "text": scan_res.sanitized_text,
                "raw_text": raw_text,
                "quarantined": True,
                "injected": True,
                "threat_level": scan_res.threat_level,
                "risk_score": scan_res.risk_score,
                "matched_patterns": scan_res.matched_patterns,
                "reasons": scan_res.reasons,
            }
            quarantined_chunks.append(quarantined_record)
            logger.warning(
                "🚨 QUARANTINED chunk (doc_id=%s, page=%s): %s",
                chunk.get("doc_id", "unknown"),
                chunk.get("page", "?"),
                scan_res.reasons,
            )
        else:
            if scan_res.is_suspicious:
                suspicious_count += 1
                all_matched_patterns.extend(scan_res.matched_patterns)
                safe_chunks.append({
                    **chunk,
                    "text": scan_res.sanitized_text,
                    "quarantined": False,
                    "injected": False,
                    "threat_level": scan_res.threat_level,
                    "risk_score": scan_res.risk_score,
                    "matched_patterns": scan_res.matched_patterns,
                })
            else:
                safe_chunks.append({
                    **chunk,
                    "text": scan_res.sanitized_text,
                    "quarantined": False,
                    "injected": False,
                    "threat_level": "SAFE",
                    "risk_score": 0.0,
                    "matched_patterns": [],
                })

    scan_summary = {
        "total_chunks_scanned": len(chunks),
        "safe_chunks_count": len(safe_chunks),
        "quarantined_chunks_count": len(quarantined_chunks),
        "suspicious_chunks_count": suspicious_count,
        "is_compromised": len(quarantined_chunks) > 0,
        "matched_patterns": list(set(all_matched_patterns)),
    }

    if scan_summary["is_compromised"]:
        logger.warning(
            "Document scan detected %d adversarial prompt injection chunk(s) quarantined out of %d.",
            len(quarantined_chunks),
            len(chunks),
        )

    return safe_chunks, quarantined_chunks, scan_summary
