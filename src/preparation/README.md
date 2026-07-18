# Task 5 — Data Preparation Layer

## Objective

This layer takes structurally sound datasets from `data/validated/` and transforms them into an optimized state for recommendation models. Here, the pipeline performs necessary modifications, including structural deduplication, variable scaling, missing value imputation, and category conversion.

## Key Operations Performed
1.  **Deduplication & Cleaning:** Drops duplicate entities across critical index bounds (e.g., ensuring `user_id` and `product_id` keys are completely unique).
2.  **Imputation of Missing Values:** Protects algorithms against matrix sparsity by dynamically filling null rows using median distributions or fallback category metrics.
3.  **Categorical Attribute Encoding:** Transforms descriptive text definitions (such as `gender`, `membership`, or product `category`) into numeric labels using category code mapping.
4.  **Numerical Normalization:** Formats highly skewed scales (such as performing **Min-Max Scaling** on ages/session durations and applying a **Log Transformation** to prices) to optimize model performance.
5.  **Chronological Transformations:** Parses raw textual timestamp strings into structured year/month fields for time-series splits.

| Transformation | Applied |
|---------------|---------|
| Deduplication | ✓ |
| Missing values | ✓ |
| Scaling | ✓ |
| Encoding | ✓ |
| Date parsing | ✓ |


## Execution & Automation
Run the data preparation pipeline from the root directory:
```bash
python src/preparation/preparation_runner.py
```

## Generated Deliverables
```text
data/validated/ (Clean Input)
       ↓
[preparation_runner.py Engine]
       ↓
data/processed/ (Deduplicated, Encoded, and Normalized Matrix Output)
```
