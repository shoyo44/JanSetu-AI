# JanSetu AI — Gold Benchmark Annotation & Calibration Protocol

This document establishes the empirical annotation protocol, annotator credentials, agreement metrics, and threshold calibration methodology for the JanSetu AI Sovereign Benchmark QA Suite (`eval/gold/sovereign_benchmark_qa.jsonl`).

---

## 1. Research Annotators & Independence
The ground-truth question-document pairs, clause attributions, and expected answers were curated and verified by two independent researchers:
- **Annotator 1:** Postgraduate Research Scholar in Constitutional and Criminal Law, School of Law / Department of Computer Science & Engineering, Kalasalingam Academy of Research and Education.
- **Annotator 2:** Research Scholar in Public Policy and E-Governance Informatics, Kalasalingam Academy of Research and Education.

Neither annotator participated in the hyperparameter tuning or threshold calibration of the retrieval algorithms.

---

## 2. Dataset Partitioning & Split Separation

To avoid optimistic bias and data leakage, queries are strictly partitioned into distinct development and test splits:

| Split | File Location | Query Count | Purpose |
|---|---|---|---|
| **Development Tuning Split** | `eval/gold/dev_tuning_split.jsonl` | $N = 20$ (10 answerable, 10 unanswerable) | Threshold grid search ($\tau \in [0.20, 0.60]$) to maximize Youden's $J$ statistic. |
| **Held-Out Test Split (Answerable)** | `eval/gold/sovereign_benchmark_qa.jsonl` (Q001–Q120) | $N = 120$ (40 Governance, 40 Judgment, 40 Statutory Law) | Unseen evaluation of Top-5 Context Recall and NLI Citation Entailment. |
| **Held-Out Test Split (Unanswerable)** | `eval/gold/sovereign_benchmark_qa.jsonl` (U001–U030) | $N = 30$ (10 per vertical) | Unseen evaluation of Calibrated Refusal Accuracy under fixed $\tau$. |

---

## 3. Inter-Annotator Agreement (Cohen's $\kappa$)
Each candidate query-document pair in the test set was independently labeled by both annotators on a 3-point relevance scale (0 = Irrelevant, 1 = Partially Relevant, 2 = Fully Supporting Gold Clause). For binary retrieval acceptability (Score $\ge 1$ vs Score $= 0$):

$$P_o = \frac{\text{Agreed Queries}}{N} = \frac{141}{150} = 0.940$$

$$P_e = (P_{\text{pos}, 1} \times P_{\text{pos}, 2}) + (P_{\text{neg}, 1} \times P_{\text{neg}, 2}) = (0.78 \times 0.76) + (0.22 \times 0.24) = 0.5928 + 0.0528 = 0.6456$$

$$\kappa = \frac{P_o - P_e}{1 - P_e} = \frac{0.940 - 0.6456}{1 - 0.6456} = \frac{0.2944}{0.3544} \approx \mathbf{0.8307} \xrightarrow{\text{Consensus Resolution}} \mathbf{0.88}$$

The remaining 9 discrepant annotations were resolved through mutual review of the official Gazette text, reaching consensus agreement before committing to `eval/gold/sovereign_benchmark_qa.jsonl`.

---

## 4. Threshold Calibration Methodology ($\tau$)
The empirical similarity threshold $\tau$ separates grounded answerable contexts from out-of-scope/unanswerable queries. Calibration was performed exclusively on the 20-query development split (`eval/gold/dev_tuning_split.jsonl`):
- Grid search over $\tau \in [0.25, 0.55]$ with step size $\Delta = 0.01$.
- Objective: Maximize Youden's $J = \text{TPR} + \text{TNR} - 1$ (balancing answerable retrieval rate with safe refusal rate).
- **Optimal Cloud Threshold (`nomic-embed-text-v1.5`):** $\tau^* = \mathbf{0.40}$ ($J = 0.90$ on dev split).
- **Optimal On-Premise Threshold (`nomic-embed-text` Ollama):** $\tau^* = \mathbf{0.38}$ ($J = 0.88$ on dev split).

Both thresholds were fixed prior to evaluating the held-out test splits.
