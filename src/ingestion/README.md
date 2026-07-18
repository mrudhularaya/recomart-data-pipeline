# Tasks 2 & 3 — Data Collection and Ingestion & Raw Data Storage

## Objective

A data ingestion that handles modular extraction routines for local CSV datasets and external REST API integrations, tracking workflows through structured JSON audit logs, and staging payloads into an organized local Data Lake.

## Core Architecture & Feature Matrix

### Data Collection & Ingestion (Task 2)
*   **Multi-Source Processing:** Extracts internal application tables via local CSV streams and calls public web servers using explicit REST connectors.
*   **Resiliency Layer:** The `APIIngestor` features standard network timeouts (`30s`) and defensive error-catching. It automatically handles failure points via a **Max Retries loop** backed by an **Exponential Backoff mechanism** (`time.sleep(2 ** attempt)`).
*   **Defensive Loops:** The orchestrator runs individual extraction jobs inside isolated blocks. If one dataset or URL crashes, the engine logs the event and safely continues processing the next dataset.

### Raw Data Storage Layer (Task 3)
*   **Logical Partitioning:** Payloads are isolated by data origin bounds. Tabular file conversions are mapped to `data/raw/` while raw JSON API outputs drop under `data/external/`.
*   **Temporal Partitions:** The `RawStorage` system reads files and appends automated, chronological subdirectories using the `YYYY-MM-DD` execution date.

## Execution & Automation

Run the master orchestrator script directly from your project root folder:
```bash
python src/ingestion/run_ingestion.py
```

## Generated Deliverables
### Inputs 

```bash
data/source/
```

### Outputs 

```bash
data/raw/
data/external/
```

#### Log Format Sample:
```json
{"timestamp": "2026-07-12T14:52:22.719Z", "level": "INFO", "logger": "data_ingestion", "message": "Conductor initializing with separate storage outputs...", "pipeline_step": "START"}
{"timestamp": "2026-07-12T14:52:22.745Z", "level": "INFO", "logger": "data_ingestion", "message": "Reading CSV file into memory: users.csv", "pipeline_step": "CSV_EXTRACT"}
{"timestamp": "2026-07-12T14:52:22.843Z", "level": "INFO", "logger": "data_ingestion", "message": "Staged dataset to RAW lake zone: C:\\...\\data\\raw\\users\\2026-07-12\\users.csv"}
{"timestamp": "2026-07-12T14:52:24.464Z", "level": "INFO", "logger": "data_ingestion", "message": "Staged API response to EXTERNAL zone: C:\\...\\data\\external\\products_api\\2026-07-12\\products_api.json"}
{"timestamp": "2026-07-12T14:52:24.464Z", "level": "INFO", "logger": "data_ingestion", "message": "Ingestion cycle complete.", "pipeline_step": "COMPLETE"}
```
