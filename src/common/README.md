# Task 8 — Data Versioning and Lineage Documentation

## 🎯 Objective
This layer enforces data integrity, tracking, and compliance across the pipeline. It handles tracking historical versions of binary data lake assets using **Git LFS** and provides transparent mapping records via a central data lineage manifest.

---

## 📦 Data Versioning Workflow (Git LFS)

Because large analytical datasets distort standard text-based source tracking systems, this project implements **Git LFS (Large File Storage)**. Git LFS replaces raw binary assets with text pointer files inside Git while storing the actual data blocks in an decoupled storage pool.

### Git LFS Tracking Matrix
The system tracks the following file patterns automatically:
*   `data/source/*.csv` — Incoming unprocessed flat source drops.
*   `data/raw/**/*.csv` — Date-partitioned historical extractions.
*   `data/processed/**/*.csv` — Preprocessed and normalized algorithmic baselines.
*   `data/warehouse/*.db` — Relational SQLite Warehouse instances and registries.

### Version Verification Workflow
To view your project data file tracking logs:
```bash
git lfs status
git lfs ls-files
```

---

## ⛓️ Pipeline Data Lineage Profile

The system dynamically documents data provenance from extraction source to model feature space inside `reports/data_lineage.json`.

### High-Level Lineage Mapping Flow
```text
[data/source/users.csv] (Raw Input)
           ↓
[data/raw/users/2026-07-12/users.csv] (Lake Landing Zone)
           ↓
[data/validated/users/users.csv] (Passed Structural Constraints)
           ↓
[data/processed/users/users.csv] (Deduplicated + Min-Max Normalized)
           ↓
[dim_users Table (recomart_warehouse.db)] (SQL Database Warehouse)
           ↓
[user_features:[id] Table] (Online serving Cache Layer)
```

### Generated Deliverables
*   **Central Audit Lineage Manifest Map:** `reports/data_lineage.json`
