# JanSetu AI — System Facts & Single Source of Truth (SSOT)

This document establishes the verified, definitive technical and factual parameters of JanSetu AI (जनसेतु). All project documentation (README, Fellowship Proposal, Academic Report, and Synopsis) must align strictly with this document.

---

## 1. Identity & Application Scope
- **Project Name:** JanSetu AI (जनसेतु) — Sovereign Multi-Vertical Agentic Knowledge Graph & RAG Platform for Public Governance and Citizen Welfare
- **Author / Applicant:** Dhanush S
- **Target Fellowship:** IndiaAI Mission Fellowship (Graduate / Research Scholar)
- **Primary Domain:** Governance
- **Cross-Cutting Domain:** Law & Justice
- **Repository:** https://github.com/shoyo44/JanSetu-AI
- **License:** MIT

---

## 2. Technical Foundation

| Parameter | Verified Specification | Notes |
|---|---|---|
| **Backend Framework** | FastAPI (Python 3.11+) | Async ASGI REST & WebSocket gateway |
| **Frontend Framework** | React 18 + Vite | Modular UI, ForceGraph2D visualizer |
| **Graph Database** | In-process NetworkX directed graph | Thread-safe with async `RWLock`, persisted to `graph_store.json`. Suited for up to 50,000 nodes; HNSW + DuckDB migration on roadmap for 250,000+ nodes. |
| **Vector Index** | In-process FAISS Flat Index (`IndexFlatIP`) | Normalized inner product (cosine similarity) |
| **Primary Embedding Model** | `nomic-embed-text-v1.5` (Cloud API / Local Ollama) | Strictly **768 dimensions** (normalized). Cloud mode uses Nomic Atlas API; on-premise mode uses local Ollama `nomic-embed-text`. |
| **Embedding Consistency** | **Vectors across models are incommensurable** | Switching between cloud (`nomic-embed-text-v1.5`) and local models requires a complete corpus re-index. Hash router in `embedding_router.py` is strictly an offline unit-test mock fixture, not semantic search. |
| **Abstention Calibration** | Per-vertical similarity threshold ($\tau = 0.40$) | Calibrated specifically for normalized `nomic-embed-text-v1.5` cosine similarities on a 20-query dev split. Recalibration ($\tau = 0.38$) on local models. |
| **Indic Language Support** | Zero-dependency Unicode script detector | Covers 10 Indic scripts: Devanagari (Hindi/Marathi), Tamil, Telugu, Bengali, Punjabi, Gujarati, Odia, Kannada, Malayalam, Urdu. |
| **Voice Interface** | Browser Web Speech API (Client-assisted) | Convenience feature in desktop/cloud mode; delegates audio to browser vendor cloud (e.g., Google Chrome speech service). For air-gapped on-premise mode, voice input must be disabled or replaced by local on-device models (e.g., Whisper.cpp / AI4Bharat IndicConformer, planned Q3). |
| **Supported File Formats** | PDF, DOCX, TXT | Binary magic-byte verified (`%PDF-`, `PK\x03\x04`, UTF-8). Blocks PE/ELF executables and double extensions. Max size: 50 MB. |

---

## 3. Sovereign Multi-Vertical Matrix (IndiaAI Fellowship Core)

JanSetu AI configures 3 primary sovereign fellowship verticals in `backend/app/config/verticals.py` (with transparent backward-compatibility aliases for legacy requests):

| Primary Vertical Key | Display Name | Chunking (Tokens/Overlap) | Retrieval Modality | Reranker Mechanism | Specialized IndiaAI Feature |
|---|---|---|---|---|---|
| `governance` | Governance & Welfare | 500 / 100 | Hybrid (Vector + Graph) | Lexical & Facet Boost | Citizen *Jan Suvidha* plain-language summary, DBT subsidy mapping, eligibility vs exclusion separation. |
| `judgment` | Court Judgments (India) | 500 / 100 | Hybrid (Vector + Graph) | Statutory Citation Boost | Binding *Ratio Decidendi* extraction, bail precedent synthesis under BNSS §483 / §479, Article 21 liberty safeguards. |
| `law` | Statutory Law & Concordance | 768 / 128 | Hybrid (Vector + Graph) | `VerticalReranker` (Domain-keyword boost) | Tri-code concordance (`IPC ⇄ BNS`, `CrPC ⇄ BNSS`, `IEA ⇄ BSA`), Regional Land Deeds (*கிரையப் பத்திரம்*), 10-point Red-Flag risk scanner. |

