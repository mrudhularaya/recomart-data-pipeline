"""Materialize versioned feature values and retrieve them for training or inference."""

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from common.logger import logger
from feature_registry.feature_views import product_features_view, user_features_view


class RecomartFeatureStore:
    def __init__(self):
        self.project_root = Path(src_dir).parent
        self.warehouse_db = self.project_root / "data" / "warehouse" / "recomart_warehouse.db"
        self.registry_json = self.project_root / "data" / "warehouse" / "feature_registry.json"

    @staticmethod
    def _create_online_schema(conn: sqlite3.Connection) -> None:
        required_columns = {"feature_view", "entity_id", "attribute_name", "attribute_value", "feature_version", "materialized_at"}
        existing_columns = {row[1] for row in conn.execute("PRAGMA table_info(online_feature_cache)")}
        if existing_columns and existing_columns != required_columns:
            # Migrate the incompatible v1 cache; its contents are derived and rebuilt below.
            conn.execute("DROP TABLE online_feature_cache")
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS online_feature_cache (
                feature_view TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                attribute_name TEXT NOT NULL,
                attribute_value TEXT,
                feature_version TEXT NOT NULL,
                materialized_at TEXT NOT NULL,
                PRIMARY KEY (feature_view, entity_id, attribute_name, feature_version)
            );
            CREATE INDEX IF NOT EXISTS idx_feature_lookup
                ON online_feature_cache (feature_view, entity_id, materialized_at DESC);
        """)

    def materialize_store(self, feature_version: Optional[str] = None) -> Dict[str, int | str]:
        if not self.warehouse_db.exists():
            raise FileNotFoundError(f"SQLite Warehouse missing at {self.warehouse_db}")
        feature_version = feature_version or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        materialized_at = datetime.now(timezone.utc).isoformat()
        views = [user_features_view, product_features_view]

        with sqlite3.connect(self.warehouse_db) as conn:
            self._create_online_schema(conn)
            total = 0
            for view in views:
                cursor = conn.execute(f"SELECT * FROM {view.source_table}")
                columns = [column[0] for column in cursor.description]
                for row in cursor.fetchall():
                    record = dict(zip(columns, row))
                    entity_id = str(record[view.join_key])
                    values = [
                        (view.name, entity_id, feature, str(record.get(feature, "")), feature_version, materialized_at)
                        for feature in view.features
                    ]
                    conn.executemany("INSERT OR REPLACE INTO online_feature_cache VALUES (?, ?, ?, ?, ?, ?)", values)
                    total += len(values)

        registry = {
            "feature_store_project": "recomart_pipeline",
            "metadata_version": "2.0.0",
            "last_materialization_timestamp": materialized_at,
            "latest_feature_version": feature_version,
            "retrieval": {
                "training": "retrieve_features(view_name, entity_id, feature_version=<version>)",
                "inference": "retrieve_features(view_name, entity_id) returns the latest materialization",
            },
            "registry": {
                view.name: {
                    "description": view.description,
                    "underlying_source_table": view.source_table,
                    "join_identifier_key": view.join_key,
                    "schema_documentation": view.features,
                } for view in views
            },
        }
        with open(self.registry_json, "w", encoding="utf-8") as file:
            json.dump(registry, file, indent=2)
        logger.info(f"Materialized {total} versioned feature values", extra={"pipeline_step": "STORE_COMPLETE"})
        return {"feature_version": feature_version, "feature_values": total}

    def retrieve_features(self, view_name: str, entity_id: str, feature_version: Optional[str] = None) -> Dict[str, str]:
        """Return a complete entity feature vector, latest by default or from a named version."""
        with sqlite3.connect(self.warehouse_db) as conn:
            if feature_version:
                rows = conn.execute(
                    "SELECT attribute_name, attribute_value FROM online_feature_cache "
                    "WHERE feature_view = ? AND entity_id = ? AND feature_version = ?",
                    (view_name, str(entity_id), feature_version),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT attribute_name, attribute_value FROM online_feature_cache "
                    "WHERE feature_view = ? AND entity_id = ? AND materialized_at = ("
                    "SELECT MAX(materialized_at) FROM online_feature_cache WHERE feature_view = ? AND entity_id = ?)",
                    (view_name, str(entity_id), view_name, str(entity_id)),
                ).fetchall()
        return dict(rows)


if __name__ == "__main__":
    store = RecomartFeatureStore()
    result = store.materialize_store()
    print(json.dumps(result, indent=2))
