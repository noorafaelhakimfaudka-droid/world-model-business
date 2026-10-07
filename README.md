# Janji: World Model for Business (Olist Edition)

> **Jangan perbaiki kurirnya dulu. Uji janjinya.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests: Pytest Passing](https://img.shields.io/badge/tests-13%20passed-brightgreen.svg)](https://pytest.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end Decision Support System that combines **Machine Learning**, **Causal Inference (PSM)**, and **Stochastic Counterfactual Simulation (World Model)** on 99,000+ real-world e-commerce orders from Olist (Brazil).

Instead of chasing leaderboard accuracy metrics in isolation, this project is engineered from an executive strategy perspective: **How can machine learning de-risk multi-million dollar operational decisions before allocating physical capital?**

---

## 📌 Executive Summary & Key Findings

| Strategic Finding | Methodology | Business Impact |
|---|---|---|
| **1. Causal Impact of Delivery Delays** | Propensity Score Matching (PSM) with Caliper 0.05 + Placebo Test | Delays causally cause a **1.71★ drop** in review scores (p < 0.001). This is not a correlational coincidence with heavy freight or long routes. |
| **2. Psychology Beats Logistics (The Underpromise Effect)** | Counterfactual Policy Simulation (World Model Block 1-3) | Adding a **+3-day SLA buffer** to delivery promises prevents **~2,600 bad reviews** at **R$ 0 logistics capex**, outperforming courier speedup programs. |
| **3. Early Warning Delay Detection** | Point-in-Time As-Of Random Forest at T0 & T1 | Identifies high-risk orders with **8.0% precision** (vs 4.4% business heuristic baseline = **1.8x lift**), enabling targeted proactive customer support. |
| **4. Unit Economics & Retention ROI** | Customer Repeat Behavior & CLV Modeling | Each bad review prevented preserves **R$ 48 to R$ 92** in future customer value. Proactive R$ 15 goodwill coupons achieve positive ROI at >11% retention conversion. |

---

## 🚀 Interactive Streamlit Application

A production-ready decision dashboard is included for live presentations and stakeholder interactions.

```bash
# Launch the interactive web app locally
streamlit run streamlit_app.py
```

### Application Features:
1. **Executive KPI Dashboard & 10 Core Business Insights**: Pareto volume concentration, geographic bottlenecks, and the satisfaction cliff.
2. **Customer (RFM) & Seller Segmentation**: Profiling high-value customers and diagnosing the 6% of sellers causing 34% of delays.
3. **Operational Demand Forecasting**: 4-week lookahead demand forecasting per category (WAPE = 13.6%).
4. **Early Warning Delay Risk Scorer**: Real-time order risk evaluation at checkout (T0) and carrier handoff (T1).
5. **Causal Impact Lab**: Interactive matched-pairs visualization comparing late vs on-time twins.
6. **The World Model Simulator (What-If Engine)**: Interactive sliders for SLA buffers, seller speedup, and carrier transit times to observe live metric shifts.
7. **Business ROI & A/B Experiment Calculator**: Sample size, power (80%), alpha (5%), and break-even financial thresholds.

---

## 🏗️ Architectural Framework

```
                          ┌──────────────────────────────────────────────┐
                          │         RAW DATA (9 OLIST CSV FILES)         │
                          └──────────────────────┬───────────────────────┘
                                                 ▼
                          ┌──────────────────────────────────────────────┐
                          │         SQL DATA MART (SQLite OLAP)          │
                          │   01_raw.sql -> 02_clean.sql -> 03_mart.sql  │
                          └──────────────────────┬───────────────────────┘
                                                 ▼
             ┌───────────────────────────────────┴───────────────────────────────────┐
             ▼                                                                       ▼
┌─────────────────────────┐                                             ┌─────────────────────────┐
│     DEVELOPMENT SET     │                                             │   SEALED HOLDOUT SET    │
│  86,283 Orders (Train)  │                                             │ 12,801 Orders (Locked)  │
└────────────┬────────────┘                                             │ SHA-256 Verified Lock   │
             │                                                          └─────────────────────────┘
             ├───────────────────────────────────────────────────────────────────────┐
             ▼                                                                       ▼
┌─────────────────────────┐                                             ┌─────────────────────────┐
│  POINT-IN-TIME AS-OF    │                                             │   CAUSAL INFERENCE      │
│  FEATURE ENGINEERING    │                                             │   PSM Matched Pairs     │
│  T0: Checkout Only      │                                             │   ATE = -1.71 Stars     │
│  T1: Carrier Handoff    │                                             │   Placebo Test: Valid   │
│  T2: Post-Delivery      │                                             └────────────┬────────────┘
└────────────┬────────────┘                                                          │
             │                                                                       │
             ▼                                                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        STOCHASTIC WORLD MODEL SIMULATOR                                │
│   Policy Intervention -> Block 1: Delay Risk -> Block 2: Review Risk -> Block 3: CLV   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Strict Methodological Guardrails:
- **Zero Future Data Leakage**: Features are timestamp-partitioned *as-of* prediction time ($T \le T_0$ for checkout risk).
- **Time-Ordered Partitioning**: Strict chronological split with a buffer period; no random shuffling on temporal data.
- **Sealed Holdout Verification**: Holdout data is sealed with SHA-256 cryptographic hashes and only evaluated once at project maturity.
- **Claims Discipline**: Every metric is derived strictly from real code execution with dual verification (SQL & pandas).

---

## 📂 Repository Navigation

| Notebook | Focus Area | Key Method / Model | Primary Output |
|---|---|---|---|
| [`01_business_eda.ipynb`](notebooks/01_business_eda.ipynb) | Exploratory Data Analysis | Descriptive Statistics, Geocoding | 10 Core Business Insights |
| [`02_clustering.ipynb`](notebooks/02_clustering.ipynb) | Segmentation | RFM Clustering, Seller Profiling | High-Value & At-Risk Segments |
| [`03_forecasting.ipynb`](notebooks/03_forecasting.ipynb) | Demand Forecasting | Moving Average, Ridge, Exp Smoothing | WAPE = 13.6% (Weekly Demand) |
| [`04_predict_late.ipynb`](notebooks/04_predict_late.ipynb) | Delay Risk Early Warning | Random Forest, Top-K Lift | Precision = 8.0% (1.8x Baseline Lift) |
| [`05_predict_reviews.ipynb`](notebooks/05_predict_reviews.ipynb) | Customer Sentiment | TF-IDF, N-Grams, Logistic Regression | PR-AUC = 0.38, Top Root Causes |
| [`06_causal_impact.ipynb`](notebooks/06_causal_impact.ipynb) | Causal Inference | Propensity Score Matching (PSM) | ATE = -1.71★ (Causal Proof) |
| [`07_world_model.ipynb`](notebooks/07_world_model.ipynb) | Simulation Engine | Multi-Block Probabilistic Chain | Unit Tests U1-U3 Validated |
| [`08_scenarios.ipynb`](notebooks/08_scenarios.ipynb) | What-If Policy Lab | Scenario Analysis (S1, S2, S3) | Buffer SLA Beats Courier Capex |
| [`09_business_value.ipynb`](notebooks/09_business_value.ipynb) | ROI & Experimentation | CLV Attribution, Sample Size Math | A/B Test Design (N=1,560/group) |

---

## 🛠️ Quickstart Guide

### 1. Prerequisites & Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-username/world-model-business.git
cd world-model-business

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Automated Test Suite
```bash
python -m pytest tests/ -v
```
*(All 13 tests verify schema contracts, time consistency, feature point-in-time constraints, and anti-leakage positive controls).*

### 3. Launch Web Application
```bash
streamlit run streamlit_app.py
```

### 4. Build Pipeline from Scratch (Optional)
```bash
# Transform raw data to SQLite database
python src/data/build_database.py

# Extract point-in-time features (T0, T1, T2)
python src/features/build_features.py
```

---

## 🧪 Automated Testing & Data Contracts

The codebase includes an automated test suite (`tests/`) ensuring data contracts and statistical integrity:
- `test_data_contracts.py`: Validates primary keys, price non-negativity, review score ranges (1-5), and mart table row counts.
- `test_features_as_of.py`: Enforces that T0 feature sets contain zero columns from post-checkout timestamps.
- `test_leakage.py`: Positive control verifying that leaking actual delivery days artificially inflates precision, confirming our leak detection flags are operational.
- `test_time_split.py`: Asserts strict chronological separation between development and holdout splits without time overlap.

---

## 📄 License & Attribution
- Dataset: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) on Kaggle.
- Code released under the [MIT License](LICENSE).