*Note: Legacy vertical aliases (`compliance` $\to$ `law`, `startup` $\to$ `law`, `university` $\to$ `governance`, `hr` $\to$ `governance`) are resolved automatically by the pipeline factory.*

---

## 3A. Preloaded Sovereign Benchmark Catalog (7 Bundled Scenarios & Provenance)

JanSetu AI provides a 1-click evaluation catalog in Document Vault (`/api/v1/benchmarks`):
1. `pm_kisan`: PM-KISAN Operational Guidelines 2024 (Governance & DBT Welfare). *Provenance: Ministry of Agriculture & Farmers Welfare, GoI (Official Gazette excerpt).* Evaluates cultivable landholder eligibility (noting the 2019 ceiling removal), "family" definition (husband, wife, minor children), pension exclusions ($\ge ₹10,000$), and mandatory e-KYC/land seeding.
2. `sc_judgment`: Synthetic Judicial Benchmark Exemplar (Law & Justice / BNSS §483 / CrPC §439). *Provenance: Authored benchmark exemplar modeled on Supreme Court bail jurisprudence in Manish Sisodia v. Directorate of Enforcement (2024 INSC 595, decided August 9, 2024) and Satender Kumar Antil v. CBI (2022) under Article 21 safeguards and the triple test.*
3. `ayushman_bharat`: Ayushman Bharat PM-JAY Policy Guidelines (Governance & Public Health). *Provenance: National Health Authority (NHA), GoI (Official Guidelines excerpt).* ₹5 Lakh cashless hospital cover guarantee and NHA 14555 grievance escalation.
4. `tamil_pattiram`: Tamil Nadu Land Sale Deed & Patta / *கிரையப் பத்திரம்* (Rural Land Administration). *Provenance: Standard Tamil Nadu Registration Department statutory bilingual deed format exemplar.* Bilingual parsing of Survey Number (`புல எண்`), 4 boundaries (`நான்கு எல்லைகள்`), consideration amount, and Nil-Encumbrance Certificate (`வில்லங்கச் சான்றிதழ்`).
5. `cyber_fir`: Cyber Fraud Reporting & Zero-FIR Guidelines / MHA Helpline 1930 (Citizen Rights). *Provenance: Indian Cyber Crime Coordination Centre (I4C), Ministry of Home Affairs (MHA) Standard Operating Procedure.* Golden Hour bank freezing via CFCFRMS, Zero-FIR registration under BNSS §173, and cyber cheating remedies under BNS §318(4) read with IT Act §66D.
6. `tenancy_act`: Model Tenancy Act Guidelines / 2-Month Deposit Cap (Urban Housing). *Provenance: Ministry of Housing and Urban Affairs (MoHUA), GoI legislative model framework.* MoHUA model framework capping residential security deposit at 2 months' rent (Section 11), statutory rule requiring at least 24 hours' prior written notice before landlord entry/inspection, and Rent Authority dispute mechanisms. *(Caveat: Model law subject to state enactment; Karnataka operates under Karnataka Rent Act, 1999).*
7. `senior_citizen`: Senior Citizens Parental Property Protection Act (MWPSC Act 2007 §23). *Provenance: Ministry of Social Justice and Empowerment statutory enactment.* Maintenance Tribunal procedure for declaring conditional property gifts void upon child neglect. *(Judicial caveat: Under SC ruling in Sudesh Chhikara (2022), maintenance obligation must be an express or integral condition of the transfer).*

---

## 4. Deployment Modes & Data Flow Boundary

JanSetu AI supports two distinct operational modes:

