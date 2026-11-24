# JanSetu AI — Gold Benchmark Annotation & Calibration Protocol

This document establishes the ground-truth curation guidelines, dataset split partitioning, threshold calibration methodology, and verification rubrics for the JanSetu AI Sovereign Benchmark QA Suite (`eval/gold/sovereign_benchmark_qa.jsonl`).

---

## 1. Ground-Truth Curation Guidelines

The 150 gold benchmark queries were curated directly against official Indian statutory enactments and government guidelines:
- **Public Governance:** Formulated against Central Sector Scheme operational guidelines (*PM-KISAN* G.S.R. 412(E)), *Ayushman Bharat PM-JAY* operational criteria, and the *Maintenance and Welfare of Parents and Senior Citizens Act, 2007*.
- **Statutory Law & Citizen Rights:** Formulated against MHA/I4C Cyber Crime advisories (Helpline 1930, Zero-FIR under BNSS §173), MoHUA Model Tenancy Act provisions, and registered Tamil Nadu land deeds (*கிரையப் பத்திரம்*, SRO Tambaram Doc 4218/2023).
- **Judicial Precedents & Bail:** Formulated against Supreme Court bail jurisprudence (*Manish Sisodia v. ED* [2024 INSC 595], *Satender Kumar Antil v. CBI* [2022], and Article 21 precedents).

Each answerable query specifies:
- `id`: Unique identifier (`Q_001` through `Q_120`).
- `vertical`: Target domain (`governance`, `law`, `judgment`).
- `subdomain`: Target legal/administrative enactment.
- `question`: Natural language query in English, Hindi (हिन्दी), or Tamil (தமிழ்).
- `answerable`: Boolean flag (`true` for answerable, `false` for held-out unanswerable).
- `target_chunk_id`: Specific ground-truth statutory chunk providing direct evidence for the query.

---

## 2. Dataset Partitioning & Split Separation

To prevent data leakage, queries are strictly partitioned into distinct development and test splits:

| Split | File Location | Query Count | Purpose |
|---|---|---|---|
| **Development Tuning Split** | `eval/gold/dev_tuning_split.jsonl` | $N = 20$ (10 answerable, 10 unanswerable) | Threshold grid search ($\tau \in [0.20, 0.60]$) to calibrate the abstention engine. |
| **Held-Out Test Split (Answerable)** | `eval/gold/sovereign_benchmark_qa.jsonl` (`Q_001`–`Q_120`) | $N = 120$ (40 Governance, 40 Judgment, 40 Statutory Law) | Unseen evaluation of Top-5 Context Recall and NLI Citation Entailment. |
| **Held-Out Test Split (Unanswerable)** | `eval/gold/sovereign_benchmark_qa.jsonl` (`Q_121`–`Q_150`) | $N = 30$ (10 per vertical) | Unseen evaluation of Calibrated Refusal Accuracy under fixed $\tau$. |

---

## 3. Planned Multi-Annotator Validation Protocol (AIKosh Release)

As part of the IndiaAI Fellowship research deliverables (Milestone: AIKosh Open Benchmark Dataset Release), the dataset is undergoing independent dual-annotation:
- **Annotation Scale:** 3-point relevance scale (0 = Irrelevant, 1 = Partially Relevant, 2 = Fully Supporting Gold Clause).
- **Metric:** Cohen's $\kappa$ inter-annotator agreement on binary retrieval acceptability (Score $\ge 1$ vs Score $= 0$).
- **Consensus Rule:** Any discrepant annotations are resolved through joint review against the official Gazette text before final submission to the national AIKosh portal. Target agreement threshold: $\kappa \ge 0.85$.

---

## 4. Threshold Calibration Methodology ($\tau$)

The empirical similarity threshold $\tau$ separates grounded answerable contexts from out-of-scope/unanswerable queries. Calibration was performed exclusively on the 20-query development split (`eval/gold/dev_tuning_split.jsonl`):
- Grid search over $\tau \in [0.25, 0.55]$ with step size $\Delta = 0.01$.
- Objective: Maximize Youden's $J = \text{TPR} + \text{TNR} - 1$ (balancing answerable retrieval rate with safe refusal rate).
- **Calibrated Cloud Threshold (`nomic-embed-text-v1.5`):** $\tau^* = \mathbf{0.40}$ ($J = 0.90$ on dev split).
- **Calibrated On-Premise Threshold (`nomic-embed-text` Ollama):** $\tau^* = \mathbf{0.38}$ ($J = 0.88$ on dev split).

Both thresholds were fixed on the development split prior to evaluating held-out test splits.
