# JanSetu AI — Sovereign Governance & Citizen Intelligence Platform
### *जनसेतु · Sovereign Multi-Vertical Agentic Knowledge Graph & RAG Platform for Public Governance and Citizen Welfare*

[![IndiaAI Fellowship](https://img.shields.io/badge/IndiaAI-Fellowship%20Aligned-orange.svg)](https://indiaai.gov.in/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%200.110-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB.svg)](https://react.dev/)
[![Security](https://img.shields.io/badge/DevSecOps-Bandit%20%7C%20Trivy%20%7C%20pip--audit-red.svg)](https://github.com/shoyo44/JanSetu-AI)
[![Data Sovereignty](https://img.shields.io/badge/Sovereignty-DPDPA%202023%20%7C%20Ollama-blue.svg)](https://github.com/shoyo44/JanSetu-AI)

JanSetu AI (जनसेतु) is a sovereign AI Document Intelligence, Q&A, and Knowledge Graph Platform designed to analyze, index, search, and reason over unstructured public documents across high-stakes sovereign domains — engineered specifically for **Public Governance** and **Law & Justice** (IndiaAI Mission Priority Domains). A modular prototype validated on live sovereign benchmark suites, JanSetu AI supports data-residency-friendly deployment and air-gapped on-premise execution.

Built with an async **FastAPI** backend, a zero-infrastructure in-process **Hybrid Vector-Graph Database** (NetworkX + FAISS Flat Index), dual cloud/on-premise LLM inference (**Cloudflare Workers AI** & sovereign local **Ollama**), and a responsive **React/Vite** SPA frontend, the system provides calibrated hallucination suppression via empirical abstention, claim-level NLI citation entailment, automated statutory criminal law concordance (IPC $\longleftrightarrow$ BNS), and pre-retrieval indirect prompt injection defense.

> 🚀 **Live Prototype Deployment:** [docs-ai-ashen.vercel.app](https://docs-ai-ashen.vercel.app) *(Hosted on Vercel; source repository: [github.com/shoyo44/JanSetu-AI](https://github.com/shoyo44/JanSetu-AI))*  
> 🏛️ **Fellowship Proposal:** [INDIA_AI_FELLOWSHIP_PROPOSAL.md](./INDIA_AI_FELLOWSHIP_PROPOSAL.md)  
> 📄 **Academic Project Report:** [DOCS_PROJECT_REPORT.pdf](./DOCS_PROJECT_REPORT.pdf)  
> 📐 **System Architecture:** [ARCHITECTURE.md](./ARCHITECTURE.md)  
> 🛡️ **DevSecOps & Security Guide:** [DEVOPS_DEVSECOPS_GUIDE.md](./DEVOPS_DEVSECOPS_GUIDE.md)  
> 📋 **Annotation & Evaluation Protocol:** [eval/annotation_protocol.md](./eval/annotation_protocol.md)  
> 📊 **Per-Query Evaluation Results:** [eval/results/per_query_evaluation_results.csv](./eval/results/per_query_evaluation_results.csv)

---

## 🇮🇳 India AI Fellowship Innovation Highlights

JanSetu AI directly addresses the **Governance** and **Law and Justice** priority focus areas outlined by the Ministry of Electronics and Information Technology (MeitY) and the IndiaAI Mission:

| Feature | Domain | Technical Implementation | Citizen / Institutional Impact |
|---|---|---|---|
| **Jan Suvidha Explainer** | Governance | Multi-facet scheme chunking (Eligibility, Disqualifying Exclusions, DBT Benefits, Documents, Steps) | Translates dense gazettes into plain language with structured eligibility checklists for rural citizens & CSC operators. |
| **Statutory Concordance Engine** | Law & Justice | Bidirectional concordance hash-maps & regex parser (`IPC ⇄ BNS`, `CrPC ⇄ BNSS`, `IEA ⇄ BSA`) | Bridges pre-2024 judicial precedents with modern 2024 criminal codes for judges, prosecutors, and legal aid clinics. Highlights undertrial relief under BNSS §479 and Zero-FIR rights under BNSS §173. |
| **Calibrated Abstention Engine** | Trust & Safety | Per-vertical similarity thresholds ($\tau = 0.40$) with structured refusal explanations | Reduces unsupported answers on absent statutory sections or unmentioned welfare provisions. |
| **NLI Citation Entailment** | Grounding | DeBERTa-v3 cross-encoder Natural Language Inference scoring claim against retrieved chunks | Verifies that factual assertions are strictly entailed by source document text, curbing legal misinformation. |
| **Bilingual Indic Deed Engine** | Land Rights | Zero-dependency Unicode script detector (`0x0B80–0x0BFF`) with key covenant extraction | Verifies Tamil Nadu registered sale deeds (*கிரையப் பத்திரம்*), identifying Survey Numbers (`புல எண்`), 4 boundaries (`நான்கு எல்லைகள்`), and encumbrance covenants. |
| **1-Click Sovereign Benchmarks** | Reproducibility | 7 bundled sovereign scenarios (PM-KISAN, SC Bail Ruling Exemplar, Ayushman Bharat, Tamil Deed, Cyber Zero-FIR, Tenancy Act, Senior Citizens Act) | Enables 1-click evaluation of high-stakes citizen problems directly from the Document Vault UI. |
| **Air-Gapped Sovereign Mode** | Compliance | Offline Ollama daemon (`qwen2.5:7b-instruct`, `nomic-embed-text` 768-dim normalized vectors) | Supports institutional data-residency compliance under Section 16 of the **Digital Personal Data Protection Act (DPDPA), 2023**; sensitive files remain within host infrastructure. |

---

## 🔍 Prior Art & Comparative Landscape

> **Disambiguation Note:** JanSetu AI (जनसेतु) developed under this fellowship is an independent academic research platform focusing on claim-level verification, calibrated abstention, deterministic statutory rule engines, and edge data sovereignty across Governance and Law & Justice. It is distinct from and unrelated to prior work bearing similar titles, including the web portal concept described by Vaishnavi et al. (International Journal of Research Publication and Reviews, Vol. 7, Issue 10, October 2026: *"JanSetu AI: An AI-Assisted Web Platform for Personalised Discovery of Indian Government Welfare Schemes"*) and the lablab.ai hackathon project *"JanSetu — India's Civic AI Assistant"* (submitted May 30, 2026). JanSetu AI's core technical differentiators lie in its unified vector-graph retrieval topology, claim-level DeBERTa-v3 NLI entailment, DPDPA 2023 air-gapped on-premise execution, and deterministic statutory rule engines.

Prior systems address isolated parts of Indian legal informatics and welfare access. JanSetu AI unifies these dimensions under a single sovereign verification layer:

| Dimension | Jugalbandi (AI4Bharat) | Nyaya Setu (GoI/DoJ) | NyayaReasoner | Falkor-IRAC / RAG–KG | LandLens / Commercial | JanSetu AI (Ours) |
|---|---|---|---|---|---|---|
| **Primary Target Users** | Citizens (Welfare) | Citizens (Legal Literacy) | Legal advocates | Legal researchers | Land buyers (TN) | **Citizens, CSCs, legal-aid counsels** |
| **Domain Scope** | Welfare schemes | Legal awareness | SC prediction | Case law, statutes | Land title due diligence | **Welfare + criminal transition + land deeds** |
| **Retrieval Modality** | Dense + FAISS | Conversational API | BM25 + dense + RRF | Graph / hybrid | OCR + AI extraction | **Hybrid (Vector + Graph) + RRF + HyDE** |
| **Claim-Level Entailment** | *Not stated* | *Not stated* | Yes (NLI) | Citation verifier | *Not stated* | **Yes (DeBERTa-v3 cross-encoder NLI)** |
| **Empirical Abstention** | *Not stated* | *Not stated* | Yes | *Not stated* | *Not stated* | **Yes (Calibrated per-vertical τ = 0.40)** |
| **On-Prem / Sovereign Profile**| *Not stated* | *Not stated* | *Not stated* | *Not stated* | *Not stated* | **Yes (Air-gapped data boundary via Ollama)** |
| **Open Evaluation Corpus** | *Not stated* | *Not stated* | *Not stated* | Dataset released | No (Proprietary) | **Committed in repo ($N=150$ gold pairs)** |

*Comparative Notes on Prior Art:*
- **Jugalbandi:** To our knowledge, public technical descriptions do not state provision of criminal statutory concordance, appellate judgment ratio extraction, or air-gapped on-premise deployment.
- **Nyaya Setu (GoI / Bhashini):** National conversational initiative for legal literacy. JanSetu AI is an independent academic research project with zero official affiliation; it contributes an evidence-grounded document verification stack (calibrated abstention, NLI entailment, and DPDPA-compliant local execution).
- **LandLens:** To our knowledge, public descriptions do not disclose evaluation datasets or calibrated abstention metrics.

---

## 🌟 Sovereign Multi-Vertical Matrix (IndiaAI Fellowship Core)

JanSetu AI configures **3 primary sovereign fellowship verticals** in `backend/app/config/verticals.py` (with transparent backward-compatibility aliases for legacy compatibility requests), each featuring an isolated chunking strategy, retrieval modality, reranker, and output generator:

| Primary Vertical Key | Display Name | Chunking (Tokens/Overlap) | Retrieval Modality | Reranker Mechanism | Specialized IndiaAI Capability |
|---|---|---|---|---|---|
| `governance` | **Governance & Welfare** 🏛️ | 500 / 100 | Hybrid (Vector + Graph) | Lexical & Facet Boost | Citizen *Jan Suvidha* plain-language summary, DBT subsidy mapping, eligibility vs disqualifying exclusion separation. |
| `judgment` | **Court Judgments (India)** ⚖️ | 500 / 100 | Hybrid (Vector + Graph) | Statutory Citation Boost | Binding *Ratio Decidendi* extraction, bail precedent synthesis under BNSS §483 / §479, Article 21 constitutional safeguards. |
| `law` | **Statutory Law & Concordance** 📑 | 768 / 128 | Hybrid (Vector + Graph) | `VerticalReranker` (Domain-keyword boost) | Tri-code concordance (`IPC ⇄ BNS`, `CrPC ⇄ BNSS`, `IEA ⇄ BSA`), Regional Land Deeds (*கிரையப் பத்திரம்*), 10-point Red-Flag risk scanner. |

*Note: Legacy vertical aliases (`compliance` $\to$ `law`, `startup` $\to$ `law`, `university` $\to$ `governance`, `hr` $\to$ `governance`) are resolved automatically by the pipeline factory.*

---

## 🏛️ Preloaded Sovereign Benchmark Catalog (7 Bundled Scenarios & Provenance)

JanSetu AI provides a 1-click evaluation catalog in Document Vault (`/api/v1/benchmarks`):

| Benchmark Key | Document Title & Provenance | Vertical | Solved Citizen / Institutional Problem & Caveats |
|---|---|---|---|
| `pm_kisan` | **PM-KISAN Operational Guidelines (Revised 2024)**<br>*(Source: Dept. of Agriculture & Farmers Welfare, GoI; authored benchmark excerpt)* | `governance` | Direct Benefit Transfer (DBT) ₹6,000/yr criteria. Evaluates cultivable landholder eligibility (2019 ceiling removal), "family" definition (husband, wife, minor children), pension exclusions ($\ge ₹10,000$), and mandatory e-KYC/land seeding. |
| `sc_judgment` | **Synthetic Judicial Benchmark Exemplar**<br>*(Source: Authored exemplar modeled on SC jurisprudence)* | `judgment` | Pre-trial bail jurisprudence under BNSS §483 / CrPC §439, triple test condition synthesis, and Article 21 liberty protections. Modeled on Supreme Court bail principles in *Manish Sisodia v. Directorate of Enforcement* (2024 INSC 595, Aug 9, 2024) and *Satender Kumar Antil v. CBI* (2022). |
| `ayushman_bharat` | **Ayushman Bharat PM-JAY Policy Guidelines**<br>*(Source: National Health Authority, GoI)* | `governance` | ₹5 Lakh cashless health cover guarantee, SECC deprivation criteria, and mandatory pre-authorization grievance resolution via NHA 14555. |
| `tamil_pattiram` | **Tamil Nadu Land Sale Deed & Patta (*கிரையப் பத்திரம்*)**<br>*(Source: TN Registration Dept deed format)* | `law` | Bilingual land record verification: Survey Number (`புல எண்`), 4 boundaries (`நான்கு எல்லைகள்`), consideration amount, and Nil-Encumbrance Certificate (`வில்லங்கச் சான்றிதழ்`). |
| `cyber_fir` | **Cyber Fraud & Citizen FIR Guidelines (Helpline 1930 / I4C)**<br>*(Source: I4C / MHA Standard Operating Procedure)* | `law` | Financial fraud reporting, Golden Hour inter-bank freezing via CFCFRMS, Zero-FIR registration under BNSS §173, and cyber cheating remedies under BNS §318(4) read with IT Act §66D. |
| `tenancy_act` | **Model Tenancy Act Guidelines (MoHUA)**<br>*(Source: Ministry of Housing & Urban Affairs framework)* | `law` | 2-month residential security deposit ceiling (Section 11), statutory rule requiring at least 24-hr advance notice prior to inspection/entry, and Rent Authority dispute redressal. *(Caveat: Model law requiring state enactment; Karnataka operates under Karnataka Rent Act, 1999).* |
| `senior_citizen` | **Senior Citizens Parental Protection Act (MWPSC Act 2007 §23)**<br>*(Source: Ministry of Social Justice & Empowerment)* | `law` | Section 23 voidance of conditional property gift deeds before Maintenance Tribunal. *(Judicial caveat: Under SC ruling in Sudesh Chhikara (2022), maintenance obligation must be an express or integral covenant of the transfer).* |

---

## 🇮🇳 Bilingual Indic Land Administration & Deed Verification Engine

JanSetu AI includes native support for regional Indian land records and registered sale deeds (*கிரையப் பத்திரம், பட்டா, சிட்டா*):
- **Zero-Dependency Unicode Script Detector:** Detects Tamil script range (`0x0B80–0x0BFF`) and other Indic scripts.
- **Key Covenant Extraction:** Automatically identifies and parses:
  - Survey Number (`புல எண்`) & Sub-division (`உட்பிரிவு`)
  - Extent of Land (`பரப்பளவு` in Ares, Cents, or Sq. Ft.)
  - Four Boundaries (`நான்கு எல்லைகள்`: North, South, East, West)
  - Encumbrance Certificate status (`வில்லங்கச் சான்றிதழ்`)
  - Consideration Amount & Sub-Registrar Office parameters
- **Bilingual Citizen Summary (*Jan Suvidha*):** Provides rural land buyers and legal aid clinics with a clear plain-language breakdown of rights, risks, and boundary integrity.
- **Cross-Encoder Note:** Claim entailment scoring via `cross-encoder/nli-deberta-v3-small` is English-primary. Indic texts are evaluated via citation span grounding and lexical verification, with native Indic NLI models (such as MuRIL / IndicBERT) planned for Q2.

---

## ⚡ Zero-Infrastructure In-Process Hybrid Store

Replaces heavy external database infrastructure (Neo4j, Milvus, Pinecone) with an embedded, zero-dependency in-process engine:

- **NetworkX Topology:** Manages hierarchical document structures (`TenantNode` $\rightarrow$ `DocumentNode` $\rightarrow$ `ChunkNode`), sequential reading chains (`NEXT_CHUNK`), and semantic entity linkages (`MENTIONS`, `CITES`, `SUPERSEDES`). Suited for up to 50,000 document nodes per instance; HNSW and DuckDB migration planned on roadmap for 250,000+ nodes.
- **FAISS Vector Acceleration:** Embeds text chunks into a 768-dimensional normalized continuous space (`nomic-embed-text-v1.5` in cloud mode; `nomic-embed-text` in local Ollama) for high-speed inner-product cosine similarity retrieval.
- **Vector Model Incommensurability Note:** Embeddings from different models inhabit different latent spaces. Switching between cloud and local Ollama requires re-indexing the document corpus. The hash router in `embedding_router.py` is strictly an offline unit-test mock fixture.
- **Re-Entrant RWLock Safety:** Regulates multi-threaded concurrency — allows unlimited parallel reads during search queries while serializing atomic background disk write-backs to `graph_store.json`.
- **SQLite Semantic Cache:** Fast retrieval ($\approx 3.8\text{ ms}$) for repeated queries with cosine similarity $\ge 0.95$.

---

## 🛡️ Platform Security, Privacy & DevSecOps

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 API Gateway / Rate Limiter              │
                  │        (Sliding Window: 20 uploads/hr, 150 queries/hr)  │
                  └───────────────────────────┬────────────────────────────┘
                                              │
                         ┌────────────────────┴────────────────────┐
                         ▼                                         ▼
            ┌──────────────────────────┐              ┌──────────────────────────┐
            │ Magic-Byte MIME Inspector │              │ Input Guardrails / Regex │
            │  (%PDF-, PK\x03\x04;      │              │ (Block system override,  │
            │   Block MZ/ELF Executables)│              │  toxic payloads, XSS)    │
            └────────────┬─────────────┘              └────────────┬─────────────┘
                         │                                         │
                         ▼                                         │
            ┌──────────────────────────┐                           │
            │ Indirect Injection Scanner│                           │
            │ (Strip Unicode Stego,    │                           │
            │  Quarantine Jailbreaks)  │                           │
            └────────────┬─────────────┘                           │
                         │                                         │
           Safe Chunks   │   Quarantine Chunks                     │
                 ┌───────┴───────┐                                 │
                 ▼               ▼                                 │
          ┌─────────────┐ ┌─────────────┐                          │
          │ FAISS Index │ │ Graph Alert │                          │
          │ (Searchable)│ │(Quarantined)│                          │
          └──────┬──────┘ └─────────────┘                          │
                 │                                                 │
                 └────────────────────────────┬────────────────────┘
                                              │
                                              ▼
                               ┌─────────────────────────────┐
                               │ Sovereign Ollama / CF LLM   │
                               │ (DPDPA 2023 Data Residency) │
                               └─────────────────────────────┘
```

1. **Pre-Indexing Indirect Prompt Injection Scanner (`doc_injection_scanner.py`):** Scans for adversarial jailbreaks, role impersonation delimiters (`<|im_start|>`), and zero-width unicode steganography. Quarantines suspicious chunks before vector indexing.
2. **Binary Magic-Byte File Validation (`file_validator.py`):** Inspects raw file headers to confirm genuine MIME signatures; outright blocks executable binaries (Windows PE `MZ`, Linux ELF `\x7fELF`), double extensions (e.g., `policy.pdf.exe`), and files $>50\text{ MB}$.
3. **Tenant Sliding-Window Rate Limiting (`rate_limiter.py`):** Enforces per-tenant quotas (20 uploads/hr, 150 queries/hr) with HTTP 429 Retry-After headers.
4. **On-Premise Sovereign Execution (`ollama_client.py`):** Supports offline, air-gapped LLM and embedding inference via local Ollama daemons, supporting data residency compliance under Section 16 of India's **Digital Personal Data Protection Act (DPDPA), 2023**.
5. **Multi-Stage Container Hardening:** Multi-stage Docker builds running under an unprivileged non-root user (`docqa:10001`) with Indic OCR language packs (`hin`, `tam`).
6. **Automated DevSecOps Pipeline (`.github/workflows/ci.yml`):** Enforces static linting (Ruff), Python security scanning with **Bandit (SAST)**, dependency vulnerability auditing with **pip-audit** & **npm audit**, and container image vulnerability scanning via **Trivy**.

---

## 📊 Quantitative Benchmarks & Evaluation

To ensure scientific credibility, JanSetu AI separates software integration tests from statistical retrieval quality measurements:

### A. Software & Functional Integration Tests (Pass/Fail)
Tested via automated test suites (`eval/test_live_e2e_full_system.py`, `eval/test_frontend_chromium.py`):

| Test Suite | Result | Scope / Coverage |
|---|---|---|
| **Live Backend E2E Test Suite** | **16/16 PASS (100.0%)** | Full-system validation: Health check, Concordance API, 1-Click Benchmark Ingestion, Ingested Document List, Chunk API, Governance RAG, Judgment RAG, Calibrated Abstention, Knowledge Graph Topology, Active Learning Feedback, Magic-Byte File Validation, Prompt Injection Quarantine, HTML/MD Audit Export. |
| **Playwright Chromium E2E Suite**| **7/7 PASS (100.0%)** | Automated headless Chrome testing: Landing, Auth, Concordance Modal, Document Vault, Analytics KG, Multi-Vertical Selection, and History. |
| **Undertrial Rule Engine Test (BNSS §479)** | **5/5 PASS (100.0%)** | Validates 1/3rd first offender, 1/2 repeat offender, life/death exclusion, multiple case exclusion, and judicial review recommendation (`eval/test_undertrial_rules.py`). |
| **Statutory Concordance Fixture**| **30/30 PASS (100.0%)** | Deterministic unit verification on curated benchmark set of statutory transitions. |
| **Adversarial Injection Fixture** | **10/10 PASS (100.0%)** | Quarantines 10 synthetic jailbreak/steganography chunks before vector indexing. |

### B. Statistical Retrieval & QA Defensibility Evaluation ($N = 120$)
Evaluated over $N = 120$ annotated answerable query-document pairs spanning Central/State Gazettes (40), Statutory Enactments (40), and Appellate Rulings (40), alongside a separate held-out set of $N = 30$ unanswerable queries (10 per vertical). Gold answers were annotated by two independent legal and public administration researchers (Cohen's $\kappa = 0.88$). Refusal threshold $\tau = 0.40$ was tuned on a separate 20-query dev split. Raw per-query evaluation results are committed and tracked in [`eval/results/per_query_evaluation_results.csv`](./eval/results/per_query_evaluation_results.csv).

All proportions report exact counts $k/N$ with 95% Wilson score confidence intervals. Entailment reports mean $\pm$ standard error.

| Evaluation Metric | Naive RAG Baseline | Advanced GraphRAG | JanSetu AI Grounded (Cloud Mode) | JanSetu AI Sovereign (On-Premise) | Metric Definition / Context |
|---|---|---|---|---|---|
| **Top-5 Context Recall** | 85/120 (**70.8%**)<br>[62.2%, 78.2%] | 102/120 (**85.0%**)<br>[77.5%, 90.3%] | 111/120 (**92.5%**)<br>[86.4%, 96.0%] | 106/120 (**88.3%**)<br>[81.4%, 92.9%] | Ground-truth statutory clause or welfare criterion present in top-5 retrieved chunks ($N=120$). |
| **Calibrated Refusal Accuracy** | 12/30 (**40.0%**)<br>[24.6%, 57.7%] | 19/30 (**63.3%**)<br>[45.5%, 78.1%] | 28/30 (**93.3%**)<br>[78.7%, 98.2%] | 27/30 (**90.0%**)<br>[74.4%, 96.5%] | Correctly abstains on $N=30$ held-out unanswerable queries ($\tau = 0.40$ cloud, $\tau = 0.38$ on-prem). |
| **Citation Entailment (NLI)** | 0.52 ± 0.06 | 0.69 ± 0.05 | **0.88 ± 0.03** | **0.84 ± 0.04** | Mean claim-level entailment score using `cross-encoder/nli-deberta-v3-small` across 111 grounded answers. |
| **Semantic Cache Hit Latency (p95)**| N/A | N/A | **3.8 ms** | **3.8 ms** | In-memory SQLite cosine similarity hit ($\ge 0.95$). |
| **Vector Search Latency (p95)** | 450 ms | 720 ms | **680 ms** | **740 ms** | Single-pass FAISS query over 768-dim space. |
| **Hybrid + HyDE Latency (p95)** | N/A | 1,850 ms | **1,620 ms** | **2,100 ms** | Vector + Graph retrieval + HyDE query expansion. |
| **End-to-End Synthesis Latency (p95)**| 850 ms | 1,750 ms | **2,150 ms** | **2,850 ms** | Complete pipeline: Retrieval + Cross-Encoder + NLI verification + LLM generation (measured on RTX 3060 edge rig for on-prem). |

#### Evaluation Protocol & Gold Dataset
- **Gold Question Set:** [`eval/gold/sovereign_benchmark_qa.jsonl`](./eval/gold/sovereign_benchmark_qa.jsonl) (120 answerable + 30 held-out unanswerable queries).
- **Per-Query Binary Hits:** [`eval/results/per_query_evaluation_results.csv`](./eval/results/per_query_evaluation_results.csv).
- **Annotation Methodology:** Two independent legal and public administration researchers annotated gold citations. Inter-annotator agreement achieved Cohen's $\kappa = 0.88$.
- **Edge Benchmark Hardware:** AMD Ryzen 7 5700X (8 cores / 16 threads), 32 GB RAM, NVIDIA GeForce RTX 3060 (12 GB VRAM). Local models: `qwen2.5:7b-instruct` (4-bit quantized) and `nomic-embed-text` via Ollama.

---

## 🛠️ Environment Setup & Quickstart

### Prerequisites
- Python 3.10+ (Recommended: Python 3.11)
- Node.js 18+ & npm
- (Optional) Docker & Docker Compose
- (Optional) Ollama for air-gapped sovereign execution (`ollama pull qwen2.5:7b-instruct`, `ollama pull nomic-embed-text`)

### 1. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

Key variables:
```env
# Cloudflare Workers AI (Cloud Mode)
CF_ACCOUNT_ID=your_cloudflare_account_id
CF_API_TOKEN=your_cloudflare_api_token

# Sovereign On-Premise Execution (Local Mode - DPDPA 2023)
USE_OLLAMA=false
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b-instruct

# In-Process & Fallback Storage
MONGODB_URI=your_mongodb_connection_string
ENABLE_JSON_FALLBACK=true

# Security & Rate Limiting
RATE_LIMIT_UPLOADS_PER_HOUR=20
RATE_LIMIT_QUERIES_PER_HOUR=150
MAX_UPLOAD_SIZE_MB=50
```

### 2. Backend Server Execution
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload --reload-dir app
```

### 3. Frontend Web Client Execution
```powershell
cd frontend
npm install
npm run dev
```
*Access the application at `http://localhost:5173/`.*

### 4. Running via Docker Compose
To run the complete production-hardened multi-container stack:
```powershell
docker-compose up --build
```
To run with local sovereign Ollama enabled:
```powershell
docker-compose --profile onprem up --build
```

---

## 🧪 Automated Testing & DevSecOps Validation

Run the comprehensive evaluation harness:
```powershell
# Set Python path
$env:PYTHONPATH="backend"

# Run the 100% Pass Live Backend End-to-End Suite (16/16 tests)
python eval/test_live_e2e_full_system.py

# Run Playwright Chromium Headless UI Suite (7/7 tests)
python eval/test_frontend_chromium.py

# Run India AI Fellowship feature verification
python eval/test_india_ai_features.py

# Run Security, Rate Limiter & Magic Byte tests
python eval/test_phase4_security.py

# Run Full Defensibility Benchmark Suite
python eval/run.py
```

Run DevSecOps Static Analysis & Vulnerability Scans:
```powershell
# Static Application Security Testing (Bandit SAST)
bandit -r backend/app -c pyproject.toml

# Dependency Vulnerability Audit
pip-audit

# Frontend Dependency Audit
cd frontend; npm audit; cd ..
```

---

## 📦 System Component Summary

| Component | Technology | Role & Purpose |
|---|---|---|
| **Frontend SPA** | React 18, Vite, Lucide Icons, ForceGraph2D | Glassmorphism UI, Jan Suvidha Card, IPC ⇄ BNS Modal, Graph Visualizer |
| **Voice Interface** | Browser Web Speech API | Client-assisted speech-to-text input (desktop convenience; local Whisper roadmap for air-gapped on-prem) |
| **API Gateway** | FastAPI, Pydantic V2, Starlette | High-performance async REST & WebSocket streaming endpoints |
| **Graph Store** | NetworkX (in-process) | Hierarchical document topology & entity linkage (up to 50k nodes; HNSW roadmap for 250k) |
| **Vector Engine** | FAISS Flat Index (768-dim) | Inner-product cosine similarity semantic search |
| **Embedding Router** | Nomic Atlas / Local Ollama Nomic | 768-dimensional normalized dense vectors with Indic script detection |
| **Concordance Engine**| Statutory Hashmaps & Regex | Real-time bidirectional mapping (IPC ⇄ BNS, CrPC ⇄ BNSS, IEA ⇄ BSA) |
| **Abstention Engine** | Calibrated Similarity Thresholds | Selective refusal on low-confidence/absent document contexts ($\tau = 0.40$) |
| **Citation Verifier** | Cross-Encoder NLI | DeBERTa-v3 claim-to-chunk entailment verification |
| **Injection Defense**| Regex / Unicode Steganography Filter | Pre-indexing quarantine of adversarial prompts |
| **Sovereign Engine** | Ollama (`qwen2.5:7b-instruct`) | Local air-gapped inference adhering to DPDPA 2023 Section 16 |
| **Containerization** | Docker, Nginx, Docker Compose | Non-root (`docqa:10001`) multi-stage deployment |

---

## 📜 Citation & Fellowship Submission

```bibtex
@misc{jansetu2024,
  author = {Dhanush S},
  title = {JanSetu AI: Sovereign Multi-Vertical Agentic Knowledge Graph & RAG Platform for Public Governance and Citizen Welfare},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/shoyo44/JanSetu-AI}}
}
```

*Developed for the **IndiaAI Mission Fellowship Program** under the priority domains of **Governance** and **Law & Justice**.*
