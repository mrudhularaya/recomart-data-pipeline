# Recomart End-to-End Recommendation Data Pipeline & Warehouse 

## 🎯 Project Overview
This repository contains a modular, configuration-driven, and enterprise-grade recommendation system data pipeline built completely around the **Single Responsibility Principle (SRP)**. 

The engine processes automated data ingestion across multi-format layers (tabular CSV structures and external vendor REST APIs), executes defensive validation gating, processes algorithmic feature transformations, and stores vectorized footprints inside a local relational SQLite database warehouse. Serving vectors are synchronized into an ultra-low latency Custom Feature Store Registry cache, tracked natively via **Git LFS** and **MLflow**, and fully automated using a **Prefect** orchestration workflow.

---

## 🏛️ Project Directory Structure

```text
recomart-data-pipeline/
│
├── config/
│   └── config.yaml             # Tasks 2 & 3: Global source paths & pipeline configs
│
├── data/                       # Local Data Lake Layer
│   ├── source/                 # Landing pad for incoming raw source file drops
│   ├── raw/                    # Chronologically partitioned historical lake files
│   ├── validated/              # Task 4: Output gate for structurally clean frames
│   ├── processed/              # Task 5: Encoded, normalized model-ready matrices
│   └── warehouse/              # Tasks 6 & 7: Relational SQLite DB, cache tables, & catalogs
│
├── logs/
│   └── ingestion.log           # Uniform machine-readable JSON logging audit trails
│
├── reports/                    # Generated pipeline deliverables
│   ├── validation_report.json  # Data profiling metrics scorecard
│   ├── validation_report.pdf   # Publication-ready Quality Report PDF
│   └── data_lineage.json       # Task 8: Provenance mapping asset graph logs
│
├── src/                        # Complete Application Source Code Base
│   ├── common/                 # Core absolute path YAML configuration and log loaders
│   ├── ingestion/              # Ingestors (CSV/API) and file system staging managers
│   ├── validation/             # Automated constraints testing and PDF generation engines
│   ├── preparation/            # Deduplication, median imputation, and numeric scalers
│   ├── feature_engineering/               # Analytical grouping matrices and SQL layer builders
│   ├── feature_registry/          # Custom real-time Online Serving Feature Cache compiler
│   ├── models/                 # Popularity baselines, text NLP TF-IDF recommenders, & MLflow
│   └── orchestration/          # Task 10: Prefect master workflow control DAG
│
├── .gitattributes              # Task 8: Git LFS binary pointer tracking definitions
├── .gitignore                  # Production system-wide clean commit filters
└── requirements.txt            # Unified project environment dependencies
```

---

## 🏗️ Comprehensive Pipeline Architecture

```text
                        Prefect Flow
                (Workflow Orchestration)
                             │
                             ▼

                        CSV + REST API

                        ↓

                        Ingestion

                        ↓

                        Raw

                        ↓

                        Validation

                        ↓

                        Preparation

                        ↓

                        Feature Engineering

                        ↓

                        SQLite Warehouse

                        ↓

                        Feature Store

                        ↓

                        Recommendation Models

                        ↓

                        Evaluation

                        ↓

                        MLflow
```

---

## 📦 Pipeline Feature Matrix By Task

### 🔄 Data Collection, Ingestion & Lake Storage (Tasks 2 & 3)
*   **Multi-Engine Processing:** Abstracts internal databases via local CSV streams and streams real-time vendor catalog models via network REST connectors using explicit timeouts (`30s`).
*   **Resiliency Layer:** Implements a strict Max Retries loop backed by an automated **Exponential Backoff mechanism** (`time.sleep(2 ** attempt)`) to survive transient connectivity timeouts.
*   **Logical & Temporal Partitioning:** Segregates internal tabular models under `data/raw/` and external endpoints under `data/external/`, partitioning subsets using automated, chronological `YYYY-MM-DD` directory tracks.

