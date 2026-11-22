"""
Indian Statutory Concordance Engine (IPC <-> BNS, CrPC <-> BNSS, IEA <-> BSA).

Provides real-time statutory cross-referencing between historic colonial criminal codes
and the new criminal laws enacted under the Bharatiya criminal jurisprudence (effective July 1, 2024):
  - Indian Penal Code, 1860 (IPC) <-> Bharatiya Nyaya Sanhita, 2023 (BNS)
  - Code of Criminal Procedure, 1973 (CrPC) <-> Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)
  - Indian Evidence Act, 1872 (IEA) <-> Bharatiya Sakshya Adhiniyam, 2023 (BSA)

Vital for Indian legal practitioners, law enforcement, and judiciary transitioning between
pre-2024 case law and new statutory charges.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# ─── IPC <-> BNS Concordance Table ───────────────────────────────────────────
IPC_TO_BNS: Dict[str, Dict[str, str]] = {
    "124A": {
        "bns": "152",
        "title": "Act endangering sovereignty, unity, and integrity of India (replaces Sedition)",
        "punishment": "Imprisonment for life or up to 7 years + fine",
    },
    "302": {
        "bns": "103(1)",
        "title": "Punishment for Murder",
        "punishment": "Death or imprisonment for life + fine",
    },
    "304": {
        "bns": "105",
        "title": "Culpable homicide not amounting to murder",
        "punishment": "Imprisonment for life or up to 10 years + fine",
    },
    "304A": {
        "bns": "106(1)",
        "title": "Causing death by negligence",
        "punishment": "Imprisonment up to 5 years + fine",
    },
    "304B": {
        "bns": "80",
        "title": "Dowry death",
        "punishment": "Imprisonment not less than 7 years up to life",
    },
    "307": {
        "bns": "109",
        "title": "Attempt to murder",
        "punishment": "Imprisonment up to 10 years + fine, up to life if hurt is caused",
    },
    "323": {
        "bns": "115(2)",
        "title": "Voluntarily causing hurt",
        "punishment": "Imprisonment up to 1 year or fine up to ₹10,000",
    },
    "324": {
        "bns": "117(1)",
        "title": "Voluntarily causing hurt by dangerous weapons or means",
        "punishment": "Imprisonment up to 3 years or fine",
    },
    "325": {
        "bns": "116(2)",
        "title": "Voluntarily causing grievous hurt",
        "punishment": "Imprisonment up to 7 years + fine",
    },
    "341": {
        "bns": "126(2)",
        "title": "Wrongful restraint",
        "punishment": "Simple imprisonment up to 1 month or fine up to ₹5,000",
    },
    "354": {
        "bns": "74",
        "title": "Assault or criminal force to woman with intent to outrage her modesty",
        "punishment": "Imprisonment 1 to 5 years + fine",
    },
    "354A": {
        "bns": "75",
        "title": "Sexual harassment",
        "punishment": "Rigorous imprisonment up to 3 years or fine",
    },
    "363": {
        "bns": "137(2)",
        "title": "Punishment for kidnapping",
        "punishment": "Imprisonment up to 7 years + fine",
    },
    "376": {
        "bns": "64(1)",
        "title": "Punishment for rape",
        "punishment": "Rigorous imprisonment not less than 10 years up to life",
    },
    "378": {
        "bns": "303(1)",
        "title": "Theft definition",
        "punishment": "Refer to 303(2)",
    },
    "379": {
        "bns": "303(2)",
        "title": "Punishment for theft",
        "punishment": "Imprisonment up to 3 years or fine or community service",
    },
    "380": {
        "bns": "305",
        "title": "Theft in dwelling house or transport",
        "punishment": "Imprisonment up to 7 years + fine",
    },
    "384": {
        "bns": "308(2)",
        "title": "Extortion",
        "punishment": "Imprisonment up to 3 years or fine",
    },
    "392": {
        "bns": "309(4)",
        "title": "Punishment for robbery",
        "punishment": "Rigorous imprisonment up to 10 years + fine",
    },
    "406": {
        "bns": "316(2)",
        "title": "Criminal breach of trust",
        "punishment": "Imprisonment up to 5 years or fine",
    },
    "420": {
        "bns": "318(4)",
        "title": "Cheating and dishonestly inducing delivery of property",
        "punishment": "Imprisonment up to 7 years + fine",
    },
    "498A": {
        "bns": "85",
        "title": "Husband or relative of husband subjecting woman to cruelty",
        "punishment": "Imprisonment up to 3 years + fine",
    },
    "506": {
        "bns": "351(2)",
        "title": "Criminal intimidation",
        "punishment": "Imprisonment up to 2 years or fine",
    },
    "509": {
        "bns": "79",
        "title": "Word, gesture or act intended to insult modesty of a woman",
        "punishment": "Simple imprisonment up to 3 years + fine",
    },
}

# Invert table for BNS -> IPC lookup
BNS_TO_IPC: Dict[str, Dict[str, str]] = {}
for ipc_sec, data in IPC_TO_BNS.items():
    bns_clean = data["bns"].split("(")[0]
    BNS_TO_IPC[bns_clean] = {
        "ipc": ipc_sec,
        "title": data["title"],
        "punishment": data["punishment"],
    }
    # Also index with full string if different
    if data["bns"] != bns_clean:
        BNS_TO_IPC[data["bns"]] = {
            "ipc": ipc_sec,
            "title": data["title"],
            "punishment": data["punishment"],
        }


# ─── CrPC <-> BNSS Concordance Table ─────────────────────────────────────────
CRPC_TO_BNSS: Dict[str, Dict[str, str]] = {
    "41A": {
        "bnss": "35(3)",
        "title": "Notice of appearance before police officer",
    },
    "82": {
        "bnss": "84",
        "title": "Proclamation for person absconding",
    },
    "83": {
        "bnss": "85",
        "title": "Attachment of property of person absconding",
    },
    "154": {
        "bnss": "173",
        "title": "Information in cognizable cases (FIR / e-FIR / Zero FIR)",
    },
    "161": {
        "bnss": "180",
        "title": "Examination of witnesses by police",
    },
    "164": {
        "bnss": "183",
        "title": "Recording of confessions and statements before Magistrate",
    },
    "167": {
        "bnss": "187",
        "title": "Procedure when investigation cannot be completed in 24 hours (Remand)",
    },
    "173": {
        "bnss": "193",
        "title": "Report of police officer on completion of investigation (Chargesheet)",
    },
    "313": {
        "bnss": "351",
        "title": "Power to examine the accused person",
    },
    "436A": {
        "bnss": "479",
        "title": "Maximum period for which an undertrial prisoner can be detained (first-time offender release after 1/3rd detention)",
    },
    "437": {
        "bnss": "480",
        "title": "When bail may be taken in case of non-bailable offence (Magistrate Bail)",
    },
    "438": {
        "bnss": "482",
        "title": "Direction for grant of bail to person apprehending arrest (Anticipatory Bail)",
    },
    "439": {
        "bnss": "483",
        "title": "Special powers of High Court or Court of Session regarding bail (Regular Bail)",
    },
    "482": {
        "bnss": "528",
        "title": "Saving of inherent powers of High Court (Quashing of FIR/proceedings)",
    },
}

BNSS_TO_CRPC: Dict[str, Dict[str, str]] = {}
for crpc_sec, data in CRPC_TO_BNSS.items():
    bnss_clean = data["bnss"].split("(")[0]
    BNSS_TO_CRPC[bnss_clean] = {"crpc": crpc_sec, "title": data["title"]}
    if data["bnss"] != bnss_clean:
        BNSS_TO_CRPC[data["bnss"]] = {"crpc": crpc_sec, "title": data["title"]}


# ─── IEA <-> BSA Concordance Table ───────────────────────────────────────────
IEA_TO_BSA: Dict[str, Dict[str, str]] = {
    "25": {"bsa": "23", "title": "Confession to police officer not to be proved"},
    "27": {"bsa": "23(2)", "title": "How much of information received from accused may be proved (Discovery)"},
    "32": {"bsa": "26", "title": "Cases in which statement of relevant fact by person who is dead or cannot be found is relevant (Dying Declaration)"},
    "65B": {"bsa": "63", "title": "Admissibility of electronic records and digital certificates"},
    "113A": {"bsa": "117", "title": "Presumption as to abetment of suicide by a married woman"},
    "113B": {"bsa": "118", "title": "Presumption as to dowry death"},
}

BSA_TO_IEA: Dict[str, Dict[str, str]] = {}
for iea_sec, data in IEA_TO_BSA.items():
    bsa_clean = data["bsa"].split("(")[0]
    BSA_TO_IEA[bsa_clean] = {"iea": iea_sec, "title": data["title"]}
    if data["bsa"] != bsa_clean:
        BSA_TO_IEA[data["bsa"]] = {"iea": iea_sec, "title": data["title"]}


# ─── Lookup Classes & Functions ──────────────────────────────────────────────

@dataclass
class ConcordanceMatch:
    source_act: str       # IPC, BNS, CrPC, BNSS, IEA, BSA
    source_section: str
    target_act: str
    target_section: str
    title: str
    punishment_or_note: str = ""

    def formatted_badge(self) -> str:
        return f"{self.source_act} §{self.source_section} ⇄ {self.target_act} §{self.target_section}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_act": self.source_act,
            "source_section": self.source_section,
            "target_act": self.target_act,
            "target_section": self.target_section,
            "title": self.title,
            "punishment_or_note": self.punishment_or_note,
            "badge": self.formatted_badge(),
        }


def find_statutory_matches(text: str) -> List[ConcordanceMatch]:
    """
    Scans a text query or judgment excerpt to detect statutory sections and
    returns corresponding pre/post 2024 equivalent criminal sections.
    """
    matches: List[ConcordanceMatch] = []
    seen = set()

    # 1. Look for IPC sections (e.g. "Section 420 IPC", "IPC 302", "sec 498A of IPC", "s. 307 ipc")
    ipc_patterns = [
        r"(?:section|sec|s\.?)\s*(\d+[A-Z]?)\s*(?:of\s*(?:the\s*)?)?ipc\b",
        r"\bipc\s*(?:section|sec|s\.?)?\s*(\d+[A-Z]?)\b",
    ]
    for pat in ipc_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            sec = m.group(1).upper()
            if sec in IPC_TO_BNS and sec not in seen:
                seen.add(sec)
                info = IPC_TO_BNS[sec]
                matches.append(ConcordanceMatch(
                    source_act="IPC (1860)",
                    source_section=sec,
                    target_act="BNS (2023)",
                    target_section=info["bns"],
                    title=info["title"],
                    punishment_or_note=info.get("punishment", ""),
                ))

    # 2. Look for BNS sections (e.g. "Section 318 BNS", "BNS 103")
    bns_patterns = [
        r"(?:section|sec|s\.?)\s*(\d+[A-Z]?)\s*(?:of\s*(?:the\s*)?)?bns\b",
        r"\bbns\s*(?:section|sec|s\.?)?\s*(\d+[A-Z]?)\b",
    ]
    for pat in bns_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            sec = m.group(1).upper()
            if sec in BNS_TO_IPC and f"BNS_{sec}" not in seen:
                seen.add(f"BNS_{sec}")
                info = BNS_TO_IPC[sec]
                matches.append(ConcordanceMatch(
                    source_act="BNS (2023)",
                    source_section=sec,
                    target_act="IPC (1860)",
                    target_section=info["ipc"],
                    title=info["title"],
                    punishment_or_note=info.get("punishment", ""),
                ))

    # 3. Look for CrPC sections (e.g. "Section 439 CrPC", "CrPC 482")
    crpc_patterns = [
        r"(?:section|sec|s\.?)\s*(\d+[A-Z]?)\s*(?:of\s*(?:the\s*)?)?crpc\b",
        r"\bcrpc\s*(?:section|sec|s\.?)?\s*(\d+[A-Z]?)\b",
    ]
    for pat in crpc_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            sec = m.group(1).upper()
            if sec in CRPC_TO_BNSS and f"CRPC_{sec}" not in seen:
                seen.add(f"CRPC_{sec}")
                info = CRPC_TO_BNSS[sec]
                matches.append(ConcordanceMatch(
                    source_act="CrPC (1973)",
                    source_section=sec,
                    target_act="BNSS (2023)",
                    target_section=info["bnss"],
                    title=info["title"],
                ))

    # 4. Look for BNSS sections
    bnss_patterns = [
        r"(?:section|sec|s\.?)\s*(\d+[A-Z]?)\s*(?:of\s*(?:the\s*)?)?bnss\b",
        r"\bbnss\s*(?:section|sec|s\.?)?\s*(\d+[A-Z]?)\b",
    ]
    for pat in bnss_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            sec = m.group(1).upper()
            if sec in BNSS_TO_CRPC and f"BNSS_{sec}" not in seen:
                seen.add(f"BNSS_{sec}")
                info = BNSS_TO_CRPC[sec]
                matches.append(ConcordanceMatch(
                    source_act="BNSS (2023)",
                    source_section=sec,
                    target_act="CrPC (1973)",
                    target_section=info["crpc"],
                    title=info["title"],
                ))

    # 5. Look for IEA sections (e.g. "Section 65B Evidence Act", "IEA 27")
    iea_patterns = [
        r"(?:section|sec|s\.?)\s*(\d+[A-Z]?)\s*(?:of\s*(?:the\s*)?)?(?:evidence\s+act|iea)\b",
        r"\b(?:evidence\s+act|iea)\s*(?:section|sec|s\.?)?\s*(\d+[A-Z]?)\b",
    ]
    for pat in iea_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            sec = m.group(1).upper()
            if sec in IEA_TO_BSA and f"IEA_{sec}" not in seen:
                seen.add(f"IEA_{sec}")
                info = IEA_TO_BSA[sec]
                matches.append(ConcordanceMatch(
                    source_act="IEA (1872)",
                    source_section=sec,
                    target_act="BSA (2023)",
                    target_section=info["bsa"],
                    title=info["title"],
                ))

    return matches


def enrich_answer_with_concordance(answer: str, matches: List[ConcordanceMatch]) -> str:
    """
    Appends an official India Law statutory concordance note to an answer.
    """
    if not matches:
        return answer

    concordance_block = "\n\n> ⚖️ **Indian Criminal Law Statutory Concordance (July 1, 2024 Transition):**\n"
    for m in matches:
        punish_str = f" — *{m.punishment_or_note}*" if m.punishment_or_note else ""
        concordance_block += (
            f"> - **{m.source_act} §{m.source_section}** corresponds to **{m.target_act} §{m.target_section}** "
            f"(*{m.title}*){punish_str}\n"
        )

    return answer + concordance_block


# ── Undertrial Detention Relief Rule Engine (BNSS §479 / CrPC §436A) ──────────

def evaluate_undertrial_relief(
    offence_max_imprisonment_years: float,
    detention_months: float,
    is_first_time_offender: bool = True,
    is_death_or_life_offence: bool = False,
    has_multiple_pending_cases: bool = False,
    delay_caused_by_accused_months: float = 0.0,
    court_ordered_continued_detention: bool = False,
    court_order_reasons: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Evaluates statutory eligibility for undertrial bail review under BNSS Section 479
    (successor to CrPC Section 436A), implementing statutory thresholds, provisos,
    explanations, and exclusions.

    Statutory Logic & Provisos under BNSS §479:
      - 1st Proviso (§479(1)): A first-time offender (never convicted previously) is eligible for
        bail review on bond after undergoing detention for 1/3rd (one-third) of the maximum period.
      - General Rule (§479(1)): Other undertrial prisoners are eligible for bail review
        after undergoing detention for 1/2 (one-half) of the maximum imprisonment period.
      - Delay Exclusion (Explanation to §479(1)): Period of detention passed due to delay in
        proceedings caused by the accused is strictly excluded from the computation.
      - Full-Maximum-Period Cap (Proviso to §479(1)): No undertrial can be detained during
        investigation, inquiry, or trial for longer than the full maximum sentence period.
      - Judicial Discretion (Second Proviso to §479(1)): The Court may, after hearing the
        Public Prosecutor and for reasons recorded in writing, order continued detention.
      - 2nd Proviso Exclusion (§479(1)): Does NOT apply to offences punishable by death or life imprisonment.
      - Sub-section (2) Bar (§479(2)): Release on bail under this section is prohibited if multiple
        cases or offences are pending investigation, inquiry, or trial against the accused.
      - Jail Superintendent Duty (§479(3)): The Superintendent of Jail is statutorily mandated
        to apply to the Court for bail review upon completion of the applicable period.
      - Important Legal Caveat: Output signifies statutory eligibility for judicial review on
        bond/sureties, not automatic extrajudicial release.
    """
    max_months = offence_max_imprisonment_years * 12.0
    effective_detention = max(0.0, detention_months - delay_caused_by_accused_months)

    # 1. Check Exclusion: Death or Life Imprisonment (BNSS §479(1) parenthetical exclusion)
    if is_death_or_life_offence:
        return {
            "eligible_for_review": False,
            "statutory_basis": "BNSS §479(1) (Exclusion for Capital / Life Imprisonment Offences)",
            "reason": "Statutory exclusion: Section 479 does not apply to offences punishable by death or life imprisonment.",
            "threshold_fraction": None,
            "threshold_months": None,
            "detention_months": detention_months,
            "effective_detention_months": effective_detention,
            "delay_excluded_months": delay_caused_by_accused_months,
            "jail_superintendent_duty_triggered": False,
            "exclusions_triggered": ["death_or_life_imprisonment_exclusion"],
        }

    # 2. Check Bar: Multiple Pending Cases (BNSS §479(2))
    if has_multiple_pending_cases:
        return {
            "eligible_for_review": False,
            "statutory_basis": "BNSS §479(2) (Multiple Pending Cases Bar)",
            "reason": "Statutory exclusion: BNSS §479(2) bars release under this section if an investigation, inquiry, or trial in more than one offence or in multiple cases is pending against the accused.",
            "threshold_fraction": None,
            "threshold_months": None,
            "detention_months": detention_months,
            "effective_detention_months": effective_detention,
            "delay_excluded_months": delay_caused_by_accused_months,
            "jail_superintendent_duty_triggered": False,
            "exclusions_triggered": ["multiple_pending_cases_exclusion"],
        }

    # 3. Check Maximum Period Ceiling (Absolute Statutory Bar on Detention Beyond Max Sentence)
    if effective_detention >= max_months:
        return {
            "eligible_for_review": True,
            "statutory_basis": "BNSS §479(1) (Proviso: Maximum Period Detention Bar)",
            "offence_max_imprisonment_years": offence_max_imprisonment_years,
            "detention_months": detention_months,
            "effective_detention_months": effective_detention,
            "delay_excluded_months": delay_caused_by_accused_months,
            "is_first_time_offender": is_first_time_offender,
            "threshold_fraction": "full-maximum (100%)",
            "threshold_months": round(max_months, 2),
            "reason": (
                f"Statutory detention ceiling reached: Effective detention ({effective_detention:.1f} months) "
                f"meets or exceeds the maximum statutory sentence ({max_months:.1f} months). Under BNSS §479(1) proviso, "
                f"no accused person may be detained during investigation or trial beyond the maximum period."
            ),
            "judicial_discretion_caveat": "Mandatory judicial review: Detention beyond maximum punishment is prohibited by statute.",
            "jail_superintendent_duty_triggered": True,
            "exclusions_triggered": [],
        }

    # 4. Check Judicial Continuation Order (BNSS §479(1) Second Proviso)
    if court_ordered_continued_detention:
        reasons_text = court_order_reasons or "Court recorded written reasons after hearing Public Prosecutor"
        return {
            "eligible_for_review": False,
            "statutory_basis": "BNSS §479(1) (Second Proviso: Judicial Continued Detention)",
            "reason": f"Detention continued by judicial order under BNSS §479(1) Second Proviso: {reasons_text}.",
            "threshold_fraction": None,
            "threshold_months": None,
            "detention_months": detention_months,
            "effective_detention_months": effective_detention,
            "delay_excluded_months": delay_caused_by_accused_months,
            "jail_superintendent_duty_triggered": False,
            "exclusions_triggered": ["judicial_continuation_order"],
        }

    # 5. Determine Applicable Threshold (First-time offender 1/3rd vs General 1/2)
    threshold_fraction = 1.0 / 3.0 if is_first_time_offender else 0.5
    fraction_label = "one-third (1/3rd)" if is_first_time_offender else "one-half (1/2)"
    threshold_months = max_months * threshold_fraction

    eligible = effective_detention >= threshold_months

    if eligible:
        relief_type = "bond" if is_first_time_offender else "bail"
        reason = (
            f"Eligible for statutory bail review on {relief_type} under BNSS §479 ({fraction_label} rule). "
            f"Effective detention is {effective_detention:.1f} months (gross {detention_months:.1f} mo less {delay_caused_by_accused_months:.1f} mo accused delay), "
            f"reaching the statutory threshold of {threshold_months:.1f} months ({fraction_label} of {offence_max_imprisonment_years:.1f} years maximum sentence)."
        )
    else:
        shortfall = threshold_months - effective_detention
        reason = (
            f"Not yet eligible for BNSS §479 review ({fraction_label} rule). "
            f"Effective detention is {effective_detention:.1f} months (gross {detention_months:.1f} mo less {delay_caused_by_accused_months:.1f} mo accused delay); "
            f"statutory requirement is {threshold_months:.1f} months. Shortfall: {shortfall:.1f} months."
        )

    return {
        "eligible_for_review": eligible,
        "statutory_basis": "BNSS §479(1) (First Proviso - First-Time Offender)" if is_first_time_offender else "BNSS §479(1) (General Provision)",
        "offence_max_imprisonment_years": offence_max_imprisonment_years,
        "detention_months": detention_months,
        "effective_detention_months": effective_detention,
        "delay_excluded_months": delay_caused_by_accused_months,
        "is_first_time_offender": is_first_time_offender,
        "threshold_fraction": fraction_label,
        "threshold_months": round(threshold_months, 2),
        "reason": reason,
        "judicial_discretion_caveat": (
            "Relief constitutes statutory eligibility for judicial consideration on personal bond/sureties; "
            "the Court may order continued detention after hearing the Public Prosecutor with written reasons."
        ),
        "jail_superintendent_duty_triggered": eligible,
        "exclusions_triggered": [],
    }
