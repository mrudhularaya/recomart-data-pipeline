# Task 10 — End-to-End Pipeline Orchestration Layer (Prefect)

## 🎯 Objective
This layer handles the orchestration and scheduling automation of the data pipeline. It leverages **Prefect** to construct an automated workflow that manages task states, handles retries, provides visibility into execution logs, and protects the system against data failure points on cross-platform architectures (Windows/macOS/Linux).

---

## 🧱 Workflow Orchestration Matrix

The operational flow uses a single master `@flow` manager control node that executes individual pipeline routines wrapped inside standalone `@task` operators:

1.  **`Data Ingestion & Staging`** (`ingest_task_node`): Extracts remote API payloads and internal tables, routing records out to the date-partitioned raw staging data lake. Features an automated recovery window (`retries=1`, `retry_delay=120s`).
2.  **`Data Profiling & Validation`** (`validate_task_node`): Runs structural schema integrity checks and format range audits, compiling the final Data Quality Report PDF.
3.  **`Data Preparation & Imputation`** (`prepare_task_node`): Automatically applies deduplication rules, executes null-value median imputations, handles category string label encodings, and scales numerical metrics.
4.  **`Feature Engineering & SQL Warehouse Load`** (`feature_task_node`): Builds aggregate behavioral tracking values (user activity frequencies, average ratings) and commits rows to the SQLite Relational Warehouse tables.
5.  **`Recommendation Model Training & MLflow Tracking`** (`train_task_node`): Loads features from SQL, builds popularity and text-similarity recommenders, verifies predictions, and logs runs inside **MLflow**.

---

## 🏛️ Flow Topology Definition
```text
[Ingestion Task] ➔ [Validation Task] ➔ [Preparation Task] ➔ [Features Task] ➔ [Model Suite Task]
```

## 🚀 Execution & UI Dashboard
To run the automated data pipeline locally:
```bash
python src/orchestration/recomart_dag.py
```

### Reviewing the Local Web Dashboard UI
Prefect includes a graphical web console. To launch the server locally and visually track task runs, success matrices, and flow durations, run this command in a separate terminal tab and open `http://127.0.0.1:4200` in your web browser:
```bash
prefect server start
```