| Data Flow Pathway | Standard Cloud Mode | Sovereign On-Premise Mode (`--profile onprem`) |
|---|---|---|
| **LLM Reasoning** | Cloudflare Workers AI (`@cf/meta/llama-3-8b-instruct`) | Local Ollama daemon (`qwen2.5:7b-instruct` 4-bit quantized) |
| **Embeddings** | Nomic Atlas API (`nomic-embed-text-v1.5`, 768-dim) | Local Ollama daemon (`nomic-embed-text`, 768-dim normalized) |
| **OCR Cascade** | 5-Tier (PyMuPDF $\rightarrow$ Tesseract $\rightarrow$ AWS Textract $\rightarrow$ OCR.space $\rightarrow$ Cloudflare Vision) | 2-Tier strictly offline (Tier 1 PyMuPDF $\rightarrow$ Tier 2 PyTesseract OCR) |
| **Authentication** | Firebase Web SDK (Google OAuth) | Local Developer Session (`tenant_id` header / DevUser). Multi-user local auth, RBAC, and AES-256 store encryption scheduled on roadmap. |
| **Chat & Log Storage**| MongoDB Atlas (with local JSON DB failover) | Local JSON storage (`/backend/data/json_db/`) |
| **Voice Interface** | Browser Web Speech API (Client-assisted cloud STT) | Disabled or routed to local on-device Whisper model |
| **Edge Hardware Profile**| Serverless cloud | NVIDIA GeForce RTX 3060 (12 GB VRAM), AMD Ryzen 7 5700X (8 cores / 16 threads), 32 GB RAM |
| **Data Residency** | Global / Multi-region | **100% on-premise within host boundary**, supporting institutional data-residency compliance under Section 16 of DPDPA 2023 |

---

## 5. Legal Concordance Scope & Verified Caveats

1. **Statutory Coverage:**
   - Indian Penal Code (IPC, 1860) $\longleftrightarrow$ Bharatiya Nyaya Sanhita (BNS, 2023)
   - Code of Criminal Procedure (CrPC, 1973) $\longleftrightarrow$ Bharatiya Nagarik Suraksha Sanhita (BNSS, 2023)
   - Indian Evidence Act (IEA, 1872) $\longleftrightarrow$ Bharatiya Sakshya Adhiniyam (BSA, 2023)
   - Specific Citizen Provisions: CrPC §436A ⇄ BNSS §479 (Undertrial first-time offender 1/3rd detention release), BNSS §173 (Zero-FIR and mandatory e-FIR), BNS §318(4) (General cheating applied to cyber fraud, read with IT Act §66D).

2. **Crucial Legal Caveats:**
   - **IPC §124A (Sedition) $\rightarrow$ BNS §152:** Sedition was repealed in the 2023 code. BNS §152 is a distinct successor provision penalizing acts endangering sovereignty, unity, and integrity of India. It is indexed as a successor mapping, not a verbatim equivalent.
   - **Temporal Jurisdiction:** The new criminal codes apply prospectively to offences committed on or after **July 1, 2024**. Offences committed prior to this date remain governed by IPC, CrPC, and IEA pursuant to Section 358 BNS and Section 531 BNSS. The concordance engine is engineered as an analytical bridging aid during this decadal transition.
   - **Model Tenancy Act (MoHUA 2021):** A model legislative framework that requires state-level enactment (tenancy falls under State List Entry 18). State laws (such as Karnataka Rent Act 1999) govern unless the state repeals and enacts the model framework. Deposit caps fall under Section 11; entry/inspection requires at least 24 hours' prior written advance notice under the statutory rules.
   - **Senior Citizens Act §23:** Under the Supreme Court decision in *Sudesh Chhikara v. Ramti Devi (2022)*, Section 23 voidance requires the condition of providing maintenance to be an express or integral part of the transfer deed; unconditional gifts are not revokable solely due to subsequent neglect.
   - **PM-KISAN Definition & Exclusions:** "Family" is defined as husband, wife, and minor children. Adult children with separate land records in their own name are treated as distinct families. Pensioners with monthly pension $\ge ₹10,000$ (except Group D / MTS) are excluded.
   - **Legal Disclaimer:** JanSetu AI is an assistive reference and research platform, **not legal advice**. All statutory outputs must be verified against the official Gazette of India.

3. **Judicial Statistics Sources:**
   - Pending cases (4.4–5.1 crore): **National Judicial Data Grid (NJDG), 2024**.
   - Undertrial inmate population: **NCRB Prison Statistics India (PSI) 2021 (77.1%) and PSI 2022 (75.8%)**.

---

## 5B. Bilingual Indic Land Administration & Deed Verification Engine

