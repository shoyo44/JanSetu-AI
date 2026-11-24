# JanSetu AI — Evaluation Framework & Benchmark Specification

This document establishes the evaluation methodology, dataset specifications, and deterministic test suite results for JanSetu AI across its 3 primary sovereign verticals: **Public Governance**, **Court Judgments (India)**, and **Statutory Law & Concordance**.

---

## 1. Sovereign Benchmark Dataset Specifications

The repository provides a standardized 150-query multilingual gold evaluation dataset committed at [`eval/gold/sovereign_benchmark_qa.jsonl`](./gold/sovereign_benchmark_qa.jsonl) curated over 7 sovereign benchmark documents:
1. `PM_KISAN_Guidelines` (Central Welfare Scheme Operational Guidelines 2024, Ministry of Agriculture)
2. `Ayushman_Bharat_PMJAY` (National Health Assurance Policy Guidelines, National Health Authority)
3. `SC_Bail_Judgment_Exemplar` (Judicial bail exemplar modeled on *Manish Sisodia v. ED* [2024 INSC 595] and *Satender Kumar Antil* [2022])
4. `Tamil_Land_Sale_Deed` (Bilingual Tamil Nadu registered sale deed & Patta exemplar)
5. `Cyber_Fraud_Zero_FIR` (I4C / MHA Helpline 1930 & BNSS §173 Standard Operating Procedure)
6. `Model_Tenancy_Act_Guidelines` (MoHUA Model Tenancy Act 2021: Section 11 deposit cap, statutory 24-hr advance notice rule)
7. `Senior_Citizens_Act_2007` (MWPSC Act 2007: Section 23 conditional gift revocation with *Sudesh Chhikara [2022]* condition caveats)

### Dataset Composition:
- **$N = 120$ Answerable Queries:** Grounded in official statutory clauses and guidelines:
  - 40 Public Governance & Welfare Schemes (PM-KISAN, Ayushman Bharat, Senior Citizens)
  - 40 Statutory Law & Citizen Rights (Cyber FIR, Model Tenancy Act, Tamil Land Deeds)
  - 40 Judicial Precedents & Bail Reforms (Supreme Court bail ruling, Statutory Concordance)
- **$N = 30$ Held-Out Unanswerable Queries:** 10 per vertical, testing safe abstention on out-of-scope, foreign, or adversarial queries without hallucinating.
- **Multilingual Coverage:** 103 queries in English, 39 queries in Hindi (हिन्दी), and 8 queries in Tamil (தமிழ்).
- **Split Separation:** The 30 unanswerable queries form an isolated held-out split. The similarity threshold ($\tau = 0.40$ cloud, $\tau = 0.38$ on-prem) was tuned on a separate 20-query development split (`eval/gold/dev_tuning_split.jsonl`).

---

## 2. Experimental Execution Modes & Architecture

| Operational Dimension | Standard Cloud Mode | Sovereign On-Premise Mode (`--profile onprem`) |
|---|---|---|
| **LLM Reasoning** | Cloudflare Workers AI (`@cf/meta/llama-3-8b-instruct`) | Local Ollama (`qwen2.5:7b-instruct`, 4-bit quantized) |
| **Embeddings** | Nomic Atlas API (`nomic-embed-text-v1.5`, 768-dim) | Local Ollama (`nomic-embed-text`, 768-dim normalized) |
| **Hardware** | Serverless Cloud Infrastructure | Local Edge Workstation: AMD Ryzen 7 5700X, 32 GB RAM, NVIDIA GeForce RTX 3060 (12 GB VRAM) |
| **Data Flow** | External API endpoints | Strictly air-gapped within local host boundary |

---

## 3. Comparative Evaluation Harness

The comparative evaluation runner is implemented in [`eval/run.py`](./run.py). It evaluates query outputs against ground truth across 4 architectural paradigms:
1. **Naive RAG Baseline:** Fixed chunking, single FAISS Flat search, top-5 chunks concatenated into prompt, without graph traversal, reranking, or calibrated abstention.
2. **Advanced GraphRAG:** Vector + NetworkX graph entity traversal with Reciprocal Rank Fusion (RRF), top-5 chunks.
3. **JanSetu AI Sovereign (On-Premise):** Local embeddings + FAISS + NetworkX graph traversal + calibrated abstention ($\tau = 0.38$) + local NLI claim verification.
4. **JanSetu AI Grounded (Cloud Mode):** Nomic Atlas embeddings + FAISS + NetworkX + RRF + calibrated abstention ($\tau = 0.40$) + DeBERTa-v3 cross-encoder NLI claim verification.

*(Note: Prior simulated benchmark figures have been removed. Empirical pipeline benchmark results across all 4 configurations are being recorded via live execution for contribution to the national AIKosh portal as part of the IndiaAI Fellowship research deliverables).*

---

## 4. Software & Functional Integration Test Suite (Pass/Fail)

All functional, security, and rule-based components are validated by deterministic automated test suites:

| Test Suite / Fixture | Verified Result | Scope & Deterministic Coverage |
|---|---|---|
| **Live Backend E2E Suite** | **16/16 PASS (100.0%)** | Validates Health, Concordance API, 1-Click Ingestion, Document Chunks, Governance RAG, Judgment RAG, Calibrated Abstention, KG Topology, Active Learning, Magic-Byte File Validation, Prompt Injection Quarantine, HTML/MD Export. |
| **Chromium Headless UI Suite** | **7/7 PASS (100.0%)** | Automated browser verification: Landing, Auth, Concordance Modal, Document Vault, Analytics KG, Multi-Vertical, History. |
| **Undertrial Rule Engine Test (BNSS §479)** | **8/8 PASS (100.0%)** | Validates 1/3rd first offender on bond, 1/2 repeat offender on bail, life/death exclusion, multiple pending cases bar (§479(2)), accused delay deduction, full-maximum cap, judicial continued detention, and jail superintendent application duty (§479(3)) in `eval/test_undertrial_rules.py`. |
| **Statutory Concordance Fixture** | **30/30 PASS (100.0%)** | Deterministic lookup on 30 standard transitions (`IPC ⇄ BNS`, `CrPC ⇄ BNSS`, `IEA ⇄ BSA`). |
| **Adversarial Injection Fixture** | **10/10 PASS (100.0%)** | Quarantines 10 synthetic jailbreak/steganography chunks before vector indexing. |
| **Cryptographic Merkle Provenance Test** | **PASS (100.0%)** | Validates SHA-256 Merkle tree calculation, chained audit blocks, single-byte modification tamper detection (`TAMPERING_DETECTED`), and authentic verification (`TAMPER_EVIDENT_VERIFIED`). |
| **5-Layer Sovereign Guardrails** | **PASS (100.0%)** | Validates Aadhaar-like number redaction (`XXXX-XXXX-1234`), PAN masking (`XXXXX1234X`), phone number redaction, and anti-forgery request rejection (100% precision/recall on 25-sample unit fixture). |
