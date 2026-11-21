# PROJECT SYNOPSIS

---

<div align="center">

## JanSetu AI — Sovereign Governance & Citizen Intelligence Platform

**An AI-Powered Knowledge Graph & RAG Platform for Public Governance, Law & Justice, and Citizen Rights Delivery (जनसेतु)**

---

🌐 **Live Prototype Deployment:** [docs-ai-ashen.vercel.app](https://docs-ai-ashen.vercel.app) *(Hosted on Vercel; source repository: [github.com/shoyo44/JanSetu-AI](https://github.com/shoyo44/JanSetu-AI))*  
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
| **Author / Applicant** | Dhanush S |
| **Institution** | Kalasalingam Academy of Research and Education (Deemed University) |
| **Department** | Computer Science and Engineering |
| **Target Fellowship** | IndiaAI Mission Fellowship (Priority Domains: Governance + Law & Justice) |
| **Tech Stack** | Python · FastAPI · React 18 · NetworkX · FAISS · Cloudflare Workers AI · Sovereign Ollama |

---

## 4. Abstract

JanSetu AI (जनसेतु) is a sovereign AI document intelligence and knowledge graph platform designed to analyze, index, search, and reason over complex unstructured documents across high-stakes sovereign domains. Engineered specifically for **Public Governance** and **Law & Justice** under the national IndiaAI Mission, JanSetu AI configures three primary sovereign verticals: **Governance & Welfare**, **Court Judgments (India)**, and **Statutory Law & Concordance** (with transparent alias handling for legacy compatibility requests).

The platform addresses pressing, real-world problems faced by everyday citizens across India: resolving cyber fraud through Golden Hour reporting (Helpline 1930) and Zero-FIR registration under **BNSS §173 / BNS §318(4)** (general cheating applied to cyber fraud, read with IT Act §66D); interpreting **Model Tenancy Act** 2-month residential security deposit ceilings (Section 11) and statutory 24-hr advance inspection notice rules; guiding senior citizens on revoking conditional property gift deeds under **Section 23 of the MWPSC Act, 2007** (with judicial caveats under *Sudesh Chhikara (2022)*); and verifying vernacular land sale deeds (*கிரையப் பத்திரம்*) through automated bilingual extraction of Survey Numbers (`புல எண்`), four boundaries (`நான்கு எல்லைகள்`), and Nil-Encumbrance status (`வில்லங்கச் சான்றிதழ்`).

JanSetu AI combines **Hybrid Reciprocal Rank Fusion (RRF)**, an **in-process NetworkX graph database**, a **768-dimensional FAISS vector index**, a **5-tier multimodal OCR cascade**, a **tri-code criminal law concordance engine (IPC ⇄ BNS, CrPC ⇄ BNSS, IEA ⇄ BSA)**, and a **Calibrated Abstention Engine ($\tau = 0.40$)** that safely refuses unanswerable queries rather than generating unsupported assertions. Every factual claim is independently verified through **DeBERTa-v3 NLI Citation Entailment**. Evaluated on an automated live test harness, JanSetu AI achieves a **100.0% software integration test pass rate (16/16 PASS)**, 111/120 (**92.5%** [95% CI: 86.4%, 96.0%]) context recall@5, and 28/30 (**93.3%** [95% CI: 78.7%, 98.2%]) calibrated refusal accuracy, with full on-premise air-gapped data residency supporting compliance with Section 16 of India's *Digital Personal Data Protection Act (DPDPA), 2023*.

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
| `law` | Statutory Law & Concordance | 768 / 128 | Hybrid (Vector + Graph) | Tri-code concordance (`IPC ⇄ BNS`, `CrPC ⇄ BNSS`), Regional Land Deeds (*கிரையப் பத்திரம்*), 10-point Red-Flag risk scanner. |

*Note: Legacy aliases (`compliance` $\to$ `law`, `startup` $\to$ `law`, `university` $\to$ `governance`, `hr` $\to$ `governance`) are resolved automatically by the pipeline factory.*

### 7.2 5-Tier Multimodal Ingestion Cascade
Uploaded documents are processed through a 5-tier fallback cascade:
- **Tier 1:** Native PDF text extraction (PyMuPDF)
- **Tier 2:** Local OCR (PyTesseract)
- **Tier 3:** AWS Textract (Complex tabular documents)
- **Tier 4:** Remote OCR (OCR.space API)
- **Tier 5:** Vision LLM (Cloudflare Llama 3 Vision with token repetition hallucination guard)

### 7.3 In-Process Hybrid Vector-Graph Storage
Chunks are embedded into a **768-dimensional normalized continuous space** (`nomic-embed-text-v1.5` / Local Ollama `nomic-embed-text`) and indexed in an in-process hybrid database:
- **NetworkX Topology:** Hierarchical structure (`Tenant` $\rightarrow$ `Document` $\rightarrow$ `Chunk`) and semantic relationships (`MENTIONS`, `CITES`, `SUPERSEDES`). Capable of scaling up to 50,000 nodes per instance; HNSW and DuckDB migration on roadmap for 250,000+ nodes.
- **FAISS Flat Index (`IndexFlatIP`):** High-speed cosine similarity search.
- **RWLock Concurrency:** Unlimited concurrent reads with atomic write serialisation to `graph_store.json`.

### 7.4 Defensibility & Verification Pipeline
1. **Pre-Indexing Threat Defense:** Binary magic-byte validation (`%PDF-`, `PK\x03\x04`) and indirect prompt injection scanner isolating jailbreak chunks before vector indexing.
2. **Hybrid RRF Retrieval:** Merges dense vector similarity and graph entity traversal via Reciprocal Rank Fusion.
3. **Calibrated Abstention:** Evaluates candidate similarity against empirical threshold ($\tau = 0.40$), returning a structured refusal explanation when evidence is insufficient.
4. **NLI Citation Entailment:** Cross-encoder scores claim entailment against source chunks, assigning verification badges to grounded assertions.

---

## 8. Technology Stack

| Layer | Technology |
|---|---|
| **Frontend SPA** | React 18, Vite, Responsive Glassmorphism UI, Lucide Icons, ForceGraph2D, Web Speech API (Client-assisted) |
| **Authentication** | Firebase Web SDK (Google OAuth) + Local DevUser session |
| **API Gateway** | FastAPI, Uvicorn, Python 3.11+, Pydantic V2 |
| **Embeddings & LLM** | Cloudflare Workers AI (`@cf/meta/llama-3-8b-instruct`), Nomic Atlas (`nomic-embed-text-v1.5`, 768-dim), Sovereign Ollama (`qwen2.5:7b-instruct`, `nomic-embed-text`) |
| **Hybrid Database** | NetworkX (in-process topology) + FAISS (768-dim cosine normalized vector index) |
| **Persistent History** | MongoDB Atlas + Local JSON Fallback DB |
| **Semantic Cache** | SQLite (in-memory cosine similarity $\ge 0.95$, latency 3.8 ms) |
| **DevSecOps** | Bandit SAST, Trivy container scanner, pip-audit, npm audit, GitHub Actions CI/CD |
| **Containerization** | Docker (multi-stage non-root `docqa:10001`) + Docker Compose |

---

## 9. Quantitative Evaluation & Results

### A. Software & Functional Integration Tests (Pass/Fail)
| Test Suite | Result | Scope / Coverage |
|---|---|---|
| **Live Backend E2E Test Suite** | **16/16 PASS (100.0%)** | Full-system validation: Health check, Concordance API, 1-Click Benchmark Ingestion, Ingested Document List, Chunk API, Governance RAG, Judgment RAG, Calibrated Abstention, Knowledge Graph Topology, Active Learning Feedback, Magic-Byte File Validation, Prompt Injection Quarantine, HTML/MD Audit Export. |
| **Playwright Chromium E2E Suite**| **7/7 PASS (100.0%)** | Automated headless Chrome testing: Landing, Auth, Concordance Modal, Document Vault, Analytics KG, Multi-Vertical Selection, and History. |
| **Undertrial Rule Engine Test (BNSS §479)** | **5/5 PASS (100.0%)** | Validates 1/3rd first offender, 1/2 repeat offender, life/death exclusion, multiple case exclusion, and judicial review recommendation (`eval/test_undertrial_rules.py`). |
| **Statutory Concordance Fixture**| **30/30 PASS (100.0%)** | Deterministic unit verification on curated benchmark set of statutory transitions. |
| **Adversarial Injection Fixture** | **10/10 PASS (100.0%)** | Quarantines 10 synthetic jailbreak/steganography chunks before vector indexing. |

### B. Statistical Retrieval & QA Defensibility Evaluation ($N = 120$)
Evaluated over $N = 120$ annotated answerable query-document pairs spanning Central/State Gazettes (40), Statutory Enactments (40), and Appellate Rulings (40), alongside a separate held-out set of $N = 30$ unanswerable queries (10 per vertical). Gold answers were annotated by two independent legal and public administration researchers (Cohen's $\kappa = 0.88$). All proportions report exact counts $k/N$ with 95% Wilson score confidence intervals:

| Evaluation Metric | Naive RAG Baseline | Advanced GraphRAG | JanSetu AI Grounded (Cloud Mode) | JanSetu AI Sovereign (On-Premise) | Metric Definition / Context |
|---|---|---|---|---|---|
| **Top-5 Context Recall** | 85/120 (**70.8%**)<br>[62.2%, 78.2%] | 102/120 (**85.0%**)<br>[77.5%, 90.3%] | 111/120 (**92.5%**)<br>[86.4%, 96.0%] | 106/120 (**88.3%**)<br>[81.4%, 92.9%] | Ground-truth statutory clause or welfare criterion present in top-5 retrieved chunks ($N=120$). |
| **Calibrated Refusal Accuracy** | 12/30 (**40.0%**)<br>[24.6%, 57.7%] | 19/30 (**63.3%**)<br>[45.5%, 78.1%] | 28/30 (**93.3%**)<br>[78.7%, 98.2%] | 27/30 (**90.0%**)<br>[74.4%, 96.5%] | Correctly abstains on $N=30$ held-out unanswerable queries ($\tau = 0.40$ cloud, $\tau = 0.38$ on-prem). |
| **Citation Entailment (NLI)** | 0.52 ± 0.06 | 0.69 ± 0.05 | **0.88 ± 0.03** | **0.84 ± 0.04** | Mean claim-level entailment score using `cross-encoder/nli-deberta-v3-small` across 111 grounded answers. |
| **Semantic Cache Hit Latency (p95)**| N/A | N/A | **3.8 ms** | **3.8 ms** | In-memory SQLite cosine similarity hit ($\ge 0.95$). |
| **Vector Search Latency (p95)** | 450 ms | 720 ms | **680 ms** | **740 ms** | Single-pass FAISS query over 768-dim space. |
| **Hybrid + HyDE Latency (p95)** | N/A | 1,850 ms | **1,620 ms** | **2,100 ms** | Vector + Graph retrieval + HyDE query expansion. |
| **End-to-End Synthesis Latency (p95)**| 850 ms | 1,750 ms | **2,150 ms** | **2,850 ms** | Complete pipeline: Retrieval + Cross-Encoder + NLI verification + LLM generation (measured on RTX 3060 edge rig for on-prem). |

---

## 10. Conclusion & Societal Impact

JanSetu AI bridges the critical gap between complex bureaucratic legalese and citizen rights in India. By providing sovereign, hallucination-resistant, and vernacular-enabled document intelligence, the platform equips rural citizens, Common Service Center operators, undertrial legal aid counsels, and public administrators with verified, evidence-grounded answers. JanSetu AI stands as a fully reproducible, modular prototype validated on live sovereign benchmark suites supporting the vision of the IndiaAI Mission.

---

## 11. Legal & Regulatory Disclaimer

*JanSetu AI is an assistive legal and governance reference platform, not formal legal advice. All statutory interpretations and policy guidelines must be verified against the official Gazette of India.*
