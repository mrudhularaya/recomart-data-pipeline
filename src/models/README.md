# Task 9 — Recommendation Model Training and MLflow Evaluation Layer

## 🎯 Objective
This layer handles the extraction of prepared features and transaction matrices from the SQLite Data Warehouse, executes baseline and personalized recommendation training loops using Scikit-Learn, calculates performance metrics, and tracks experiment states inside **MLflow**.

---

## 🏛️ Model Core Architectures

### 1. Popularity Baseline Recommender
*   **Logic:** Non-personalized catalog ranking. Sorts products using historical interaction counts weighted by overall mean rating scores.
*   **Purpose:** Establishes a performance baseline and handles cold-start scenarios for unengaged profiles.

### 2. Content-Based TF-IDF Similarity Recommender
*   **Logic:** Text-driven semantic mapping. Converts descriptive fields (`product_name` + `category`) into textual vectors using a Term Frequency-Inverse Document Frequency (**TF-IDF**) vectorizer. It then computes item similarity distances using **Cosine Similarity** to recommend products matching a user's purchase history.

---

## 📊 Experiment Tracking Specifications (MLflow)

The modeling loop leverages **MLflow** to maintain reproducibility and transparency. Every training sequence creates an immutable run capture logging parameters and metrics.

### Monitored Performance Metrics (K=5)
*   **Precision@K:** Measures the proportion of recommended items that match true user interactions.
*   **Recall@K:** Measures the proportion of true user interactions captured in the recommended list.

---

## 🚀 Execution & Tracking

Run the training pipeline directly from your project root workspace:
```bash
python src/models/train_eval.py
```

### Reviewing the MLflow UI
To open the interactive dashboard and compare parameter runs visually, execute this command in your project terminal and navigate to `http://localhost:5000` in your web browser:
```bash
mlflow ui
```

### Generated Deliverables
*   **Local Experiment Tracking Storage Repository:** `mlruns/`
