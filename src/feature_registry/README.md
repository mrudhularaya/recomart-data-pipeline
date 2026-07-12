# Task 7 — Custom Metadata Feature Store Registry Layer

## 🎯 Objective
This layer implements a lightweight, platform-independent, metadata-driven **Feature Store**. It registers engineered analytical columns directly from the SQLite Data Warehouse, provisions an active **Online Key-Value Cache** to feed real-time recommendation inference layers, and documents feature schemas within a central data catalog registry.

---

## 🏛️ System Core Framework Architecture

Following the Single Responsibility Principle, this feature store is divided into three cleanly decoupled modules:
*   `entities.py`: Central registration database for lookups or entity primary join keys (`user_id`, `product_id`).
*   `feature_views.py`: Architectural documentation catalog defining features, source data tables, and normalization transformations.
*   `materialize.py`: Operational execution manager that populates the online key-value tables and writes out the data catalog logs.

---

## 💾 Storage Layer Specifications & Serving Schema

To guarantee low-latency serving during model deployment, the materialization engine hooks straight into the SQLite data warehouse and constructs a specialized key-value storage layer:

```sql
CREATE TABLE IF NOT EXISTS online_feature_cache (
    feature_key TEXT PRIMARY KEY,       -- Composite serving format -> [view_name]:[entity_id]
    attribute_name TEXT,                -- The engineered feature variable name
    attribute_value TEXT,               -- The normalized/processed variable metric string
    last_synchronized TIMESTAMP         -- Chronological pipeline processing record tracker
);
```

### 📦 Central Data Catalog Sample Profile (`feature_registry.json`)
The catalog generates an audit trail listing our active definitions:
*   **`user_features`**: Tracks `user_activity_frequency` and `user_avg_rating` baselines linked to `user_id`.
*   **`product_features`**: Tracks `item_avg_rating` performance records and `item_interaction_count` metrics mapped to `product_id`.

---

## 🚀 Execution & Pipeline Orchestration

Execute the materialization synchronization routine directly from your project root folder path:
```bash
python src/feature_registry/materialize.py
```

### Expected Deliverable Output Targets
*   **Online Store Cache Table:** Populated natively inside `data/warehouse/recomart_warehouse.db`
*   **Central Governance Catalog:** Compiled at `data/warehouse/feature_registry.json`
