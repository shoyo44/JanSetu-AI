"""
Sovereign Guardrails — Public Governance & Legal AI Safety Shield.
Complies with MeitY AI Safety Directives, UIDAI Aadhaar Regulations, and Digital Personal Data Protection (DPDP) Act 2023.
"""
from __future__ import annotations

import re
from typing import Optional, Tuple, List

# ── 1. Jailbreak & Prompt Injection Patterns ──────────────────────────────────
_JAILBREAK_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|directives|prompts|rules)",
    r"disregard\s+(all\s+)?(previous|prior|above|the\s+system)",
    r"you\s+are\s+now\s+(in\s+)?(developer|god|unrestricted|jailbreak|jailbroken|dan)\s+mode",
    r"act\s+as\s+(a\s+)?(jailbroken|dan|unrestricted|adversary|malicious)\s+(ai|assistant|model|agent)",
    r"(reveal|print|leak|output|dump|echo)\s+(your\s+)?(full\s+)?(system\s+)?(prompt|instructions|rules|preprompt)",
    r"<\|im_start\|>|<\|im_end\|>|<\|endoftext\|>",
    r"\[INST\]|\[\/INST\]|<<SYS>>|<\/SYS>>",
    r"###\s*(SYSTEM|INSTRUCTION|HUMAN|ASSISTANT)\s*:",
    r"---+\s*BEGIN\s+(ADMIN|SYSTEM|DEVELOPER)\s+(OVERRIDE|INSTRUCTION)",
]

# ── 2. Sovereign Government Document Forgery & Fraud Patterns ─────────────────
_GOV_FRAUD_PATTERNS: List[Tuple[str, str]] = [
    (
        r"(create|generate|forge|fake|duplicate|counterfeit)\s+(fake\s+)?(aadhaar|pan|voter\s*id|ration\s*card|patta|chitta|7/12|land\s*deed|pattiram)",
        "Creation or forgery of fake Government of India identity cards or land records is strictly prohibited under the IPC/BNS and Aadhaar Act.",
    ),
    (
        r"(bypass|hack|spoof|exploit|trick)\s+(biometric|e-?kyc|aadhaar\s*auth|fingerprint|otp\s*verification|patwari|talathi)",
        "Attempts to bypass, spoof, or compromise statutory e-KYC or official revenue verification protocols are blocked.",
    ),
    (
        r"(create|script|phish|send)\s+(fake|fraudulent|deceptive)\s+(pm-?kisan|pm-?jay|dbt|subsidy)\s+(sms|apk|link|message)",
        "Generation of fraudulent messages or APKs imitating official Government welfare portals is strictly blocked.",
    ),
    (
        r"(how\s+to\s+bribe|pay\s+bribe|corrupt|influence)\s+(patwari|tahsildar|officer|judge|nodal\s*officer)",
        "Queries encouraging corruption or illicit influence over public officials violate anti-corruption statutory guidelines (Prevention of Corruption Act).",
    ),
]

# ── 3. Cyber Exploit & Threat Terms ───────────────────────────────────────────
_CYBER_THREAT_TERMS = [
    "bypass authentication",
    "malware",
    "ddos execution",
    "brute force login",
    "sql injection attack",
    "reverse shell",
    "exploit government portal",
]

# ── 4. PII Redaction Regexes (Aadhaar & PAN) ─────────────────────────────────
_AADHAAR_REGEX = re.compile(r"\b([2-9]\d{3})[\s-]?(\d{4})[\s-]?(\d{4})\b")
_PAN_REGEX = re.compile(r"\b([A-Z]{5})(\d{4})([A-Z]{1})\b")


def mask_pii(text: str) -> str:
    """
    Mask raw citizen PII in compliance with Section 29 of the Aadhaar Act
    and India's DPDP Act 2023.
    Transforms:
      Aadhaar: '2345 6789 0123' -> 'XXXX-XXXX-0123'
      PAN:     'ABCDE1234F'     -> 'XXXXX1234F'
    """
    if not text:
        return ""
    # Mask 12-digit Aadhaar
    text = _AADHAAR_REGEX.sub(r"XXXX-XXXX-\3", text)
    # Mask 10-char PAN
    text = _PAN_REGEX.sub(r"XXXXX\2\3", text)
    return text


def check_guardrails(query: str) -> Optional[str]:
    """
    Sovereign Safety Check: Validate queries for prompt injection, fraud,
    forgery, and cyber exploits.
    Returns refusal message if violation is found, else None.
    """
    if not query or not query.strip():
        return None

    q_lower = query.lower()

    # 1. Jailbreak & Prompt Injection
    for pattern in _JAILBREAK_PATTERNS:
        if re.search(pattern, q_lower):
            return "🛡️ Sovereign Security Guardrail: Query blocked (detected adversarial prompt injection / jailbreak attempt)."

    # 2. Government Document Forgery & e-KYC Fraud
    for pattern, refusal in _GOV_FRAUD_PATTERNS:
        if re.search(pattern, q_lower):
            return f"🛡️ National Safety Advisory: {refusal}"

    # 3. Cyber Threat Terms
    for term in _CYBER_THREAT_TERMS:
        if term in q_lower:
            return f"🛡️ Cyber Defense Guardrail: Request blocked due to restricted security terms ('{term}')."

    return None
