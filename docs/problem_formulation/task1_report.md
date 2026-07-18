# Task 1 — Problem Formulation

## End-to-End Data Management Pipeline for a Recommendation System

### 1. Problem Definition

RecoMart is an e-commerce platform that aims to improve customer engagement and increase product sales through personalized product recommendations. As the platform grows, data is continuously generated from multiple operational systems including user interactions, product catalogs, customer reviews, browsing sessions, and external services. These datasets arrive in different formats, vary in quality, and require systematic processing before they can be used for machine learning.

The primary business challenge is to design and implement an automated, modular, and maintainable data management pipeline that continuously ingests data from multiple sources, validates data quality, prepares datasets for downstream processing, engineers recommendation features, trains recommendation models, and orchestrates the complete workflow with minimal manual intervention.

The proposed solution follows modern data engineering practices by integrating data ingestion, validation, preprocessing, feature engineering, feature management, experiment tracking, data lineage, and workflow orchestration into a single end-to-end pipeline.

---

## 2. Project Objectives

The objectives of the proposed solution are to:

- Develop an automated pipeline capable of ingesting data from multiple heterogeneous sources.
- Store incoming datasets using a structured, timestamp-partitioned data lake.
- Validate incoming datasets for schema consistency, completeness, duplicates, and business constraints.
- Prepare cleaned datasets suitable for downstream analytical and machine learning tasks.
- Engineer recommendation-specific features from user behaviour and product interactions.
- Store transformed datasets within a structured SQLite data warehouse.
- Implement a lightweight feature store supporting metadata management and versioned feature retrieval.
- Train baseline recommendation models while tracking experiments using MLflow.
- Maintain data lineage and versioning information for governance and reproducibility.
- Automate the complete workflow using Prefect orchestration.

---

## 3. Data Sources

The pipeline integrates both internal enterprise datasets and external API data.

| Data Source | Description | Key Attributes |
|-------------|-------------|----------------|
| Users | Customer demographic information | user_id, age, gender, membership |
| Products | Product catalogue | product_id, product_name, category, price, avg_rating |
| Reviews | Explicit user ratings | review_id, user_id, product_id, rating |
| Sessions | Browsing session information | session_id, user_id, session_duration_sec |
| Clickstream | User interaction events | user_id, product_id, timestamp, event_type |
| Product REST API | External product metadata | popularity indicators, additional product metadata |

These datasets collectively support both collaborative filtering and content-based recommendation models.

---

## 4. Expected Pipeline Outputs

The proposed pipeline generates several intermediate and final outputs throughout the data lifecycle.

### Data Outputs

- Timestamp-partitioned raw datasets stored in the local data lake.
- Validated datasets after schema and quality verification.
- Cleaned and preprocessed datasets ready for analytics.
- Engineered recommendation features.
- Structured SQLite data warehouse.
- Materialized online feature store.

### Machine Learning Outputs

- Popularity-based recommendation model.
- Content-based TF-IDF recommendation model.
- Recommendation inference artifact.
- MLflow experiment tracking records.

### Governance Outputs

- Data Quality Report (JSON and PDF).
- Data Lineage Manifest.
- Structured execution logs.
- Prefect orchestration execution logs.

---

## 5. Recommendation Pipeline

The proposed architecture follows a modular pipeline in which each stage has a single responsibility.

```
Data Sources
      │
      ▼
Data Collection & Ingestion
      │
      ▼
Raw Data Lake
      │
      ▼
Data Validation
      │
      ▼
Data Preparation
      │
      ▼
Feature Engineering
      │
      ▼
SQLite Data Warehouse
      │
      ▼
Feature Store
      │
      ▼
Model Training & Evaluation
      │
      ▼
MLflow + Lineage + Reports
```

The modular design improves maintainability, traceability, and scalability while ensuring that downstream machine learning components always operate on validated and reproducible datasets.

![Draw.io Architecture Diagram](architecture.drawio.png)


---

## 6. Model Evaluation Metrics

The recommendation models are evaluated using ranking-based metrics that measure recommendation quality.

| Metric | Purpose |
|---------|----------|
| Precision@K | Measures the proportion of recommended items that are relevant. |
| Recall@K | Measures the proportion of relevant items successfully recommended. |
| NDCG@K | Evaluates recommendation ranking quality by rewarding highly ranked relevant items. |

MLflow is used to record model parameters, evaluation metrics, execution timestamps, and experiment metadata to support reproducibility and comparison of different model runs.

---

## 7. Expected Outcomes

The proposed pipeline provides an end-to-end framework for managing recommendation system data, beginning with multi-source data ingestion and ending with automated model training and governance reporting. By integrating data validation, feature engineering, experiment tracking, feature management, and workflow orchestration, the solution demonstrates the principles of modern data management pipelines used in machine learning systems.

> *The implementation is developed using Python, Pandas, SQLite, Prefect, MLflow, Git LFS, and ReportLab, following a modular Single Responsibility Principle (SRP) architecture.*

