# JanSetu AI — Quantitative Evaluation Results & Benchmark Protocol

This document establishes the verified experimental methodology, dataset specifications, baselines, and exact quantitative evaluation metrics for JanSetu AI across its 3 primary sovereign verticals: **Public Governance**, **Court Judgments (India)**, and **Statutory Law & Concordance**.

---

## 1. Evaluation Protocol & Ground-Truth Annotation

- **Curated Corpus:** Ingested over the 7 sovereign benchmark documents:
  1. `PM_KISAN_Guidelines` (Central Welfare Scheme Operational Guidelines 2024, Ministry of Agriculture)
  2. `Ayushman_Bharat_PMJAY` (National Health Assurance Policy Guidelines, National Health Authority)
  3. `SC_Bail_Judgment_Exemplar` (Synthetic judicial bail exemplar modeled on *Manish Sisodia v. ED* [2024 INSC 595] and *Satender Kumar Antil* [2022])
  4. `Tamil_Land_Sale_Deed` (Bilingual Tamil Nadu registered sale deed & Patta exemplar)
  5. `Cyber_Fraud_Zero_FIR` (I4C / MHA Helpline 1930 & BNSS §173 Standard Operating Procedure)
  6. `Model_Tenancy_Act_Guidelines` (MoHUA Model Tenancy Act 2021: Section 11 deposit cap, statutory 24-hr advance notice rule)
  7. `Senior_Citizens_Act_2007` (MWPSC Act 2007: Section 23 conditional gift revocation with *Sudesh Chhikara [2022]* condition caveats)
- **Question Set Structure:**
  - **$N = 120$ Answerable Queries:** 40 Governance, 40 Statutory Law & Citizen Rights, 40 Judicial Precedents & Bail.
  - **$N = 30$ Unanswerable / Out-of-Scope Queries:** 10 per vertical, testing ungrounded hallucination refusal.
  - **Split Separation:** The 30 unanswerable queries form a separate held-out test split. The empirical similarity threshold ($\tau = 0.40$ cloud, $\tau = 0.38$ on-prem) was tuned on a distinct development split of 20 queries (`eval/gold/dev_tuning_split.jsonl`) not present in the test set.
- **Annotation Methodology:** Gold answers, target statutory clauses, and acceptable chunk spans were annotated by two independent legal and public administration researchers at Kalasalingam Academy of Research and Education. Discrepancies were resolved through consensus, yielding an inter-annotator agreement score of **Cohen's $\kappa = 0.83$** (protocol documented in `eval/annotation_protocol.md`).
- **Per-Query Data:** Raw query-level outcomes are preserved in `eval/results/per_query_evaluation_results.csv` and questions in `eval/gold/sovereign_benchmark_qa.jsonl`.

---

## 2. Experimental Hardware & Execution Modes

| Operational Dimension | Standard Cloud Mode | Sovereign On-Premise Mode (`--profile onprem`) |
|---|---|---|
| **LLM Reasoning** | Cloudflare Workers AI (`@cf/meta/llama-3-8b-instruct`) | Local Ollama (`qwen2.5:7b-instruct`, 4-bit quantized) |
| **Embeddings** | Nomic Atlas API (`nomic-embed-text-v1.5`, 768-dim) | Local Ollama (`nomic-embed-text`, 768-dim normalized) |
| **Hardware** | Serverless Cloud Infrastructure | Local Edge Workstation: AMD Ryzen 7 5700X (8 cores / 16 threads), 32 GB DDR4 RAM, NVIDIA GeForce RTX 3060 (12 GB VRAM) |
| **Data Flow** | External API endpoints | Strictly air-gapped within local host boundary |

---

## 3. Comparative Retrieval & QA Evaluation

All proportions report exact counts $k/N$ and 95% Wilson score confidence intervals. Entailment scores report bootstrap mean $\pm$ standard error.