JanSetu AI includes native support for regional Indian land records and registered sale deeds (*கிரையப் பத்திரம், பட்டா, சிட்டா*):
- Zero-dependency Indic Unicode character range detector (`0x0B80–0x0BFF` for Tamil script).
- Key covenant extraction: Survey Number (`புல எண்`), Sub-division (`உட்பிரிவு`), Extent (`பரப்பளவு`), Four Boundaries (`நான்கு எல்லைகள்`), Encumbrance Certificate status (`வில்லங்கச் சான்றிதழ்`), and Consideration Amount.
- Resilient JSON parser and token allocation for Indic scripts with regional citizen summaries (*Jan Suvidha*).
- *Cross-encoder note:* Claim entailment verification via `cross-encoder/nli-deberta-v3-small` is English-primary. Regional Indic texts are evaluated via citation span grounding and lexical verification, with native Indic NLI models (such as MuRIL / IndicBERT fine-tuned on IndicXNLI) planned for the Q2 fellowship milestone.

---

## 6. Official IndiaAI Mission Pillar Alignment

JanSetu AI aligns with 3 official pillars established by the Ministry of Electronics and Information Technology (MeitY):
1. **IndiaAI Application Development Initiative:** Deploying high-impact AI applications in Public Governance, Law & Justice, and Rural Land Administration.
2. **IndiaAI Datasets Platform:** Contributing our standardized, verified sovereign benchmark corpus and open-source evaluation pairs (`eval/gold/sovereign_benchmark_qa.jsonl`).
3. **Safe & Trusted AI:** Calibrated abstention engine ($\tau = 0.40$), claim-level NLI citation entailment, and pre-retrieval indirect prompt injection defense.

---

## 7. Verified Performance & Evaluation Metrics

To ensure mathematical consistency and avoid conflating software unit tests with statistical retrieval quality, JanSetu AI separates its evaluation into two distinct categories:

### A. Software & Functional Integration Test Suite (Pass/Fail)
Evaluated on our automated live test harness (`eval/test_live_e2e_full_system.py`, `eval/test_frontend_chromium.py`):

| Test Suite | Result | Scope / Coverage |
|---|---|---|
| **Live Backend E2E Test Suite** | **16/16 PASS (100.0%)** | Full-system validation: Health check, Concordance API, 1-Click Benchmark Ingestion, Ingested Document List, Chunk API, Governance RAG, Judgment RAG, Calibrated Abstention, Knowledge Graph Topology, Active Learning Feedback, Magic-Byte File Validation, Prompt Injection Quarantine, HTML/MD Audit Export. |
| **Playwright Chromium E2E Suite**| **7/7 PASS (100.0%)** | Automated headless Chrome testing: Landing, Auth, Concordance Modal, Document Vault, Analytics KG, Multi-Vertical Selection, and History. |
| **Frontend Production Build** | **PASS (463 ms)** | Clean Vite production build with zero warnings or errors. |
| **Statutory Concordance Fixture**| **30/30 PASS (100.0%)** | Deterministic unit verification on curated benchmark set of statutory transitions. |
| **Adversarial Injection Fixture** | **10/10 PASS (100.0%)** | Quarantines 10 synthetic jailbreak/steganography chunks before vector indexing. |

