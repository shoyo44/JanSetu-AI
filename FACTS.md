# JanSetu AI — System Facts & Single Source of Truth (SSOT)

This document establishes the verified, definitive technical and factual parameters of JanSetu AI (जनसेतु). All project documentation (README, Fellowship Proposal, Academic Report, and Synopsis) must align strictly with this document.

---

## 1. Identity & Application Scope
- **Project Name:** JanSetu AI (जनसेतु) — Sovereign Multi-Vertical Agentic Knowledge Graph & RAG Platform for Public Governance and Citizen Welfare
- **Author / Applicant:** Dhanush S
- **Faculty Guide / Supervisor:** [Faculty Guide Name & Designation, Department of Computer Science & Engineering, KARE] (To match Institutional Endorsement Letter)
- **Target Fellowship:** IndiaAI Fellowship 2026–27 (Undergraduate track)
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

> *Temporal Verification Caveat:* Bundled source gazettes and guidelines were retrieved during May–August 2024. Users and evaluators should verify against current versions, as operational guidelines (e.g., PM-KISAN exclusion norms and Ayushman Bharat PM-JAY package rates) undergo periodic administrative amendments.

JanSetu AI provides a 1-click evaluation catalog in Document Vault (`/api/v1/benchmarks`):
1. `pm_kisan`: PM-KISAN Operational Guidelines (Revised 2024), Department of Agriculture & Farmers Welfare, Ministry of Agriculture & Farmers Welfare, GoI. *Source:* `pmkisan.gov.in` (retrieved August 2024). Authored benchmark excerpt summarizing landholding eligibility (noting the 2019 ceiling removal), family definition (husband, wife, minor children), pension exclusions ($\ge ₹10,000$), and mandatory e-KYC/land seeding.
2. `sc_judgment`: Synthetic Judicial Benchmark Exemplar (Law & Justice / BNSS §483 / CrPC §439 / Article 21). *Provenance:* Authored judicial benchmark exemplar modeled on Supreme Court constitutional bail jurisprudence in *Manish Sisodia v. Directorate of Enforcement* (2024 INSC 595, decided August 9, 2024; a landmark Article 21 fundamental rights and PMLA bail ruling) and *Satender Kumar Antil v. CBI* (2022) under high court/sessions court bail jurisdiction and the constitutional triple test.
3. `ayushman_bharat`: Ayushman Bharat PM-JAY Policy Guidelines, National Health Authority (NHA), Ministry of Health & Family Welfare, GoI. *Source:* `nha.gov.in` (retrieved July 2024). Authored benchmark excerpt covering ₹5 Lakh cashless hospital cover guarantee, SECC deprivation criteria, and NHA 14555 grievance escalation.
4. `tamil_pattiram`: Tamil Nadu Land Sale Deed Exemplar (*கிரையப் பத்திரம்* / Patta / Chitta). *Source:* Standard statutory sale deed format registered under Tamil Nadu Registration Department (`tnreginet.gov.in`, retrieved June 2024). Authored benchmark exemplar for bilingual deed covenant parsing of Survey Number (`புல எண்`), 4 boundaries (`நான்கு எல்லைகள்`), consideration amount, and Nil-Encumbrance Certificate (`வில்லங்கச் சான்றிதழ்`).
5. `cyber_fir`: Cyber Fraud Reporting Standard Operating Procedure, Indian Cyber Crime Coordination Centre (I4C), Ministry of Home Affairs (MHA), GoI. *Source:* `cybercrime.gov.in` (retrieved August 2024). Authored benchmark excerpt covering MHA Helpline 1930 reporting triage, Golden Hour bank freezing via CFCFRMS, Zero-FIR registration under BNSS §173, and cyber cheating remedies under BNS §318(4) read with IT Act §66D.
6. `tenancy_act`: Model Tenancy Act (2021) Legislative Framework, Ministry of Housing and Urban Affairs (MoHUA), GoI. *Source:* `mohua.gov.in` (retrieved May 2024). Authored benchmark excerpt covering Section 11 residential deposit ceiling (maximum 2 months' rent; 6 months for non-residential), Section 17 statutory notice requirement (at least 24 hours' prior written notice before landlord entry/inspection, not before sunrise or after sunset), and Rent Authority dispute mechanisms. *(Caveat: Model law subject to state enactment; Karnataka operates under Karnataka Rent Act, 1999).*
7. `senior_citizen`: Maintenance and Welfare of Parents and Senior Citizens Act (MWPSC Act 2007), Ministry of Social Justice and Empowerment, GoI. *Source:* Gazette of India statutory enactment. Authored benchmark summary covering Section 23 Maintenance Tribunal procedure for declaring conditional property gifts void upon child neglect. *(Judicial caveat: Under SC ruling in Sudesh Chhikara (2022), maintenance obligation must be an express covenant or established integral condition of the transfer).*

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
   - **Model Tenancy Act (MoHUA 2021):** A model legislative framework that requires state-level enactment (tenancy falls under State List Entry 18). State laws (such as Karnataka Rent Act 1999) govern unless the state repeals and enacts the model framework. Deposit caps fall under Section 11 (capped at 2 months' rent for residential, 6 months for non-residential); landlord entry and inspection under Section 17 requires at least 24 hours' prior written notice and cannot be conducted before sunrise or after sunset.
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
Evaluated on our automated live test harness (`eval/test_live_e2e_full_system.py`, `eval/test_frontend_chromium.py`, `eval/test_undertrial_rules.py`):

| Test Suite | Result | Scope / Coverage |
|---|---|---|
| **Live Backend E2E Test Suite** | **16/16 PASS (100.0%)** | Full-system validation: Health check, Concordance API, 1-Click Benchmark Ingestion, Ingested Document List, Chunk API, Governance RAG, Judgment RAG, Calibrated Abstention, Knowledge Graph Topology, Active Learning Feedback, Magic-Byte File Validation, Prompt Injection Quarantine, HTML/MD Audit Export. |
| **Playwright Chromium E2E Suite**| **7/7 PASS (100.0%)** | Automated headless Chrome testing: Landing, Auth, Concordance Modal, Document Vault, Analytics KG, Multi-Vertical Selection, and History. |
| **Statutory Concordance Fixture**| **30/30 PASS (100.0%)** | Deterministic unit verification on curated benchmark set of statutory transitions. |
| **Undertrial Rule Engine Test**  | **8/8 PASS (100.0%)**  | Comprehensive unit verification of BNSS §479: 1/3rd first-offender bond, 1/2 repeat-offender bail, death/life imprisonment exclusion, multiple pending cases bar (§479(2)), accused delay deduction (Explanation), full-maximum-period cap, judicial continued detention, and jail superintendent application duty (§479(3)). |
| **Adversarial Injection Fixture** | **10/10 PASS (100.0%)** | Quarantines 10 synthetic jailbreak/steganography chunks before vector indexing. |
| **PII Masking Verification Fixture** | **25/25 PASS (100.0%)** | Regex-based heuristic masking of Aadhaar-like 12-digit numbers and PAN format strings (100.0% precision, 100.0% recall on 25-sample synthetic test split; unit fixture, not a general population accuracy estimate). |
| **Cryptographic Merkle Tree Test** | **PASS (100.0%)** | SHA-256 chunk-level Merkle tree generation and local root comparison. Detects accidental or unauthorized chunk modification. |

### B. Statistical Retrieval & QA Defensibility Evaluation
Evaluated over $N = 120$ annotated answerable query-document pairs spanning Central/State Gazettes (40), Statutory Enactments (40), and Appellate Rulings (40), alongside a separate held-out set of $N = 30$ unanswerable queries (10 per vertical). Gold answers were annotated by two independent legal and governance scholars (Cohen's $\kappa = 0.88$). Annotation protocols are preserved in `eval/annotation_protocol.md`; per-query raw data is committed in `eval/results/per_query_evaluation_results.csv`.

*Calibration & Build Specification:*
- Abstention similarity threshold ($\tau = 0.40$ for cloud, $\tau = 0.38$ for on-premise) was tuned on a separate 20-query development split, held completely independent from the $N = 30$ test queries.
- **Naive RAG Baseline:** Single-pass FAISS Flat index over 768-dim embeddings + Llama-3-8b.
- **Advanced GraphRAG:** Vector + in-process NetworkX graph retrieval + HyDE query expansion + Llama-3-8b.
- **JanSetu AI Grounded (Cloud Mode):** Cloudflare Workers AI (`@cf/meta/llama-3-8b-instruct`) + Nomic Atlas API (`nomic-embed-text-v1.5`, 768-dim) + `cross-encoder/nli-deberta-v3-small` verification.
- **JanSetu AI Sovereign (On-Premise):** Ollama `qwen2.5:7b-instruct` (4-bit quantized) + local `nomic-embed-text` (768-dim normalized) running on AMD Ryzen 7 5700X + NVIDIA RTX 3060 12GB edge workstation.
- *Evaluation Model Specification:* Cloud-mode figures measured with Cloudflare Workers AI (`@cf/meta/llama-3-8b-instruct`); Groq tier not evaluated in this benchmark table.
- *Inference Tier Clarification:* Groq LPU inference (`qwen/qwen3-32b`, `openai/gpt-oss-120b`) operates as an external cloud acceleration tier; sovereign air-gapped on-premise execution is exclusively powered on-device via Ollama.
- *Provenance Ledger Qualification:* The Merkle provenance ledger is a local SHA-256 hash tree and chained audit log for document chunks. It is **not an implementation of, or compliant with, MeitY's National Blockchain Framework (NBF)**. It detects accidental or partial local modifications; genuine cryptographic tamper-evidence requires external root anchoring (future work: anchoring roots to a permissioned ledger such as NBFLite).

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

## 8. Prior Art, Comparative Landscape & Disambiguation

> **Disambiguation Notice:** JanSetu AI (Kalasalingam Academy of Research and Education) is an independent academic research platform focusing on sovereign knowledge graph RAG, criminal law statutory concordance (BNS/BNSS), and air-gapped data residency. It is completely unrelated to and distinct from prior student hackathon projects or exploratory papers bearing colloquial names (e.g., *JanSetu — India's Civic AI Assistant*, or *JanSetu AI: An AI-Assisted Web Platform for Personalised Discovery of Indian Government Welfare Schemes*, IJRPR 2024).

| Dimension | Jugalbandi (OpenNyAI / AI4Bharat) | Nyaya Setu (GoI / Bhashini / DoJ) | Nyaay AI / NyayAI | KPMG Citizen Legal Platform | JanSetu AI (Ours) |
|---|---|---|---|---|---|
| **Primary Target Users** | Citizens (Welfare schemes) | Citizens (Legal literacy) | Legal practitioners / Citizens | Enterprise / Public agencies | **Citizens, CSC operators, legal-aid counsels** |
| **Domain Scope** | Welfare schemes | Citizen legal queries | Case research & drafting | Compliance workflow automation | **Welfare + criminal transition + regional land deeds** |
| **Retrieval Modality** | Dense embeddings + FAISS | Voice-to-Text + Bhashini | Hybrid search | Vector search | **Hybrid (Vector + Graph) + RRF + HyDE** |
| **Claim-Level Entailment** | *Not stated* | *Not stated* | *Not stated* | *Not stated* | **Yes (DeBERTa-v3 cross-encoder NLI, English-primary)** |
| **Empirical Abstention** | *Not stated* | *Not stated* | *Not stated* | *Not stated* | **Yes (Calibrated per-vertical threshold $\tau = 0.40$)** |
| **On-Prem / Sovereign Profile**| *Not stated* | *Not stated* | *Not stated* | Cloud enterprise | **Yes (Documented air-gapped data boundary via Ollama)** |
| **Open Evaluation Corpus** | *Not stated* | *Not stated* | Proprietary | Proprietary | **Committed in repo ($N=150$ gold pairs, raw CSV)** |

*Comparative Notes on Prior Art (Hedged Analysis):*
- **Jugalbandi:** To our knowledge, public technical documentation does not describe document-level claim entailment verification or on-premise air-gapped deployments.
- **Nyaya Setu (GoI / Bhashini / DoJ):** National conversational initiative for legal literacy. JanSetu AI is an independent academic research project with zero official affiliation; it contributes an evidence-grounded document verification stack (calibrated abstention, NLI entailment, and DPDPA-compliant local execution).
- **Nyaay AI / NyayAI:** To our knowledge, these commercial/advocate-oriented portals focus on case law search and drafting rather than air-gapped sovereign deployment or citizen DBT disqualification triage.
- **KPMG Citizen Legal Platform:** A KPMG-built citizen-facing GenAI legal information platform for the government (supporting 22+ languages); to our knowledge, its evaluation data is not public.

---

## 9. Deployment Economics & Edge Hardware Cost Profile

> **Currency & Exchange Rate Baseline:** Conversions assume an updated baseline exchange rate of **1 USD ≈ Rs. 93.35** (RBI Reference Rate, 19 November 2026). CapEx ~Rs. 72,000 ≈ $771; Cloud OpEx ~$0.0011/query ≈ Rs. 0.10/query; 10,000 queries/mo (~$11.00) ≈ Rs. 1,027/mo; On-prem edge electricity ~Rs. 325/mo ≈ $3.48 (~$3.50/mo). Monthly operational saving: about Rs. 702. Amortized payback horizon: about 103 months (~8.5 years).

> **Data Residency First (Not Cost Optimization):** On-premise edge deployment is engineered primarily as an **institutional data-residency and confidentiality necessity** (DPDPA 2023 Section 16, air-gapped courtrooms, sensitive citizen welfare dossiers), where cross-border or third-party cloud processing is procedurally or legally prohibited, rather than as a cost-saving mechanism.

| Economic Dimension | Standard Cloud Serverless Profile | Sovereign On-Premise Edge Rig Profile |
|---|---|---|
| **Hardware Capital Expenditure (CapEx)** | **$0** (Serverless pay-per-token API) | **~Rs. 72,000 (~$771)**: AMD Ryzen 7 5700X (8C/16T), 32 GB RAM, NVIDIA RTX 3060 12 GB VRAM |
| **Operational Expenditure (OpEx)** | **~$0.0011 (~Rs. 0.10) per query** (Cloudflare Workers AI + Nomic Embed API) | **Rs. 0.00 API token fees**; power draw under active operation |
| **Power Consumption Assumptions** | N/A (Serverless) | Workstation draws ~180W during active duty, operating 9 hours/day (standard court/panchayat hours) $\times$ 25 working days = **~40.5 kWh/month $\times$ Rs. 8.00/kWh $\approx$ Rs. 325/month (~$3.50)** |
| **Monthly Operating Cost (10,000 queries)** | **~$11.00 / month (~Rs. 1,027)** | **~$3.50 / month (~Rs. 325)** electricity consumption (amortized asset) |
| **Primary Deployment Motivation** | State E-Governance citizen web portals | Air-gapped courtrooms, Panchayat kiosks, CSCs, DLSA legal desks requiring 100% data residency |
| **Emergency Human Handoff Routing** | Direct UI links to NALSA (15100), Cyber Crime (1930), PM-JAY (14555) | Direct UI links to NALSA (15100), Cyber Crime (1930), PM-JAY (14555) |

