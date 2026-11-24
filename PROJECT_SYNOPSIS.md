# PROJECT SYNOPSIS

---

<div align="center">

## JanSetu AI — Sovereign Governance & Citizen Intelligence Platform

**An AI-Powered Knowledge Graph & RAG Platform for Public Governance, Law & Justice, and Citizen Rights Delivery (जनसेतु)**

---

🌐 **Live Cloud Demo (AWS EC2, us-east-1; plain HTTP prototype, do not enter real citizen PII):** [http://ec2-98-93-55-8.compute-1.amazonaws.com:3000](http://ec2-98-93-55-8.compute-1.amazonaws.com:3000) *(Secondary Web Mirror: [docs-ai-ashen.vercel.app](https://docs-ai-ashen.vercel.app); repository: [github.com/shoyo44/JanSetu-AI](https://github.com/shoyo44/JanSetu-AI))*  
📁 **Repository:** [github.com/shoyo44/JanSetu-AI](https://github.com/shoyo44/JanSetu-AI)  

---

</div>

---

## 1. Project Title

**JanSetu AI (जनसेतु) — Sovereign Governance & Citizen Intelligence Platform**

---

## 2. Project Category

Artificial Intelligence · Natural Language Processing · Information Retrieval · Legal & Public Governance Informatics · Full-Stack Web Application

---

## 3. Team / Author

| Field | Details |
|---|---|
| **Author / Applicant** | Dhanush S (B.Tech Final Year, Dept. of CSE) |
| **Faculty Guide / Supervisor** | [Faculty Guide Name & Designation, Dept. of Computer Science & Engineering, KARE] *(Matches Institutional Endorsement Letter)* |
| **Institution** | Kalasalingam Academy of Research and Education (Deemed University) |
| **Department** | Computer Science and Engineering |
| **Target Fellowship** | IndiaAI Fellowship 2026–27 (Undergraduate track; Priority Domains: Governance + Law & Justice) |
| **Tech Stack** | Python · FastAPI · React 18 · NetworkX · FAISS · Cloudflare Workers AI · Sovereign Ollama |

---

## 4. Abstract

JanSetu AI (जनसेतु) is a sovereign AI document intelligence and knowledge graph platform designed to analyze, index, search, and reason over complex unstructured documents across high-stakes sovereign domains. Engineered specifically for **Public Governance** and **Law & Justice** under the national IndiaAI Mission, JanSetu AI configures three primary sovereign verticals: **Governance & Welfare**, **Court Judgments (India)**, and **Statutory Law & Concordance** (with transparent alias handling for legacy compatibility requests).

The platform addresses pressing, real-world problems faced by everyday citizens across India: resolving cyber fraud through Golden Hour reporting (Helpline 1930) and Zero-FIR registration under **BNSS §173 / BNS §318(4)** (general cheating applied to cyber fraud, read with IT Act §66D); interpreting **Model Tenancy Act** 2-month residential security deposit ceilings (Section 11) and statutory 24-hr advance inspection notice rules; guiding senior citizens on revoking conditional property gift deeds under **Section 23 of the MWPSC Act, 2007** (with judicial caveats under *Sudesh Chhikara (2022)*); and verifying vernacular land sale deeds (*கிரையப் பத்திரம்*) through automated bilingual extraction of Survey Numbers (`புல எண்`), four boundaries (`நான்கு எல்லைகள்`), and Nil-Encumbrance status (`வில்லங்கச் சான்றிதழ்`).

JanSetu AI combines **Hybrid Reciprocal Rank Fusion (RRF)**, an **in-process NetworkX graph database**, a **768-dimensional FAISS vector index**, a **Tamper-Evident SHA-256 Merkle Provenance Ledger** (an internal hash tree, not an implementation of MeitY's National Blockchain Framework), a **5-tier multimodal OCR cascade**, a **tri-code criminal law concordance engine (IPC ⇄ BNS, CrPC ⇄ BNSS, IEA ⇄ BSA)**, **5-Layer Sovereign Government Guardrails (PII Masking & Safety Shield)**, and a **Calibrated Abstention Engine** (initial threshold $\tau = 0.40$ chosen on a 20-query development set, to be recalibrated on the full benchmark) that safely refuses unanswerable queries rather than generating unsupported assertions. Every factual claim is independently verified through **DeBERTa-v3 NLI Citation Entailment** (English-primary). Evaluated on an automated live test harness and deployed on AWS EC2 (`http://ec2-98-93-55-8.compute-1.amazonaws.com:3000`; plain HTTP demo, do not enter sensitive personal data), JanSetu AI achieves a **100.0% software integration test pass rate (16/16 PASS)**, deterministic statutory concordance (30/30), undertrial rule verification (8/8), and adversarial injection defense (10/10), establishing a curated 150-query multilingual gold benchmark for sovereign evaluation (102 English, 39 Hindi, 9 Tamil), with full on-premise air-gapped data residency supporting compliance with Section 16 of India's *Digital Personal Data Protection Act (DPDPA), 2023*. Measured baseline retrieval and refusal metrics across naive, graph, cloud, and on-premise configurations form the first fellowship deliverable.

---

## 5. Problem Statement

Everyday citizens, public administrators, and judicial practitioners face acute structural barriers:
1. **Welfare Information Asymmetry:** Millions of eligible rural citizens are excluded from direct benefit transfer (DBT) and healthcare schemes (*PM-KISAN, Ayushman Bharat PM-JAY*) due to impenetrable bureaucratic gazettes and poorly understood exclusion criteria (pensioners $\ge ₹10,000$, institutional landholders).
2. **Decadal Criminal Law Transition:** The July 1, 2024 implementation of the *Bharatiya Nyaya Sanhita (BNS)*, *Bharatiya Nagarik Suraksha Sanhita (BNSS)*, and *Bharatiya Sakshya Adhiniyam (BSA)* created friction in bridging decades of colonial precedents with modern statutory charges, especially concerning undertrial bail relief under BNSS §479 for India's 77.1% undertrial inmate population (NCRB PSI 2021).
3. **Cyber Financial Exploitation:** Citizens falling victim to digital financial fraud lose funds due to delays in executing "Golden Hour" freezing protocols via Helpline 1930 and lack knowledge of their statutory right to file a Zero-FIR under BNSS §173.
4. **Urban Tenancy & Elder Vulnerability:** Renters face arbitrary 6–10 month security deposit demands, while elderly parents are abandoned after gifting property to adult children.
5. **Vernacular Land Deed Disputes:** Rural property buyers in Tamil Nadu and regional states face title fraud due to ambiguous survey subdivisions, boundary discrepancies, and unverified encumbrances in regional deeds (*கிரையப் பத்திரம்*).
6. **Hallucination & Data Sovereignty Risks:** Generic cloud LLMs hallucinate non-existent statutory clauses and compromise sensitive public data across cross-border cloud boundaries.

---

## 6. Objectives

1. **Deploy 3 Primary Sovereign Verticals** (`governance`, `judgment`, `law`) with domain-specific chunking, hybrid retrieval, and customized reranking mechanisms.
2. **Deliver 7 Preloaded Citizen Benchmarks** in Document Vault for 1-click evaluation of high-stakes citizen problems (PM-KISAN, Synthetic Judicial Benchmark Exemplar, Ayushman Bharat, Tamil Land Deed, Cyber Zero-FIR, Model Tenancy Act, Senior Citizens Act §23).
3. **Build an Indic Land Administration Engine** extracting Survey Numbers, four boundaries, consideration, and encumbrance covenants from regional Tamil sale deeds (*கிரையப் பத்திரம்*).
4. **Bridge the 2024 Criminal Law Transition** via a bidirectional concordance hash-map (`IPC ⇄ BNS`, `CrPC ⇄ BNSS`, `IEA ⇄ BSA`), highlighting undertrial release rights under BNSS §479 and Zero-FIR registration under BNSS §173.
5. **Suppress Hallucinations through Calibrated Defensibility:**
   - Calibrated Abstention Engine ($\tau = 0.40$) to safely refuse out-of-scope or unanswerable queries.
   - DeBERTa-v3 Cross-Encoder NLI to verify that every synthesized factual assertion is strictly entailed by source document chunks.
6. **Ensure Strict Data Sovereignty:** Provide an air-gapped on-premise execution profile via local Ollama (`qwen2.5:7b-instruct`, `nomic-embed-text` 768-dim) supporting institutional data residency within host boundaries under DPDPA 2023 Section 16.

---

## 7. System Architecture & Methodology

### 7.1 Sovereign Multi-Vertical Matrix

| Primary Vertical Key | Display Name | Chunking (Tokens/Overlap) | Retrieval Modality | Specialized IndiaAI Capability |
|---|---|---|---|---|
| `governance` | Governance & Welfare | 500 / 100 | Hybrid (Vector + Graph) | Citizen *Jan Suvidha* plain-language cards, DBT subsidy mapping, eligibility vs exclusion separation. |
| `judgment` | Court Judgments (India) | 500 / 100 | Hybrid (Vector + Graph) | Binding *Ratio Decidendi* extraction, bail condition synthesis under BNSS §483 / §479, Article 21 protections. |
| `law` | Statutory Law & Concordance | 400 / 80 | Hybrid (Vector + Graph) | Tri-code concordance (`IPC ⇄ BNS`, `CrPC ⇄ BNSS`), Regional Land Deeds (*கிரையப் பத்திரம்*), 10-point Red-Flag risk scanner. |

*Note: Legacy aliases (`compliance` $\to$ `law`, `startup` $\to$ `law`, `university` $\to$ `governance`, `hr` $\to$ `governance`) are resolved automatically by the pipeline factory.*

### 7.2 5-Tier Multimodal Ingestion Cascade
Uploaded documents are processed through a 5-tier fallback cascade:
- **Tier 1:** Native PDF text extraction (PyMuPDF)
- **Tier 2:** Local OCR (PyTesseract with Indic models)
- **Tier 3:** AWS Textract (Complex tabular documents)
- **Tier 4:** Remote OCR (OCR.space API)
- **Tier 5:** Vision LLM (Cloudflare Llama 3 Vision with token repetition hallucination guard)
*(Note: Evaluated as a functional multi-tier fallback cascade ensuring zero-failure document ingestion; empirical Character Error Rate (CER) and Word Error Rate (WER) benchmarking across degraded historic gazettes is slated for the fellowship research phase).*

### 7.3 In-Process Hybrid Vector-Graph Storage
Chunks are embedded into a **768-dimensional normalized continuous space** (`nomic-embed-text-v1.5` / Local Ollama `nomic-embed-text`) and indexed in an in-process hybrid database:
- **NetworkX Topology:** Hierarchical structure (`Tenant` $\rightarrow$ `Document` $\rightarrow$ `Chunk`) and semantic relationships (`MENTIONS`, `CITES`, `SUPERSEDES`). Capable of scaling up to 50,000 nodes per instance; HNSW and DuckDB migration on roadmap for 250,000+ nodes.
- **FAISS Flat Index (`IndexFlatIP`):** High-speed cosine similarity search.
- **RWLock Concurrency:** Unlimited concurrent reads with atomic write serialisation to `graph_store.json`.

### 7.4 Defensibility & Verification Pipeline
1. **Pre-Indexing Threat Defense:** Binary magic-byte validation (`%PDF-`, `PK\x03\x04`) and indirect prompt injection scanner isolating jailbreak chunks before vector indexing.
2. **5-Layer Sovereign Government Guardrails:** Regex and heuristic filters that mask Aadhaar numbers (`XXXX-XXXX-1234`) under Aadhaar Act 2016 §29, mask PANs, anonymize phone numbers/emails under DPDP Act 2023, and outright block prompts requesting counterfeit government IDs or forged land records.
3. **Hybrid RRF Retrieval:** Merges dense vector similarity and graph entity traversal via Reciprocal Rank Fusion.
4. **Calibrated Abstention:** Evaluates candidate similarity against empirical threshold ($\tau = 0.40$), returning a structured refusal explanation when evidence is insufficient.
5. **NLI Citation Entailment:** Cross-encoder scores claim entailment against source chunks, assigning verification badges to grounded assertions.

### 7.5 Tamper-Evident SHA-256 Merkle Provenance Ledger
- Generates a cryptographic SHA-256 Merkle DAG tree for every ingested document chunk.
- Calculates an immutable 256-bit Merkle Root anchored to an audit ledger with genesis block sequencing.
- Exposes on-demand mathematical verification (`/api/v1/ledger/verify/{doc_id}`): recalculating the Merkle tree from current chunks instantly flags `TAMPERING_DETECTED` if any chunk has been altered, or confirms `TAMPER_EVIDENT_VERIFIED`.

---

## 8. Technology Stack

| Layer | Technology |
|---|---|
| **Frontend SPA** | React 18, Vite, Responsive Glassmorphism UI, Lucide Icons, ForceGraph2D, Web Speech API (Client-assisted) |
| **Authentication** | Firebase Web SDK (Google OAuth) + Local DevUser session |
| **API Gateway** | FastAPI, Uvicorn, Python 3.11+, Pydantic V2 |
| **Document Provenance** | Tamper-Evident SHA-256 Merkle DAG Ledger (`core/sovereign_ledger.py`; local audit log) |
| **Sovereign Guardrails** | 5-Layer Shield (Aadhaar Act 2016 §29, DPDP Act 2023 PII Masking, Anti-Forgery Gates) |
| **LLM & Inference Tier** | Groq LPU (`qwen/qwen3-32b`, `openai/gpt-oss-120b`), Cloudflare Workers AI, Sovereign Ollama (`qwen2.5:7b`), Extractive RAG fallback |
| **Hybrid Database** | NetworkX (in-process topology) + FAISS (768-dim cosine normalized vector index) |
| **Persistent History** | Containerized MongoDB + Local JSON Fallback DB |
| **Semantic Cache** | SQLite (in-memory cosine similarity $\ge 0.95$, indicative development measurement ~3.8 ms) |
| **DevSecOps** | Bandit SAST, Trivy container scanner, pip-audit, npm audit, GitHub Actions CI/CD |
| **Containerization** | Docker (multi-stage non-root `docqa:10001`) + Docker Compose (Frontend, Backend, Mongo, Prometheus, Grafana) |

---

## 9. Quantitative Evaluation & Results

### A. Software & Functional Integration Tests (Pass/Fail)
| Test Suite | Result | Scope / Coverage |
|---|---|---|
| **Live Backend E2E Test Suite** | **16/16 PASS (100.0%)** | Full-system validation: Health check, Concordance API, 1-Click Benchmark Ingestion, Ingested Document List, Chunk API, Governance RAG, Judgment RAG, Calibrated Abstention, Knowledge Graph Topology, Active Learning Feedback, Magic-Byte File Validation, Prompt Injection Quarantine, HTML/MD Audit Export. |
| **Playwright Chromium E2E Suite**| **7/7 PASS (100.0%)** | Automated headless Chrome testing: Landing, Auth, Concordance Modal, Document Vault, Analytics KG, Multi-Vertical Selection, and History. |
| **Undertrial Rule Engine Test (BNSS §479)** | **8/8 PASS (100.0%)** | Validates 1/3rd first offender on bond, 1/2 repeat offender on bail, life/death exclusion, multiple pending cases bar (§479(2)), accused delay deduction, full-maximum cap, judicial continued detention, and jail superintendent application duty (`eval/test_undertrial_rules.py`). |
| **Statutory Concordance Fixture**| **30/30 PASS (100.0%)** | Deterministic unit verification on curated benchmark set of statutory transitions. |
| **Adversarial Injection Fixture** | **10/10 PASS (100.0%)** | Quarantines 10 synthetic jailbreak/steganography chunks before vector indexing. |

### B. Sovereign Gold Benchmark & Comparative Evaluation Framework ($N = 150$)
The repository establishes a standardized 150-query multilingual gold evaluation benchmark committed at [`eval/gold/sovereign_benchmark_qa.jsonl`](./eval/gold/sovereign_benchmark_qa.jsonl):
- **120 Answerable Queries:** 40 Public Governance (PM-KISAN, Ayushman Bharat, Senior Citizens Act), 40 Statutory Law & Citizen Rights (Cyber FIR, Model Tenancy Act, Tamil Land Deeds), 40 Judicial Precedents & Bail Reforms (Supreme Court bail ruling, Statutory Concordance).
- **30 Held-Out Unanswerable Queries:** 10 per vertical, to evaluate calibrated abstention without hallucinating.
- **Multilingual Scope:** 102 queries in English, 39 queries in Hindi (हिन्दी), and 9 queries in Tamil (தமிழ்).
- **Calibrated Abstention Engine:** Initial similarity threshold $\tau = 0.40$ (cloud) and $\tau = 0.38$ (on-premise) chosen on an isolated 20-query development split (`eval/gold/dev_tuning_split.jsonl`), to be recalibrated on the full benchmark.
- **Comparative Evaluation Harness:** [`eval/run.py`](./eval/run.py) provides the evaluation harness across 4 architectural paradigms: Naive RAG, Advanced GraphRAG, Sovereign On-Premise, and Grounded Cloud Mode. Full empirical comparative metrics across all configurations are being recorded via live execution for open publication on AIKosh as part of the IndiaAI Fellowship deliverables.

---

## 10. Conclusion & Societal Impact

JanSetu AI bridges the critical gap between complex bureaucratic legalese and citizen rights in India. By providing sovereign, hallucination-resistant, and vernacular-enabled document intelligence, the platform equips rural citizens, Common Service Center operators, undertrial legal aid counsels, and public administrators with verified, evidence-grounded answers. JanSetu AI stands as a fully reproducible, modular prototype validated on live sovereign benchmark suites supporting the vision of the IndiaAI Mission.

---

## 11. Legal & Regulatory Disclaimer

*JanSetu AI is an assistive legal and governance reference platform, not formal legal advice. All statutory interpretations and policy guidelines must be verified against the official Gazette of India.*