| Evaluation Metric | Naive RAG Baseline | Advanced GraphRAG | JanSetu AI Grounded (Cloud Mode)* | JanSetu AI Sovereign (On-Premise) | Metric Context & Protocol |
|---|---|---|---|---|---|
| **Top-5 Context Recall** | 85/120 (**70.8%**)<br>[62.2%, 78.2%] | 102/120 (**85.0%**)<br>[77.5%, 90.3%] | 111/120 (**92.5%**)<br>[86.4%, 96.0%] | 106/120 (**88.3%**)<br>[81.4%, 92.9%] | Ground-truth statutory clause or welfare criterion present in top-5 candidate chunks ($N = 120$). |
| **Calibrated Refusal Accuracy** | 12/30 (**40.0%**)<br>[24.6%, 57.7%] | 19/30 (**63.3%**)<br>[45.5%, 78.1%] | 28/30 (**93.3%**)<br>[78.7%, 98.2%] | 27/30 (**90.0%**)<br>[74.4%, 96.5%] | Correctly triggers refusal on $N = 30$ held-out unanswerable queries ($\tau = 0.40$ cloud, $\tau = 0.38$ on-prem). |
| **Citation Entailment (NLI)** | 0.52 ± 0.06 | 0.69 ± 0.05 | **0.88 ± 0.03** | **0.84 ± 0.04** | Mean claim-level entailment scored via `cross-encoder/nli-deberta-v3-small` across 111 grounded responses. |
| **Semantic Cache Hit (p95)** | N/A | N/A | **3.8 ms** | **3.8 ms** | In-memory SQLite cosine similarity hit ($\ge 0.95$). |
| **Single-Pass Vector Search (p95)**| 450 ms | 720 ms | **680 ms** | **740 ms** | FAISS Flat inner-product search over 768-dim continuous space. |
| **Hybrid + HyDE Latency (p95)** | N/A | 1,850 ms | **1,620 ms** | **2,100 ms** | HyDE generation + Vector + NetworkX graph traversal with RRF. |
| **End-to-End Latency (p95)** | 850 ms | 1,750 ms | **2,150 ms** | **2,850 ms** | Complete pipeline: Retrieval + Cross-Encoder + NLI verification + LLM generation. |

*\*Note: Cloud-mode benchmark figures were measured with Cloudflare Workers AI (`@cf/meta/llama-3-8b-instruct`); the Groq LPU tier was not evaluated in this quantitative benchmark table.*

### Baseline Implementation Specifications:
1. **Naive RAG Baseline:** Fixed 500-token chunking (50 overlap), single FAISS flat cosine search, top-5 chunks concatenated directly into LLM prompt without HyDE, graph traversal, reranking, or calibrated abstention threshold.
2. **Advanced GraphRAG:** Vector + NetworkX graph entity traversal with Reciprocal Rank Fusion (RRF), top-5 candidate chunks, without calibrated per-vertical refusal or cross-encoder NLI claim verification.

---

## 4. Software & Functional Integration Test Suite (Pass/Fail)

| Test Suite / Fixture | Verified Result | Scope & Deterministic Coverage |
|---|---|---|
| **Live Backend E2E Suite** | **16/16 PASS (100.0%)** | Validates Health, Concordance API, 1-Click Ingestion, Document Chunks, Governance RAG, Judgment RAG, Calibrated Abstention, KG Topology, Active Learning, Magic-Byte File Validation, Prompt Injection Quarantine, HTML/MD Export. |
| **Chromium Headless UI Suite** | **7/7 PASS (100.0%)** | Automated browser verification: Landing, Auth, Concordance Modal, Document Vault, Analytics KG, Multi-Vertical, History. |
| **Undertrial Rule Engine Test (BNSS §479)** | **8/8 PASS (100.0%)** | Validates 1/3rd first offender on bond, 1/2 repeat offender on bail, life/death exclusion, multiple pending cases bar (§479(2)), accused delay deduction, full-maximum cap, judicial continued detention, and jail superintendent application duty (§479(3)) in `eval/test_undertrial_rules.py`. |
| **Statutory Concordance Fixture**| **30/30 PASS (100.0%)** | Deterministic lookup on 30 standard transitions (`IPC ⇄ BNS`, `CrPC ⇄ BNSS`, `IEA ⇄ BSA`). |
| **Adversarial Injection Fixture** | **10/10 PASS (100.0%)** | Quarantines 10 synthetic jailbreak/steganography chunks before vector indexing. |
| **Cryptographic Merkle Provenance Test** | **PASS (100.0%)** | Validates SHA-256 Merkle tree calculation, chained audit blocks, single-byte modification tamper detection (`TAMPERING_DETECTED`), and authentic verification (`TAMPER_EVIDENT_VERIFIED`). |
| **5-Layer Sovereign Guardrails** | **PASS (100.0%)** | Validates Aadhaar-like number redaction (`XXXX-XXXX-1234`), PAN masking (`XXXXX1234X`), phone number redaction, and anti-forgery request rejection (100% precision/recall on 25-sample unit fixture, not a general population estimate). |

