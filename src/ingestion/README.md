# Recomart Data Ingestion Engine & Storage Layer (Tasks 2 & 3)

A highly scalable, production-ready data ingestion pipeline built following the **Single Responsibility Principle (SRP)**. The system handles modular extraction routines for local CSV datasets and external REST API integrations, tracking workflows through structured JSON audit logs, and staging payloads into an organized local Data Lake.

---

## 🏛️ Project Directory Structure

The system enforces a clean, modular hierarchy dividing configurations, utilities, structural source targets, and multi-tier destination directories:

```text
recomart-task2-task3/
│
├── config/
│   └── config.yaml            # Central pipeline parameters & dataset path definitions
│
├── data/
│   ├── source/                # Landing pad for incoming/unprocessed source files
│   │   ├── users.csv
│   │   ├── products.csv
│   │   ├── reviews.csv
│   │   ├── sessions.csv
│   │   └── clickstream.csv
│   │
│   ├── raw/                   # Internal Data Lake: Partitioned business objects
│   │   └── [dataset_name]/[YYYY-MM-DD]/[dataset_name].csv
│   │
│   └── external/              # External Data Lake: Vendor API response stream drops
│       └── [api_name]/[YYYY-MM-DD]/[api_name].json
│
├── logs/                      # Audit trails destination
│   └── ingestion.log
│
└── src/
    ├── common/
    │   ├── __init__.py
    │   ├── config.py          # Dynamic absolute path YAML loader
    │   └── logger.py          # Structured JSON log formatter
    │
    └── ingestion/
        ├── __init__.py
        ├── csv_ingestor.py    # Class: Read CSV -> Memory (Pandas DataFrame)
        ├── api_ingestor.py    # Class: HTTP GET -> JSON with Timeout & Retries
        ├── raw_storage.py     # Class: Data Lake Storage Manager
        └── run_ingestion.py   # The Conductor: Orchestration & Routine Execution
```

---

## 🛠️ Setup & Installation

### 1. Install Dependencies
Ensure you have Python 3.10+ installed. Install required packages using `pip`:
```bash
pip install -r requirements.txt
```

### 2. Populate Source Data
Place your source files (`users.csv`, `products.csv`, etc.) inside the `data/source/` directory as specified in `config/config.yaml`.

---

## 🚀 Execution & Automation

Run the master orchestrator script directly from your project root folder:
```bash
python src/ingestion/run_ingestion.py
```

### 🕒 Periodic Automation
Because the pipeline reads parameters dynamically from a standalone configuration file and runs via a single master execution script, it can be scheduled periodically using native system schedulers without altering code:
*   **Linux/macOS (Cron):** Schedule a cronjob (`crontab -e`) to execute the runner daily or hourly.
*   **Windows (Task Scheduler):** Point a Basic Task action directly to your Python executable and pass `src/ingestion/run_ingestion.py` as an argument.

---

## 📦 Core Architecture & Feature Matrix

### 🔄 Data Collection & Ingestion (Task 2)
*   **Multi-Source Processing:** Extracts internal application tables via local CSV streams and calls public web servers using explicit REST connectors.
*   **Resiliency Layer:** The `APIIngestor` features standard network timeouts (`30s`) and defensive error-catching. It automatically handles failure points via a **Max Retries loop** backed by an **Exponential Backoff mechanism** (`time.sleep(2 ** attempt)`).
*   **Defensive Loops:** The orchestrator runs individual extraction jobs inside isolated blocks. If one dataset or URL crashes, the engine logs the event and safely continues processing the next dataset.

### 💾 Raw Data Storage Layer (Task 3)
*   **Logical Partitioning:** Payloads are isolated by data origin bounds. Tabular file conversions are mapped to `data/raw/` while raw JSON API outputs drop under `data/external/`.
*   **Temporal Partitions:** The `RawStorage` system reads files and appends automated, chronological subdirectories using the `YYYY-MM-DD` execution date.

### 📝 Audit Trails & Monitoring
All activities yield machine-readable, single-line **Structured JSON Logs** to standard output. This layout ensures logs are instantly parseable by modern log-management stacks (e.g., Datadog, ELK, AWS CloudWatch).

#### Log Format Sample:
```json
{"timestamp": "2026-07-12T14:52:22.719Z", "level": "INFO", "logger": "data_ingestion", "message": "Conductor initializing with separate storage outputs...", "pipeline_step": "START"}
{"timestamp": "2026-07-12T14:52:22.745Z", "level": "INFO", "logger": "data_ingestion", "message": "Reading CSV file into memory: users.csv", "pipeline_step": "CSV_EXTRACT"}
{"timestamp": "2026-07-12T14:52:22.843Z", "level": "INFO", "logger": "data_ingestion", "message": "Staged dataset to RAW lake zone: C:\\...\\data\\raw\\users\\2026-07-12\\users.csv"}
{"timestamp": "2026-07-12T14:52:24.464Z", "level": "INFO", "logger": "data_ingestion", "message": "Staged API response to EXTERNAL zone: C:\\...\\data\\external\\products_api\\2026-07-12\\products_api.json"}
{"timestamp": "2026-07-12T14:52:24.464Z", "level": "INFO", "logger": "data_ingestion", "message": "Ingestion cycle complete.", "pipeline_step": "COMPLETE"}
```
