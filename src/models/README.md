# Task 9 — Model Training and Evaluation

## Objective
This layer extracts prepared feature matrices and interaction logs from the SQLite Data Warehouse, runs aggregate popularity baseline and personalized content-based recommendation training loops, calculates execution metrics, and logs execution parameters into **MLflow**.

## Decoupled Architectural Design

Following the Single Responsibility Principle, the modeling codebase is divided into four single-purpose modules:
*   `popularity.py`: Implements non-personalized baseline rankings based on interaction velocity and average item scores.
*   `content_based.py`: Handles high-dimensional Natural Language Processing (NLP) text vectorization and proximity calculations.
*   `evaluator.py`: A pure mathematical module tasked with computing accuracy dimensions over predicted recommendation arrays.
*   `trainer.py`: The master conductor that coordinates data streams, initializes MLflow contexts, and executes the processing loops.

## Model Core Architectures

### 1. Popularity Baseline Recommender (`popularity.py`)
*   **Logic:** Non-personalized catalog sorting. Orders item nodes using historical review volume (`item_interaction_count`) combined with average product ratings (`item_avg_rating`).

### 2. Content-Based TF-IDF Similarity Recommender (`content_based.py`)
*   **Logic:** Text-driven semantic proximity mapping. Combines descriptive columns (`product_name` + `category` + `description`) into a unified text metadata block. It converts text phrases into numerical vectors using a Term Frequency-Inverse Document Frequency (**TF-IDF**) vectorizer and calculates textual distances via **Cosine Similarity** to suggest items similar to a user's past purchases.


## Experiment Tracking Specifications (MLflow)

The pipeline integrates **MLflow** to maintain execution traceability. Every training cycle generates an unchangeable run tracking parameters and metrics.

### Monitored Performance Metrics (K=5)
*   **Precision@K:** Evaluates prediction precision by calculating the ratio of recommended items that match true historical user transactions.
*   **Recall@K:** Evaluates prediction coverage by tracking the proportion of total true user interactions successfully captured inside the recommended list.

## Inputs
```bash
SQLite Warehouse
```

## Outputs
```bash
mlruns/
artifacts/recommendations.json
```

## Execution & Automation

Run the master training orchestrator directly from your project root workspace:
```bash
python src/models/trainer.py
```

## Generated Deliverables
*   **Decoupled Model Packages:** `popularity.py`, `content_based.py`, `evaluator.py`, `trainer.py`
*   **Local Experiment Tracking Storage Repository:** `mlruns/`