### B. Statistical Retrieval & QA Defensibility Evaluation
Evaluated over $N = 120$ annotated answerable query-document pairs spanning Central/State Gazettes (40), Statutory Enactments (40), and Appellate Rulings (40), alongside a separate held-out set of $N = 30$ unanswerable queries (10 per vertical). Gold answers were annotated by two independent researchers (Cohen's $\kappa = 0.88$). Raw results are tracked in `eval/results/per_query_evaluation_results.csv`.

All proportions report exact counts $k/N$ with 95% Wilson score confidence intervals. Entailment reports mean $\pm$ standard error.

| Evaluation Metric | Naive RAG Baseline | Advanced GraphRAG | JanSetu AI Grounded (Cloud Mode) | JanSetu AI Sovereign (On-Premise) | Metric Definition / Protocol |
|---|---|---|---|---|---|
| **Top-5 Context Recall** | 85/120 (**70.8%**)<br>[62.2%, 78.2%] | 102/120 (**85.0%**)<br>[77.5%, 90.3%] | 111/120 (**92.5%**)<br>[86.4%, 96.0%] | 106/120 (**88.3%**)<br>[81.4%, 92.9%] | Ground-truth statutory clause or welfare criterion present in top-5 retrieved chunks ($N=120$). |
| **Calibrated Refusal Accuracy** | 12/30 (**40.0%**)<br>[24.6%, 57.7%] | 19/30 (**63.3%**)<br>[45.5%, 78.1%] | 28/30 (**93.3%**)<br>[78.7%, 98.2%] | 27/30 (**90.0%**)<br>[74.4%, 96.5%] | Correctly abstains on $N=30$ held-out unanswerable queries ($\tau = 0.40$ cloud, $\tau = 0.38$ on-prem). |
| **Citation Entailment (NLI)** | 0.52 ± 0.06 | 0.69 ± 0.05 | **0.88 ± 0.03** | **0.84 ± 0.04** | Mean claim-level entailment score using `cross-encoder/nli-deberta-v3-small` across 111 grounded answers. |
| **Semantic Cache Hit Latency (p95)**| N/A | N/A | **3.8 ms** | **3.8 ms** | In-memory SQLite cosine similarity hit ($\ge 0.95$). |
| **Vector Search Latency (p95)** | 450 ms | 720 ms | **680 ms** | **740 ms** | Single-pass FAISS query over 768-dim space. |
| **Hybrid + HyDE Latency (p95)** | N/A | 1,850 ms | **1,620 ms** | **2,100 ms** | Vector + Graph retrieval + HyDE query expansion. |
| **End-to-End Synthesis Latency (p95)**| 850 ms | 1,750 ms | **2,150 ms** | **2,850 ms** | Complete pipeline: Retrieval + Cross-Encoder + NLI verification + LLM generation (measured on RTX 3060 edge rig for on-prem). |


---

## 8. Prior Art & Comparative Landscape

| Dimension | Jugalbandi (OpenNyAI / AI4Bharat) | NyayaReasoner | Falkor-IRAC / RAG–KG | LandLens / Commercial | JanSetu AI (Ours) |
|---|---|---|---|---|---|
| **Primary Target Users** | Citizens (Welfare schemes) | Legal advocates | Legal researchers | Land buyers (Tamil Nadu) | **Citizens, CSC operators, legal-aid counsels** |
| **Domain Scope** | Welfare schemes | SC judgment prediction | Case law, statutes | Land title due diligence | **Welfare + criminal transition + regional land deeds** |
| **Retrieval Modality** | Dense embeddings + FAISS | BM25 + dense + RRF | Graph / hybrid traversal | OCR + AI extraction | **Hybrid (Vector + Graph) + RRF + HyDE** |
| **Claim-Level Entailment** | *Not stated* | Yes (NLI) | Citation verifier (Falkor-IRAC) | *Not stated* | **Yes (DeBERTa-v3 cross-encoder NLI, English-primary)** |
| **Empirical Abstention** | *Not stated* | Yes | *Not stated* | *Not stated* | **Yes (Calibrated per-vertical threshold $\tau = 0.40$)** |
| **On-Prem / Offline Profile**| *Not stated* | *Not stated* | *Not stated* | *Not stated* | **Yes (Documented air-gapped data boundary via Ollama)** |
| **Open Evaluation Corpus** | *Not stated* | *Not stated* | Dataset released (Falkor-IRAC) | No (Proprietary) | **Committed in repo ($N=150$ gold pairs, raw CSV)** |

---

## 9. Deployment Economics & Edge Hardware Cost Profile

| Cost / Operating Dimension | Standard Cloud Mode (Serverless) | Sovereign On-Premise Edge Mode (`--profile onprem`) |
|---|---|---|
| **Hardware Capital Expenditure (CapEx)** | **$0** (No specialized hardware required) | **~Rs. 68,000 – Rs. 75,000** ($820 – $900) for edge workstation (AMD Ryzen 7 5700X, 32 GB RAM, NVIDIA RTX 3060 12 GB VRAM) |
| **Operational Expenditure (OpEx)** | **~$0.0011 per complex query** (Cloudflare Workers AI + Nomic Embeddings API) | **$0 API fees**; ~180W power draw under active inference (~Rs. 1.20 / hour electricity) |
| **Monthly Operating Cost (10,000 queries)** | **~$11.00 / month (~Rs. 920)** | **~$4.00 / month (~Rs. 330)** power cost (fixed workstation asset) |
| **Target Deployment Environment** | State E-Governance portals, cloud-hosted public web portals | Panchayat offices, Common Service Centers (CSCs), District Legal Services Authorities (DLSAs), air-gapped court complexes |
| **Emergency Human Handoff Routing** | Direct UI links to NALSA (15100), Cyber Crime (1930), PM-JAY (14555) | Local DLSA legal aid register & offline print-ready escalation slip |
