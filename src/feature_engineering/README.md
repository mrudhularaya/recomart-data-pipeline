# Task 6 — Feature Engineering and Transformation

## Objective

This layer calculates behavioral interaction features from your prepared datasets to feed collaborative filtering and recommendation engines. Once these metrics are generated, the engine maps the tables into a structured relational **SQLite Database Warehouse** for persistent storage.

## Engineered Feature Matrix
The system applies aggregate grouping operations across interaction paths to extract three core feature pillars:
*   **User Activity Frequency:** Aggregates cumulative clickstream interaction sequences per `user_id` to establish activity baseline vectors.
*   **User Average Rating:** Computes individual user rating averages to evaluate personal grading skewness.
*   **Item Average Rating & Popularity Count:** Evaluates product baseline profiles by tracking total interaction volume alongside overall mean score ratings.

## Relational Warehouse Schema (DDL)
The pipeline automatically compiles a Star Schema within an indexed SQLite database file container:
*   `dim_users`: Stores static profiles paired with engineered activity and score metrics.
*   `dim_products`: Captures stock attributes combined with aggregate performance ratings and review counts.
*   `fact_interactions`: Maps active link interactions (`review_id`, `user_id`, `product_id`, `rating`) to tie dimension fields together.

## Execution & Automation
To run feature generation algorithms and compile the warehouse database:
```bash
python src/feature_engineering/feature_runner.py
```

### Generated Deliverables
*   **SQLite Relational Warehouse Instance:** `data/warehouse/recomart_warehouse.db`
