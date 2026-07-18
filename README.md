# Recomart End-to-End Recommendation Data Pipeline & Warehouse 

## Project Overview
This project implements an end-to-end recommendation data pipeline for the RecoMart e-commerce platform. The pipeline ingests raw datasets, validates and prepares data, engineers recommendation features, loads them into a SQLite warehouse, materializes serving features, trains baseline recommendation models, and orchestrates the workflow using Prefect.
The implementation follows the Single Responsibility Principle (SRP), with each pipeline stage isolated into an independent module.

---

## Project Directory Structure

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
├── docs/problem_formulation
│   └── task1_report.md    
│   └── task1_report.pdf         # Task 1: Problem Formulation - short report (PDF) 
│
├── reports/                    # Generated pipeline deliverables
│   ├── validation_report.json  # Data profiling metrics scorecard
│   ├── validation_report.pdf   # Quality Report PDF
│   └── data_lineage.json       # Task 8: Provenance mapping asset graph logs
│
├── src/                        # Complete Application Source Code Base
│   ├── common/                 # Core absolute path YAML configuration and log loaders
│   ├── ingestion/              # Ingestors (CSV/API) and file system staging managers
│   ├── validation/             # Automated constraints testing and PDF generation engines
│   ├── preparation/            # Deduplication, median imputation, and numeric scalers
│   ├── feature_engineering/               # Analytical grouping matrices and SQL layer builders
│   ├── feature_store/          # Custom real-time Online Serving Feature Cache compiler
│   ├── models/                 # Popularity baselines, text NLP TF-IDF recommenders, & MLflow
│   └── orchestration/          # Task 10: Prefect master workflow control DAG
│
├── .gitattributes              # Task 8: Git LFS binary pointer tracking definitions
├── .gitignore                  # Production system-wide clean commit filters
└── requirements.txt            # Unified project environment dependencies
```

---

## Project Documentation

The repository includes the following documentation:

- Task 1 – Problem Formulation (`docs/problem_formulation/`)
- Module-specific README files for Tasks 2–10
- Validation reports (`reports/`)
- EDA visualizations (`reports/eda/`)
- Data lineage manifest (`reports/data_lineage.json`)

---

## Comprehensive Pipeline Architecture

```text
                        Prefect Flow
                (Workflow Orchestration)
                             │
                             ▼

                        CSV + REST API (Source Data)

                        ↓

                        Ingestion

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

                        Model Training

                        ↓

                        Evaluation

                        ↓

                        MLflow + Reports + Lineage
```

---

## Modules

| Module | Responsibility |
|---------|---------------|
| Ingestion | CSV + REST API extraction |
| Validation | Schema and quality checks |
| Preparation | Cleaning and feature preprocessing |
| Feature Engineering | Aggregations and warehouse loading |
| Feature Store | Online feature materialization |
| Models | Popularity and content-based recommenders |
| Governance | Data lineage |
| Orchestration | Prefect workflow |
---

## Technologies

- Python
- Pandas
- SQLite
- Prefect
- MLflow
- ReportLab
- Scikit-learn
---

## Setup & Execution Guide

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

### Monitoring Dashboard Tools
To open interactive tracking UIs and visually inspect your pipeline execution runs and machine learning parameters:
*   **MLflow Metrics Console:** Run `mlflow ui` in a terminal tab and open `http://localhost:5000`
*   **Prefect Orchestration Server:** Run `prefect server start` in a terminal tab and open `http://127.0.0.1:4200`
