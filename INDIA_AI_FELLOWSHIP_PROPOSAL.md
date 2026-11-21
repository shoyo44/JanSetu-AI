# IndiaAI Fellowship Project Proposal Dossier

**Project Title:** JanSetu AI: Sovereign Agentic Knowledge Graph & RAG Platform for Public Governance & Citizen Welfare  
**Applicant Name:** Dhanush S  
**Institution:** Department of Computer Science and Engineering, Kalasalingam Academy of Research and Education (Deemed University), Tamil Nadu, India  
**Primary Domain (Portal Choice):** Governance *(Cross-cutting with Law and Justice)*  
**Repository:** [github.com/shoyo44/JanSetu-AI](https://github.com/shoyo44/JanSetu-AI)  
**Target Fellowship:** IndiaAI Mission — Graduate / Research Scholar AI Fellowship (Ministry of Electronics and Information Technology, MeitY)  

---

## 1. Executive Summary & Abstract

India faces an immense dual bottleneck at the intersection of public administration and justice delivery: over 4.4–5.1 crore pending court cases (source: National Judicial Data Grid, NJDG 2024), alongside a severe information asymmetry preventing common citizens from claiming statutory rights and direct welfare entitlements. Vulnerable populations face recurring exploitation: cyber fraud victims lose critical hours before filing complaints; urban tenants are trapped by excessive deposit demands; senior citizens face property abandonment by kin; rural land buyers suffer from unverified vernacular sale deeds; and eligible farmers and families miss out on Central Direct Benefit Transfer (DBT) and healthcare schemes (*PM-KISAN, Ayushman Bharat PM-JAY*).

**JanSetu AI** (जनसेतु) is a sovereign, verifiable agentic RAG and knowledge graph platform supporting air-gapped deployment, engineered specifically for the Indian public sector. In the **Governance** domain, JanSetu AI ingests Central/State Gazettes and policy guidelines, utilizing a custom facet chunker and our citizen-first *Jan Suvidha* engine to translate dense administrative notifications into plain-language eligibility cards, document checklists, and DBT subsidy maps. In the **Law and Justice** domain, JanSetu AI synthesizes appellate court judgments (extracting binding *Ratio Decidendi*) and features an automated **Statutory Concordance Engine** bridging colonial criminal codes with India's July 1, 2024 enactments (`IPC ⇄ BNS`, `CrPC ⇄ BNSS`, `IEA ⇄ BSA`), with specialized logic for undertrial detention relief (BNSS §479 / CrPC §436A) and mandatory Zero-FIR registration (BNSS §173).

Crucially, JanSetu AI significantly curtails ungrounded hallucinations through an empirical **Calibrated Abstention Engine** ($\tau = 0.40$) and claim-level **DeBERTa-v3 NLI Citation Entailment** verification. The architecture is sovereign and zero-infrastructure: an in-process NetworkX topology paired with a 768-dimensional FAISS index, with optional 100% offline edge execution via Ollama (`qwen2.5:7b-instruct`, `nomic-embed-text` 768-dim) supporting institutional data residency mandates under Section 16 of the *Digital Personal Data Protection Act (DPDPA), 2023*. Evaluated on an automated live test harness, JanSetu AI achieves **100% pass rate across 16 software integration tests**, 111/120 (**92.5%** [95% CI: 86.4%, 96.0%]) context recall@5, and 28/30 (**93.3%** [95% CI: 78.7%, 98.2%]) calibrated refusal accuracy.

---

## 2. Problem Statement & National Importance

### A. The Governance Divide & Welfare Benefit Exclusion
The Government of India disburses hundreds of billions of rupees annually across DBT schemes. However, smallholder farmers, informal workers, and rural households are frequently excluded due to impenetrable bureaucratic guidelines. Common Service Center (CSC) operators and Village Administrative Officers (VAOs) lack real-time intelligent aids to evaluate nuanced statutory exclusions (e.g., institutional landownership, income tax payee status, pension ceilings $\ge ₹10,000$) versus raw landholding criteria.

### B. The Criminal Jurisprudence Transition Challenge (July 1, 2024)
With the enforcement of the *Bharatiya Nyaya Sanhita (BNS)*, *Bharatiya Nagarik Suraksha Sanhita (BNSS)*, and *Bharatiya Sakshya Adhiniyam (BSA)* on July 1, 2024, the Indian legal ecosystem faces its largest legislative transition since Independence. Under Section 358 BNS and Section 531 BNSS, pending investigations and past offences remain governed by colonial statutes, while fresh FIRs invoke modern codes. Legal aid counsels, police station house officers (SHOs), and subordinate judiciary lack automated bidirectional concordance systems to map historical precedents (e.g., *Arnesh Kumar*, *Satender Kumar Antil*) to new procedural sections. Furthermore, with undertrial inmates constituting 77.1% of India's prison population (NCRB Prison Statistics India 2021; 75.8% in PSI 2022), automated identification of bail and detention relief under **BNSS §479 (relaxing detention limits to one-third for first-time offenders)** is of paramount national importance.

### C. Critical Real-World Citizen Vulnerabilities Addressed by JanSetu AI
1. **Cyber Financial Fraud & Golden Hour Freezing (Helpline 1930 / I4C):** Citizens losing funds to UPI/phishing scams often miss the critical 2-hour "Golden Hour" needed for inter-bank liens via CFCFRMS. JanSetu AI provides immediate operational guidance: immediate 1930 reporting triage, transaction ID harvesting, and mandatory Zero-FIR drafting under **BNSS §173 / BNS §318(4)** (general cheating applied to cyber fraud, read with Information Technology Act §66D).
2. **Urban Tenancy Exploitation & Deposit Ceilings:** Urban migrant workers and students face arbitrary 6–10 month security deposit demands and unannounced lockouts. JanSetu AI interprets the **Model Tenancy Act (MoHUA)**, asserting the statutory 2-month residential security deposit ceiling (Section 11), statutory rule requiring at least 24 hours' written advance notice prior to landlord entry/inspection, and Rent Authority dispute mechanisms. *(Caveat: As land/tenancy falls under State List Entry 18, the Model Tenancy Act is a model framework for state adoption; states such as Karnataka currently operate under state acts like the Karnataka Rent Act, 1999).*
3. **Elder Care & Property Protection (MWPSC Act 2007 §23):** Senior citizens transferring ancestral property to adult children under promises of care are often evicted once title deeds are registered. JanSetu AI guides senior citizens through Section 23 of the *Maintenance and Welfare of Parents and Senior Citizens Act*, explaining the statutory procedure to declare conditional gifts void before the Maintenance Tribunal. *(Judicial caveat: Under the Supreme Court's landmark ruling in Sudesh Chhikara v. Ramti Devi (2022), the condition to provide maintenance must be an express covenant in the deed or an established integral condition of the transfer).*
4. **Vernacular Land Title Fraud & Boundary Disputes:** Rural land transactions in Tamil Nadu rely on regional language registered deeds (*கிரையப் பத்திரம், பட்டா, சிट्टा*). Ambiguous four-boundary recitals (*நான்கு எல்லைகள்*), missing Survey/Sub-division numbers (`புல எண்`), and unregistered encumbrances result in multi-decade civil litigation. JanSetu AI provides automated bilingual Indic deed analysis and title verification.

### D. Flagship Operational Use Cases with Measurable Outcomes
Rather than presenting disjointed prototypes, JanSetu AI concentrates evaluation on two measurable flagship operational pipelines:
1. **Undertrial Detention Relief Screener (BNSS §479 / CrPC §436A):**
   - *Problem:* 75.8%–77.1% of India's prison population consists of undertrials (NCRB PSI 2021/2022). Legal aid advocates must manually scour hundreds of docket pages to determine if an inmate has served one-third (first-time offender) or one-half of the maximum statutory sentence.
   - *Measurable Outcome:* We hypothesize and target a reduction in pre-screening review time from an estimated manual legal-aid docket intake baseline of ~45 minutes to < 2.5 minutes of automated pre-screening, to be empirically evaluated during the Q3 pilot. The screener applies verified statutory rule logic (unit-tested 5/5 PASS in `eval/test_undertrial_rules.py`; end-to-end docket screening accuracy to be evaluated in the Q3 pilot) evaluating eligibility for judicial review under Section 479 of the Bharatiya Nagarik Suraksha Sanhita (BNSS), incorporating the 1/3rd detention threshold for first-time offenders, the 1/2 threshold for repeat offenders, and explicit statutory disqualification checks (second proviso excluding offences punishable by death or life imprisonment, and third proviso excluding persons with multiple pending investigations/trials), outputting an advisory recommendation for judicial review rather than mandatory release, with a strict human-in-the-loop legal aid safeguard.
2. **Citizen Welfare Disqualification & Exclusion Filter (PM-KISAN / Ayushman Bharat):**
   - *Problem:* Rural applicants face benefit rejection without understanding disqualification clauses (institutional land, pension $\ge ₹10,000$, non-updated e-KYC).
   - *Measurable Outcome:* We hypothesize and target a reduction in eligibility false-negatives and citizen application cycle times, providing a structured 5-point *Jan Suvidha* checklist that highlights prerequisite gaps prior to formal submission, with empirical error reduction to be measured during Q3 CSC pilot trials.

### E. Prior Art, Related Work & Comparative Landscape

> **Disambiguation Note:** JanSetu AI (जनसेतु) developed under this fellowship is an independent academic research platform focusing on claim-level verification, calibrated abstention, deterministic statutory rule engines, and edge data sovereignty across Governance and Law & Justice. It is distinct from and unrelated to prior work bearing similar titles, including the web portal concept described by Vaishnavi et al. (International Journal of Research Publication and Reviews, Vol. 7, Issue 10, October 2026: *"JanSetu AI: An AI-Assisted Web Platform for Personalised Discovery of Indian Government Welfare Schemes"*) and the lablab.ai hackathon project *"JanSetu — India's Civic AI Assistant"* (submitted May 30, 2026). JanSetu AI's core technical differentiators lie in its unified vector-graph retrieval topology, claim-level DeBERTa-v3 NLI entailment, DPDPA 2023 air-gapped on-premise execution, and deterministic statutory rule engines.

Prior efforts address isolated dimensions of public governance and Indian legal informatics:
* **Jugalbandi (OpenNyAI, AI4Bharat, Microsoft):** Pioneers multilingual voice and text queries for welfare schemes over WhatsApp, later integrated with Bhashini. To our knowledge, public technical descriptions do not state provision of criminal statutory concordance, appellate judgment ratio extraction, or air-gapped on-premise deployment.
* **Nyaya Setu (Department of Justice / Bhashini, GoI):** A voice-first, multilingual conversational citizen legal literacy bot launched under the national Digital India initiative. JanSetu AI is an independent academic research project with no institutional connection to Nyaya Setu. While public descriptions of Nyaya Setu indicate an emphasis on conversational citizen legal literacy, JanSetu AI contributes a document-level verification layer: multi-tier NLI citation entailment, calibrated empirical abstention (τ = 0.40), statutory criminal concordance rule engines (BNSS §479 undertrial review), and an air-gapped on-premise deployment profile ensuring institutional data residency under Section 16 of DPDPA 2023.
* **NyayaReasoner:** Combines hybrid BM25 and dense retrieval with claim verification for Supreme Court judgment prediction, focusing specifically on judicial outcomes rather than citizen welfare or regional land administration.
* **Falkor-IRAC / RAG–KG Architectures:** Utilize knowledge graphs for statutory grounding and legal research.
* **LandLens & Commercial Tools:** Target isolated private verticals (such as Tamil Nadu land due diligence or IPC ↔ BNS lookup) behind proprietary subscription paywalls. To our knowledge, public descriptions do not disclose evaluation datasets or calibrated abstention metrics.

JanSetu AI does not claim to supersede these specialized systems; rather, it contributes:
1. A **unified open platform** applying the same multi-layered verification stack (calibrated abstention τ = 0.40, claim-level NLI entailment, pre-indexing injection defense) across public governance, criminal law transition, and vernacular land deeds.
2. A **documented sovereign on-premise profile** with explicit data-flow boundaries complying with Section 16 of DPDPA 2023.
3. A **reproducible open gold benchmark corpus** ($N = 120 + 30$ pairs) with committed exact binary counts, Wilson score confidence intervals, and inter-annotator agreement metrics.

| Dimension | Jugalbandi (AI4Bharat) | Nyaya Setu (GoI/DoJ) | NyayaReasoner | Falkor-IRAC / RAG–KG | LandLens / Commercial | JanSetu AI (Ours) |
|---|---|---|---|---|---|---|
| **Primary Target Users** | Citizens (Welfare) | Citizens (Legal Literacy) | Legal advocates | Legal researchers | Land buyers (TN) | **Citizens, CSCs, legal-aid counsels** |
| **Domain Scope** | Welfare schemes | Legal awareness | SC prediction | Case law, statutes | Land title due diligence | **Welfare + criminal transition + land deeds** |
| **Retrieval Modality** | Dense + FAISS | Conversational API | BM25 + dense + RRF | Graph / hybrid | OCR + AI extraction | **Hybrid (Vector + Graph) + RRF + HyDE** |
| **Claim-Level Entailment** | *Not stated* | *Not stated* | Yes (NLI) | Citation verifier | *Not stated* | **Yes (DeBERTa-v3 cross-encoder NLI)** |
| **Empirical Abstention** | *Not stated* | *Not stated* | Yes | *Not stated* | *Not stated* | **Yes (Calibrated per-vertical τ = 0.40)** |
| **On-Prem / Sovereign Profile**| *Not stated* | *Not stated* | *Not stated* | *Not stated* | *Not stated* | **Yes (Air-gapped data boundary via Ollama)** |
| **Open Evaluation Corpus** | *Not stated* | *Not stated* | *Not stated* | Dataset released | No (Proprietary) | **Committed in repo ($N=150$ gold pairs)** |

### F. Theory of Change Framework
```
[Societal Bottleneck]
4.4–5.1 Cr Pending Court Cases · 75.8% Undertrial Population · Bureaucratic Welfare Exclusion
       │
       ▼
[Target Beneficiaries]
Rural Citizens · CSC Operators / VLEs · DLSA Legal Aid Counsels · Subordinate Courts
       │
       ▼
[JanSetu AI Sovereign Intervention]
Jan Suvidha Plain-Language Explainer + BNSS §479 Pre-screener + Bilingual Indic Deed Parser
Zero-Infrastructure Hybrid Graph-Vector Store + Calibrated Abstention (tau = 0.40) + NLI Entailment
       │
       ▼
[Empirical Pilot Validation (Q3)]
N = 15 CSC Operators & Legal Aid Counsels · Measuring Task Completion Time & System Usability Scale (SUS)
       │
       ▼
[Long-Term DPI Impact]
Open-Source Reference Architecture & Benchmark Datasets contributed to IndiaAI Datasets Platform
```

---

## 3. Technical Architecture & System Innovation

```mermaid
flowchart TD
    subgraph S1["1. Multi-Format Ingestion & Threat Defense"]
        DOC["Public Gazettes / Deeds / Judgments / Circulars\n(PDF, DOCX, TXT - Magic-Byte Verified)"]
        INJ["Pre-Indexing Indirect Injection Scanner\n(Strip Stego, Quarantine Adversarial Delimiters)"]
        OCR["5-Tier Indic Multimodal OCR Cascade\n(PyMuPDF ➔ Tesseract ➔ Textract ➔ OCR.space ➔ Vision)"]
    end

    subgraph S2["2. In-Process Sovereign Knowledge Engine"]
        ROUTER["Multilingual 768-dim Embedding Router\n(Cloud: Nomic v1.5 API | On-Prem: Ollama Nomic 768-dim)"]
        GRAPH["In-Process NetworkX Graph Database\n(Tenant ➔ Document ➔ Chunk Topology & CITES Edges)"]
        FAISS["FAISS Flat Index (IndexFlatIP, 768-dim)\n(Cosine Normalized Vector Space)"]
    end

    subgraph S3["3. Hybrid Retrieval & Defensibility Layer"]
        HYB["Hybrid Reciprocal Rank Fusion (RRF)\n(Dense Vector + In-Process Graph Traversal)"]
        RERANK["Multi-Vertical Reranker\n(Domain Lexical Boost + Citation Scoring)"]
        ABSTAIN["Calibrated Abstention Engine (tau = 0.40)\n(Safely Refuses Unanswerable Queries)"]
        NLI["DeBERTa-v3 Cross-Encoder NLI\n(Claim-to-Chunk Entailment Verification)"]
    end

    subgraph S4["4. Sovereign Citizen & Judicial Applications"]
        CONC["Statutory Concordance Engine\n(IPC ⇄ BNS, CrPC ⇄ BNSS, IEA ⇄ BSA)"]
        DEED["Bilingual Indic Deed Analyzer\n(Tamil Survey No, 4 Boundaries, Encumbrance)"]
        JAN["Jan Suvidha Citizen Explainer\n(Plain-Language Cards, DBT Maps, Legal Aid)"]
        SOV["Sovereign On-Premise Execution\n(Local Ollama Qwen2.5 - DPDPA 2023 Sec 16)"]
    end

    DOC --> INJ --> OCR --> ROUTER
    ROUTER --> GRAPH & FAISS
    GRAPH & FAISS --> HYB --> RERANK --> ABSTAIN --> NLI
    NLI --> CONC & DEED & JAN
    JAN & CONC & DEED -.-> SOV
```

### Key Technical Contributions:
1. **Calibrated Abstention Engine ($\tau = 0.40$):** Reduces unsupported answers by establishing per-vertical empirical similarity thresholds calibrated on normalized `nomic-embed-text-v1.5` embeddings. Queries lacking sufficient source evidence trigger structured refusal explanations rather than fabrication.
2. **Claim-Level NLI Entailment Verification:** Uses `cross-encoder/nli-deberta-v3-small` to compute directional entailment between each generated factual assertion and retrieved source chunks, assigning verification badges. *(English primary; Indic texts evaluated via citation span grounding and lexical verification, with native Indic NLI planned for Q2).*
3. **Tri-Code Statutory Concordance Engine:** Real-time bidirectional mapping across IPC $\longleftrightarrow$ BNS, CrPC $\longleftrightarrow$ BNSS, and IEA $\longleftrightarrow$ BSA, with proactive highlighting of procedural rights (undertrial bail under BNSS §479; Zero-FIR under BNSS §173).
4. **Bilingual Indic Land Deed Verification Engine:** Zero-dependency Unicode script detector identifying Tamil characters (`0x0B80–0x0BFF`) and extracting survey numbers, four boundaries, consideration, and encumbrance covenants.
5. **Data Sovereignty Architecture (DPDPA 2023):** Dual-mode runtime allowing instant toggle between Cloudflare Workers AI and an entirely offline local Ollama daemon (`qwen2.5:7b-instruct`, `nomic-embed-text` 768-dim), keeping sensitive records within institutional borders. *(Note: Vectors across models are incommensurable; switching modes requires corpus re-indexing).*
6. **Pre-Indexing Threat Defense:** Binary magic-byte validation (`%PDF-`, `PK\x03\x04`) and indirect prompt injection scanner isolating adversarial prompts before vector indexing.

---

## 4. IndiaAI Mission Pillar Alignment

JanSetu AI aligns directly with 3 official pillars established by the Ministry of Electronics and Information Technology (MeitY):

| Official IndiaAI Mission Pillar | JanSetu AI Implementation & National Relevance |
|---|---|
| **IndiaAI Application Development Initiative** | High-impact citizen application deployed across Public Governance, Law & Justice, and Vernacular Land Administration. |
| **IndiaAI Datasets Platform** | Standardized ingestion of Central/State Gazettes, Supreme Court judgments, and Tamil land deeds; committing to contribute our verified $N=150$ gold benchmark dataset (`eval/gold/sovereign_benchmark_qa.jsonl`) to the national repository. |
| **Safe & Trusted AI** | Calibrated refusal engine ($\tau = 0.40$), claim-level NLI verification, pre-indexing injection quarantine, and sliding-window rate limiting. |

*(Note: JanSetu AI is engineered for compute efficiency and runs on IndiaAI sovereign cloud compute or local edge workstations, without claiming the separate Startup Financing pillar).*

---

## 5. Quantitative Evaluation & Benchmark Results

To avoid conflating software unit tests with statistical retrieval quality, JanSetu AI separates its evaluation into two distinct categories:

### A. Software & Functional Integration Tests (Pass/Fail)
Evaluated on our automated live test harness (`eval/test_live_e2e_full_system.py`, `eval/test_frontend_chromium.py`):

| Test Suite | Result | Scope / Coverage |
|---|---|---|
| **Live Backend E2E Test Suite** | **16/16 PASS (100.0%)** | Full-system validation: Health check, Concordance API, 1-Click Benchmark Ingestion, Ingested Document List, Chunk API, Governance RAG, Judgment RAG, Calibrated Abstention, Knowledge Graph Topology, Active Learning Feedback, Magic-Byte File Validation, Prompt Injection Quarantine, HTML/MD Audit Export. |
| **Playwright Chromium E2E Suite**| **7/7 PASS (100.0%)** | Automated headless Chrome testing: Landing, Auth, Concordance Modal, Document Vault, Analytics KG, Multi-Vertical Selection, and History. |
| **Undertrial Rule Engine Test (BNSS §479)** | **5/5 PASS (100.0%)** | Validates 1/3rd first offender, 1/2 repeat offender, life/death exclusion, multiple case exclusion, and judicial review recommendation (`eval/test_undertrial_rules.py`). |
| **Statutory Concordance Fixture**| **30/30 PASS (100.0%)** | Deterministic unit verification on curated benchmark set of statutory transitions. |
| **Adversarial Injection Fixture** | **10/10 PASS (100.0%)** | Quarantines 10 synthetic jailbreak/steganography chunks before vector indexing. |

### B. Statistical Retrieval & QA Defensibility Evaluation ($N = 120$)
Evaluated over $N = 120$ annotated query-document pairs spanning Central/State Gazettes (40), Statutory Enactments (40), and Appellate Rulings (40), alongside a separate held-out set of $N = 30$ unanswerable queries (10 per vertical). Gold answers were annotated by two independent legal and public administration researchers (Cohen's $\kappa = 0.88$). The calibrated refusal threshold ($\tau = 0.40$) was tuned on a separate 20-query dev split. Raw per-query evaluation results are committed and tracked in [`eval/results/per_query_evaluation_results.csv`](./eval/results/per_query_evaluation_results.csv). Baselines were executed under identical conditions:
- **Naive RAG:** 500-token chunks / 50 overlap, FAISS flat inner-product search, top-5 chunks concatenated into prompt, no HyDE, no graph expansion, no reranker, no calibrated refusal.
- **Advanced GraphRAG:** Vector + NetworkX graph traversal with Reciprocal Rank Fusion (RRF), top-5 chunks, but without calibrated per-vertical abstention or cross-encoder NLI verification.
- **Confidence Intervals:** 95% Wilson score intervals for proportions; bootstrap standard error for NLI.

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

## 6. Preloaded Benchmark Scenarios & Citizen Impact

JanSetu AI bundles 7 preloaded sovereign benchmarks directly accessible in 1 click from Document Vault:

1. **PM-KISAN DBT Welfare Guidelines 2024 (`pm_kisan`):**
   - *Provenance:* Operational Guidelines (Revised 2024), Department of Agriculture & Farmers Welfare, Ministry of Agriculture & Farmers Welfare, GoI (source: `pmkisan.gov.in`, retrieved August 2024; authored benchmark excerpt).
   - *Citizen Query:* *"I own agricultural land. Can I receive ₹6,000 annually if my father was a retired government servant?"*
   - *System Output:* Confirms cultivable landholder eligibility (2019 ceiling removal), verifies "family" definition (husband, wife, minor children; adult child with separate land title is eligible independently), verifies pension exclusion ($\ge ₹10,000$), and outputs a structured **Jan Suvidha Card** detailing mandatory prerequisites (Aadhaar-seeded bank account via NPCI, e-KYC via PM-KISAN app, state land seeding).

2. **Synthetic Judicial Benchmark Exemplar (`sc_judgment`):**
   - *Legal Aid Query:* *"Bail considerations for undertrials in non-violent economic offences."*
   - *System Output:* Extracts binding *Ratio Decidendi*, invokes Article 21 liberty safeguards, applies the triple test (flight risk, witness tampering, evidence destruction), and cross-references **CrPC §439 with BNSS §483** and **CrPC §436A with BNSS §479** (first-time offender 1/3rd detention release). Modeled on landmark principles from *Satender Kumar Antil v. CBI* (2022) and *Manish Sisodia v. Directorate of Enforcement* (2024 INSC 595).

3. **Ayushman Bharat PM-JAY Policy Guidelines (`ayushman_bharat`):**
   - *Citizen Query:* *"Hospital is asking cash advance for cardiac surgery under Ayushman card."*
   - *System Output:* Cites mandatory cashless clause under PM-JAY guidelines, ₹5 Lakh family float cover, and provides immediate grievance escalation steps via the National Health Authority (NHA) 14555 helpline.

4. **Tamil Nadu Land Sale Deed & Patta (*கிரையப் பத்திரம்*) (`tamil_pattiram`):**
   - *Citizen Query:* *"கிரையப் பத்திரத்தில் புல எண் மற்றும் நான்கு எல்லைகளை சரிபார்க்கவும்."*
   - *System Output:* Identifies Survey Number (`புல எண் 142/3B`), confirms extent (1200 Sq. Ft. / 2.75 Cents), parses North/South/East/West boundary recitals, checks Nil-Encumbrance Certificate (`வில்லங்கச் சான்றிதழ்`) status, and verifies consideration amount.

5. **Cyber Fraud Reporting & Zero-FIR (Helpline 1930 / I4C) (`cyber_fir`):**
   - *Citizen Query:* *"Scammer transferred ₹50,000 from my UPI account 40 minutes ago. What should I do?"*
   - *System Output:* Outlines the Golden Hour protocol, instructs calling 1930 for CFCFRMS bank-lien freezing, details required transaction IDs, and explains the mandatory right to file a **Zero-FIR under BNSS §173** and **BNS §318(4)** (general cheating applied to cyber fraud, read with IT Act §66D) at any police station without territorial restriction.

6. **Model Tenancy Act Guidelines (`tenancy_act`):**
   - *Citizen Query:* *"Landlord is demanding 10 months deposit and threatened immediate eviction without notice."*
   - *System Output:* Cites Section 11 of the Model Tenancy Act limiting residential security deposit to a maximum of **2 months' rent**, cites the statutory rule requiring at least 24 hours' written advance notice prior to landlord entry/inspection, and details summary eviction protection under the Rent Authority. *(With caveat on state enactment and existing state laws like Karnataka Rent Act, 1999).*

7. **Senior Citizens Parental Property Protection Act 2007 (§23) (`senior_citizen`):**
   - *Citizen Query:* *"I gifted my house to my son on the condition he takes care of my medical expenses, but he threw me out. Can I get my property back?"*
   - *System Output:* References **Section 23 of the MWPSC Act, 2007**, explaining the procedure to petition the Maintenance Tribunal to declare conditional gift deeds void. Highlights the judicial requirement (*Sudesh Chhikara v. Ramti Devi, 2022 SC*) that the maintenance condition must be an express or integral covenant of the transfer.

---

## 6A. Deployment Economics: Cloud Serverless vs. On-Premise Edge TCO

> **Currency & Exchange Rate Baseline:** Conversions assume a baseline exchange rate of **1 USD ≈ Rs. 84.00**. CapEx ~Rs. 72,000 ≈ $857; Cloud OpEx ~$0.0011/query ≈ Rs. 0.092/query; 10,000 queries/mo ~$11.00 ≈ Rs. 924 (~Rs. 925/mo); On-prem edge electricity ~Rs. 325/mo ≈ $3.87 (~$4.00/mo).

> **Data Residency First:** On-premise edge deployment is engineered primarily as an **institutional data-residency and confidentiality necessity** (DPDPA 2023 Section 16, air-gapped courtrooms, sensitive citizen welfare dossiers), where cross-border cloud processing is procedurally or legally prohibited, rather than as a quick cost-payback mechanism.

To establish operational feasibility for public sector deployment, JanSetu AI benchmarks two profiles:
- **Cloud Serverless:** Rs. 920/mo ($11.00) at ~Rs. 0.09/query.
- **On-Premise Edge Rig:** Rs. 72,000 CapEx. Electricity formula: ~180W duty × 9 hrs/day × 25 working days = **~40.5 kWh/month × Rs. 8.00/kWh ≈ Rs. 325/month (~$4.00)**.

| Economic Dimension | Cloud Serverless (Pay-per-Token) | Sovereign On-Premise Edge Rig |
|---|---|---|
| **Capital Expenditure (CapEx)** | **$0** (No upfront server hardware purchase) | **~Rs. 72,000 ($860)**: AMD Ryzen 7 5700X (8C/16T), 32 GB DDR4, NVIDIA RTX 3060 12 GB VRAM |
| **Operational Cost per Query** | **~$0.0011 (Rs. 0.09) per query** (Workers AI + Nomic Embed API) | **Rs. 0.00 API cost**; ~180W power under active synthesis (~Rs. 1.44 / hour (180W at Rs. 8.00/kWh) electricity) |
| **Monthly Operating Cost (10,000 Queries)** | **~$11.00 / month (~Rs. 920)** | **~$4.00 / month (~Rs. 325)** power draw (amortized fixed asset) |
| **Institutional Applicability** | State E-Governance citizen web portals | Panchayat kiosks, Common Service Centers (CSCs), District Legal Services Authorities (DLSAs), air-gapped courtrooms |

## 6B. Citizen Safeguards, Red-Teaming & Human Handoff Routing
JanSetu AI strictly enforces responsible AI standards for citizen protection:
1. **Explicit Legal Disclaimer:** Every interface prominently indicates that JanSetu AI is an assistive research and information tool, not legal advice.
2. **Direct Human Handoff Hotlines:** When legal risks, distress, or complex criminal allegations are flagged, the system actively routes users to certified official bodies:
   - **National Legal Services Authority (NALSA) 24x7 Helpline:** `15100` (Free legal aid for undertrials, women, and marginalized citizens).
   - **Indian Cyber Crime Coordination Centre (I4C) Helpline:** `1930` (National Cyber Financial Fraud Reporting).
   - **Ayushman Bharat PM-JAY Grievance Helpline:** `14555` (Cashless hospital dispute escalation).
3. **Adversarial Red-Teaming Results:** Evaluated against 10 synthetic injection payloads (system prompt extraction, Unicode zero-width steganography, ChatML role hijacking), achieving **100% quarantine isolation (10/10 PASS)** prior to vector indexing.

## 6C. Structured Real-World Pilot Protocol (Q3 Milestone)
The Q3 edge deployment milestone follows a structured, human-subject-compliant evaluation protocol:
- **Participant Cohort:** $N = 15$ operators across 5 Common Service Centers (CSCs) and 2 legal aid desks, subject to Institutional Review Board (IRB) exemption and formal institutional MoUs.
- **Evaluation Design:** Within-subject comparative study ($N = 60$ live queries) comparing manual administrative search against JanSetu AI assisted lookup.
- **Key Empirical Metrics:**
  1. *Task Completion Time (TCT):* Mean duration to identify qualifying welfare clauses or bail eligibility (targeting $\ge 70\%$ reduction).
  2. *Eligibility Error Rate:* False exclusions or missed prerequisites detected on sample applications.
  3. *System Usability Scale (SUS):* Standardized 10-item usability survey targeting an SUS benchmark score $> 80$ (Grade A).

---

## 7. 12-Month Fellowship Work Plan & Implementation Roadmap

| Milestone / Quarter | Focus Areas | Key Technical Deliverables | National Impact & Outcomes |
|---|---|---|---|
| **Q1 (Months 1–3)** | **Sovereign Foundation & Corpus Expansion** | • Scale vector retrieval from flat FAISS to `IndexHNSWFlat` and migrate graph persistence to embedded columnar storage (DuckDB / SQLite WAL) for scaling to 250,000 document nodes.<br>• Ingest complete Central Gazettes (2020–2024) and Supreme Court Constitution Bench rulings.<br>• Refine zero-dependency Indic script parsing across 10 official languages.<br>• Implement local authentication (argon2id password hashing + local JWT tokens), RBAC roles, and AES-256 storage encryption to transition beyond single-tenant DevUser test profiles. | High-fidelity retrieval across national welfare and legal statutes with scalable vector-graph search and hardened local security. |
| **Q2 (Months 4–6)** | **Multi-State Land Deed & Concordance Hardening** | • Expand deed extraction to Telugu, Marathi, and Hindi registry formats (*विक्रय विलेख, खरेदीखत*).<br>• Integrate native Indic NLI models (MuRIL / IndicBERT fine-tuned on IndicXNLI) for vernacular entailment verification.<br>• Incorporate State-specific High Court concordance amendments under BNSS.<br>• Curate and contribute `IndiaGroundedRAG-2500` benchmark dataset ($N=2,500$ verified pairs in Q2, scaling to $N=5,000$ in Q3, annotated by 4 legal and public administration research scholars, targeting Cohen's $\kappa \ge 0.85$). | Rural citizen protection against fraudulent land registrations, boundary manipulation, and verified open datasets for the IndiaAI platform. |
| **Q3 (Months 7–9)** | **Edge Hardware Deployment & CSC Pilot Trials** | • Containerize JanSetu AI for lightweight edge devices (AMD Ryzen 7 5700X, 32 GB RAM, NVIDIA RTX 3060 12 GB VRAM / Jetson) with quantized local models (Qwen2.5 7B, local Whisper.cpp / AI4Bharat IndicConformer for offline speech).<br>• Proposed pilot trials: 10 Common Service Centers (CSCs) and 2 District Legal Services Authorities (DLSAs), subject to Institutional Review and formal MoUs with State E-Governance Missions and State Legal Services Authorities.<br>• Hybrid architecture: offline local edge processing for document intelligence, with optional online uplink to Government of India Bhashini APIs. | Grassroots citizen assistance at panchayats and legal aid kiosks. |
| **Q4 (Months 10–12)** | **Open-Source DPI Release & Policy Synthesis** | • Open-source reference implementation under MIT License on GitHub.<br>• Finalize comprehensive empirical benchmark dataset and evaluation suite.<br>• Draft and submit Technical Policy Whitepaper on Verifiable RAG for e-Courts and Digital India. | Open-source reference implementation and evaluation benchmark for Digital Public Infrastructure (DPI). |

---

## 8. Applicant Credentials & Submission Summary

- **Applicant:** Dhanush S
- **Institution:** Department of Computer Science and Engineering, Kalasalingam Academy of Research and Education, Tamil Nadu, India.
- **Research Scholars / Annotator Support:** Ground-truth annotations and verification rubrics conducted with 2 postgraduate legal and public administration scholars at Kalasalingam Academy of Research and Education (Cohen's $\kappa = 0.88$, protocol in `eval/annotation_protocol.md`).
- **Research Foundation:** Built upon peer-reviewed literature in Retrieval-Augmented Generation (Lewis et al., 2020), HyDE (Gao et al., 2022), Reciprocal Rank Fusion (Cormack et al., 2009), and cross-encoder claim entailment.
- **Repository:** Fully reproducible code, tests, and documentation hosted publicly at [github.com/shoyo44/JanSetu-AI](https://github.com/shoyo44/JanSetu-AI).
- **Compliance:** Aligned with IndiaAI Mission trust and safety frameworks and open-source reproducibility standards.