### 🛡️ Automated Data Profiling & Validation (Task 4)
*   **Structural Schema Gate:** Compares column presence dynamically against strict target headers, gracefully trapping missing frames before they corrupt downstream steps.
*   **Constraint Checklist Checks:** Audits data fields for type safety and out-of-bounds parameters (e.g., verifying `age` boundaries are $0 \le \text{age} \le 120$ and review rankings fit the mandatory $1 \text{ to } 5$ scale).
*   **Executive Delivery:** Output logs write out to a central `validation_report.json` which is instantly compiled into a publication-ready **Data Quality Report (PDF)** document.

### 🧼 Data Preparation, Imputation & Scaling (Task 5)
*   **Tabular Deduplication:** Drops dirty duplicate entries across core unique indexes (`user_id`, `product_id`).
*   **Sparsity Protection Imputation:** Preserves calculation densities by dynamically filling missing null fields using median values or neutral fallback categories.
*   **Mathematical Normalization Variable Scaling:** Performs **Min-Max Scaling** on user age fields and executes **Log Normalization Transformations** on skewed price variables to optimize training weights.

### 🗄️ Feature Engineering & SQL Warehousing (Task 6)
*   **Behavioral Feature Aggregations:** Computes user-level interaction profiles (session activity frequencies) and product metrics (item review volume and baseline mean scoring weights).
*   **Star-Schema Relational Warehouse:** Structures structured dimensional tables (`dim_users`, `dim_products`) and connecting transactions maps (`fact_interactions`) inside an indexed **SQLite Database Warehouse** file.

### ⚡ Custom Metadata Feature Store Registry (Task 7)
*   **Real-Time Online Cache Layer:** Deploys an active Key-Value serving cache table (`online_feature_cache`) inside the warehouse database. It pivots flat dimensions out into structured composite keys (`[view_name]:[entity_id]`) to enable ultra-low latency real-time model inference.
*   **Central Governance Catalog:** Outputs a standardized governance document (`feature_registry.json`) detailing active features, sources, data formats, and logic mappings.

### ⛓️ Data Versioning & Provenance Tracking (Task 8)
*   **Git LFS Large Asset Tracking:** Enforces **Git Large File Storage (LFS)** to replace heavy data structures (`.csv`, `.db`) with light text pointer hashes inside the source repository, protecting history bounds.
*   **Programmatic Lineage Manifest:** Generates an end-to-end data provenance log (`data_lineage.json`) mapping asset dependencies from entry source down to engineered feature space.

### 🧠 Model Training & Lab Experiment Tracking (Task 9)
*   **Popularity Baseline Recommender:** Sorts item entities by total interaction counts and average rating matrices to handle cold-start conditions for new profiles.
*   **Content-Based TF-IDF Recommender:** Synthesises product text fields (`product_name` + `category` + `description`), extracts keyword semantics via a **TF-IDF Vectorizer**, and applies **Cosine Similarity Matrices** to make personalized product recommendations.
*   **MLflow Observability Workspace:** Connects directly into training runs to log hyper-parameters, configurations, and evaluation metrics (`Precision@5` and `Recall@5`).

### ⚙️ Pipeline Automation Workflow Orchestration (Task 10)
*   **Native Cross-Platform DAG Management:** Automates the complete data platform using **Prefect** task graph nodes. It handles task dependencies natively on Windows/macOS/Linux, provides real-time logs, and supports local tracking via `prefect server start`.

---

## 🚀 Setup & Execution Guide

### 1. Initialize Virtual Environment & Install Dependencies
Ensure you have Python 3.10+ installed. Create an environment, activate it, and install packages:
```bash
python -m venv .venv
# Activate on Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Upgrade base packaging tools and run installation
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 2. Configure Git LFS Tracking
Activate Large File Storage on your system before committing your project directory:
```bash
git lfs install
git add .gitattributes
```

### 3. Run the Complete Automated Pipeline via Prefect
Trigger the entire architecture sequentially—from data collection down to your personalized polo shirt model recommendations—by executing the master flow script:
```bash
python src/orchestration/recomart_dag.py
```

### 🔍 Monitoring Dashboard Tools
To open interactive tracking UIs and visually inspect your pipeline execution runs and machine learning parameters:
*   **MLflow Metrics Console:** Run `mlflow ui` in a terminal tab and open `http://localhost:5000`
*   **Prefect Orchestration Server:** Run `prefect server start` in a terminal tab and open `http://127.0.0.1:4200`