---

## 5. Indic Multilingual Benchmark & Calibrated Abstention Case Study

Evaluated live on AWS EC2 (`http://ec2-98-93-55-8.compute-1.amazonaws.com:3000`) using the Tamil Nadu registered sale deed (*கிரையப் பத்திரம்*) and Patta exemplar:

| Dimension | Tamil Indic Query (`ta`) | Cross-Lingual English Query (`en`) |
|---|---|---|
| **Input Query** | `தமிழில் விடை: சொத்து யாருக்கு விற்கப்பட்டது மற்றும் கிரையத் தொகை எவ்வளவு?` | `"What is the total cost of the land and who are the buyer and seller?"` |
| **Retrieved Chunks** | 9 evidence chunks (100% corpus coverage) | 5 candidate chunks (Vendor/Purchaser details) |
| **Extracted Consideration**| **₹45,00,000/- (ரூபாய் நாற்பத்தைந்து லட்சம் மட்டும்)** | **Calibrated Abstention Refusal** |
| **Payment Instrument** | SBI Cheque No. 489102 | Refusal explanation: *"Text chunks contain parties and property details but do NOT contain monetary amount of sale price."* |
| **Seller / Vendor** | K. Ramaswami (திரு. கே. ராமசுவாமி) | Mr. K. Ramaswami |
| **Buyer / Purchaser** | M. Meenakshi (திருமதி. எம். மீனாட்சி) | Mrs. M. Meenakshi |
| **Property Spec** | Survey 142/3A, Patta 874, Chitlapakkam Village | Survey 142/3A, Sub-division 3A2, Patta 874 |
| **Statutory Citations** | Tamil Nadu Stamp Act 1899 (Clause 6, Clause 3/4) | Clause 2 & 3 (Vendor & Purchaser Details) |
| **Calibrated Abstention Behavior** | Verbatim grounding from Clause 6 | **Refused to guess monetary amount** when Clause 6 was omitted from candidate context window. |


*Evaluation Build & Model Specification:*
- Similarity threshold ($\tau = 0.40$ cloud, $\tau = 0.38$ on-prem) was tuned on a separate 20-query dev split, completely held out from the 30 unanswerable test queries.
- Cloud mode utilizes Cloudflare Workers AI (`@cf/meta/llama-3-8b-instruct`) + Nomic Atlas API + DeBERTa-v3 Small cross-encoder NLI. Groq LPU operates as an external cloud acceleration tier (`qwen/qwen3-32b`, `openai/gpt-oss-120b`).
- Sovereign on-premise mode runs locally via Ollama (`qwen2.5:7b-instruct` 4-bit) + local Ollama `nomic-embed-text` on AMD Ryzen 7 5700X + RTX 3060 12GB edge workstation.
- Provenance ledger is an internal SHA-256 Merkle tree and chained audit log (not an implementation of national blockchain platforms; future work: anchoring roots on permissioned ledgers such as NBFLite).
