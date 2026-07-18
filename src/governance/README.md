# Data Versioning & Lineage

## Overview

This module provides governance capabilities for the RecoMart recommendation pipeline by recording data lineage information for every pipeline execution. It maintains an audit trail of datasets as they move through ingestion, validation, preparation, feature engineering, and model training.

The lineage manifest improves reproducibility, traceability, and debugging by documenting the origin, transformation stages, and output artifacts generated during the pipeline.

## Inputs

The module reads metadata from pipeline outputs including:

```
data/raw/
data/validated/
data/prepared/
warehouse/
artifacts/
```

## Outputs

The module generates:

```
reports/
└── data_lineage.json
```

This JSON document contains metadata describing the execution lineage of the pipeline.

## Lineage Flow

```
Raw Data
    │
    ▼
Validation
    │
    ▼
Preparation
    │
    ▼
Feature Engineering
    │
    ▼
SQLite Warehouse
    │
    ▼
Feature Store
    │
    ▼
Model Training
    │
    ▼
Prediction Artifacts
```

## Generated Metadata

The lineage manifest includes information such as:

- Pipeline execution timestamp
- Source datasets
- Processing stages executed
- Output datasets
- Generated artifacts
- Storage locations
