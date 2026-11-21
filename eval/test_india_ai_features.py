"""
India AI Fellowship Features Verification Suite:
1. Indian Criminal Law Statutory Concordance Engine (IPC <-> BNS, CrPC <-> BNSS, IEA <-> BSA).
2. Governance & Public Policy Vertical Indexer (Welfare Schemes & Gazettes).
3. Governance RAG Pipeline Factory Wiring.
"""
from __future__ import annotations

import os
import sys

# Ensure backend is on PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from app.core.statutory_concordance import (
    find_statutory_matches,
    enrich_answer_with_concordance,
    IPC_TO_BNS,
    CRPC_TO_BNSS,
    IEA_TO_BSA,
)
from app.indexers.governance import GovernanceIndexer
from app.core.factory import build_pipeline


def test_statutory_concordance():
    print("\n--- 1. Testing Indian Statutory Concordance Engine ---")

    # Test 1: IPC Section 420 -> BNS 318(4)
    query_1 = "The accused was charged under Section 420 IPC for dishonestly inducing transfer of funds."
    matches_1 = find_statutory_matches(query_1)
    assert len(matches_1) > 0, "Failed to match IPC 420"
    m = matches_1[0]
    assert m.source_section == "420"
    assert "318" in m.target_section
    print(f"  [PASS] IPC §420 correctly mapped to BNS §{m.target_section} ({m.title}).")

    # Test 2: IPC Section 302 -> BNS 103(1)
    query_2 = "FIR registered under IPC 302 and IPC 307 for assault."
    matches_2 = find_statutory_matches(query_2)
    secs = {m.source_section: m.target_section for m in matches_2}
    assert "302" in secs and "103(1)" in secs["302"]
    assert "307" in secs and "109" in secs["307"]
    print(f"  [PASS] Multi-charge IPC query mapped: {secs}.")

    # Test 3: CrPC Section 439 -> BNSS 483 (Bail)
    query_3 = "Bail application filed under Section 439 CrPC before the High Court."
    matches_3 = find_statutory_matches(query_3)
    assert len(matches_3) > 0, "Failed to match CrPC 439"
    assert "483" in matches_3[0].target_section
    print(f"  [PASS] CrPC §439 mapped to BNSS §{matches_3[0].target_section} (Regular Bail).")

    # Test 4: Evidence Act Section 65B -> BSA 63
    query_4 = "Call detail records submitted without Section 65B Evidence Act certificate."
    matches_4 = find_statutory_matches(query_4)
    assert len(matches_4) > 0, "Failed to match IEA 65B"
    assert "63" in matches_4[0].target_section
    print(f"  [PASS] IEA §65B mapped to BSA §{matches_4[0].target_section} (Digital Certificate).")

    # Test 5: Enrichment formatting
    enriched = enrich_answer_with_concordance("Sample judicial holding text.", matches_1)
    assert "Indian Criminal Law Statutory Concordance" in enriched
    assert "BNS" in enriched
    print("  [PASS] Judicial holding answer enrichment verified.")


def test_governance_indexer():
    print("\n--- 2. Testing Governance & Welfare Scheme Indexer ---")

    scheme_sample = """
    GOVERNMENT OF INDIA
    MINISTRY OF AGRICULTURE & FARMERS WELFARE
    Notification No. G.S.R. 412(E)

    Operational Guidelines for Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)

    1. Eligibility Criteria:
    All landholder farmer families who have cultivable landholding in their names as per state land records
    are eligible for financial assistance under this scheme (subject to exclusion criteria). The beneficiary must have an Aadhaar-linked bank account.

    2. Exclusion Criteria:
    The following categories are not eligible:
    (a) All Institutional Landholders.
    (b) Former and present holders of constitutional posts.
    (c) All persons who paid Income Tax in last assessment year.

    3. Benefits Provided:
    Financial benefit of Rs. 6000/- per year per family payable in three equal four-monthly installments 
    of Rs. 2000/- each through Direct Benefit Transfer (DBT) directly into bank accounts.

    4. Documents Required:
    (a) Aadhaar Card.
    (b) Record of Land Ownership (Khatauni / Patta / 7-12 extract).
    (c) Bank Account Passbook copy.

    5. How to Apply:
    Eligible farmers can apply online at pmkisan.gov.in or through local Common Service Centres (CSCs) 
    or submit physical forms to Village Revenue Officer / Gram Panchayat.
    """

    indexer = GovernanceIndexer(target_chunk_size=350, overlap=30)
    chunks = indexer.chunk(scheme_sample, metadata={"doc_id": "pm_kisan_01", "page": 1, "tenant_id": "gov_india"})

    assert len(chunks) >= 3, f"Expected at least 3 chunks, got {len(chunks)}"

    facets = [c["facet"] for c in chunks]
    print(f"  [PASS] Extracted {len(chunks)} governance facet chunks: {set(facets)}")

    # Check scheme name & Gazette extraction
    assert any("PM-KISAN" in (c.get("scheme_name") or "") for c in chunks), "Scheme name detection failed"
    assert any("G.S.R." in (c.get("gazette_ref") or "") for c in chunks), "Gazette ref detection failed"
    print("  [PASS] Automatic extraction of Scheme Name ('PM-KISAN') and Gazette Ref ('G.S.R. 412(E)') verified.")


def test_pipeline_factory():
    print("\n--- 3. Testing Pipeline Factory for Governance & Judgment Verticals ---")

    class MockLLM:
        pass

    pipeline_gov = build_pipeline("governance", MockLLM(), None)
    assert pipeline_gov.config["vertical"] == "governance"
    assert pipeline_gov.indexer.__class__.__name__ == "GovernanceIndexer"
    assert pipeline_gov.generator.__class__.__name__ == "GovernanceGenerator"
    print("  [PASS] 'governance' vertical successfully assembled in RAGPipeline.")

    pipeline_judg = build_pipeline("judgment", MockLLM(), None)
    assert pipeline_judg.config["vertical"] == "judgment"
    assert pipeline_judg.indexer.__class__.__name__ == "JudgmentIndexer"
    assert pipeline_judg.generator.__class__.__name__ == "JudgmentGenerator"
    print("  [PASS] 'judgment' vertical successfully assembled in RAGPipeline.")


def main():
    print("=" * 65)
    print("DocsAI India AI Fellowship Features Verification Suite")
    print("=" * 65)
    test_statutory_concordance()
    test_governance_indexer()
    test_pipeline_factory()
    print("\n" + "=" * 65)
    print("ALL INDIA AI FELLOWSHIP FEATURES VERIFIED SUCCESSFULLY!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
