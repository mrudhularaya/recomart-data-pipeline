# Task 4 — Data Profiling and Validation Layer

## 🎯 Objective
This layer implements automated data profiling and structural constraint checks on raw datasets landing inside the Data Lake staging area (`data/raw/`). Following the Single Responsibility Principle, this module only answers **"Is this data acceptable?"**—it deliberately does not perform data cleaning or variable manipulation.

## 🧱 Architectural Components
*   `schema_validator.py`: Asserts structural compliance by comparing incoming dataset columns against strict baseline signatures.
*   `quality_validator.py`: Evaluates rows for format anomalies, null distributions, and business constraint boundaries (e.g., matching the 1–5 review rating scale).
*   `validation_runner.py`: The orchestration conductor that scans the raw lake, executes tests, routes compliant datasets to `data/validated/`, and triggers report generation.
*   `report_generator.py`: Compiles JSON metrics into a professional, publication-ready Data Quality Report PDF.

## 📊 Automated Validation Rules Applied
*   **Users Schema:** Verifies columns and ensures `age` values fall within natural biological bounds ($0 \le \text{age} \le 120$).
*   **Products Schema:** Ensures `price` and `avg_rating` figures do not contain negative boundaries.
*   **Reviews Schema:** Strictly screens user-item interaction rankings against the assignment's defined $1 \text{ to } 5$ scale.
*   **Sessions Schema:** Identifies negative time tracking fields inside `session_duration_sec`.

## 🚀 Execution & Verification
To execute validation scripts and compile your quality scorecard:
```bash
python src/validation/validation_runner.py
```

### Generated Deliverables
*   **Staging Output Path:** `data/validated/[dataset_domain]/[dataset_domain].csv`
*   **JSON Audit Profile Matrix:** `reports/validation_report.json`
*   **Data Quality Report (PDF):** `reports/validation_report.pdf`
