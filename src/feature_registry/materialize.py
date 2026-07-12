import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

# Resolve global packages structure path context
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from common.logger import logger
from feature_registry.feature_views import user_features_view, product_features_view

class RecomartFeatureStore:
    """A high-performance custom Feature Store managing schema metadata and online caching."""
    
    def __init__(self):
        self.project_root = Path(src_dir).parent
        self.warehouse_db = self.project_root / "data" / "warehouse" / "recomart_warehouse.db"
        self.registry_json = self.project_root / "data" / "warehouse" / "feature_registry.json"
        
    def materialize_store(self):
        logger.info("Initializing Custom Feature Store Registry Engine...", extra={"pipeline_step": "STORE_START"})
        
        if not self.warehouse_db.exists():
            logger.critical(f"Aborting materialization: SQLite Warehouse missing at {self.warehouse_db}")
            return
            
        conn = sqlite3.connect(self.warehouse_db)
        cursor = conn.cursor()
        
        # --- REQUIREMENT: ENABLE FOR ONLINE INFERENCE IN REAL TIME ---
        # Create an ultra-fast Key-Value cache table directly inside the database warehouse.
        # This acts as a Feast-equivalent Online Store.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS online_feature_cache (
                feature_key TEXT PRIMARY KEY,
                attribute_name TEXT,
                attribute_value TEXT,
                last_synchronized TIMESTAMP
            )
        """)
        
        registered_views = [user_features_view, product_features_view]
        total_features_materialized = 0
        
        # Read from analytical columns and sync them to the real-time cache
        for view in registered_views:
            cursor.execute(f"SELECT * FROM {view.source_table}")
            
            # Extract column header strings dynamically
            columns = [col[0] for col in cursor.description]
            records = cursor.fetchall()
            
            for row in records:
                row_dict = dict(zip(columns, row))
                entity_key_value = str(row_dict.get(view.join_key))
                
                # Pivot structured table columns out into indexable feature keys
                for feature_name in view.features.keys():
                    if feature_name in row_dict:
                        # Construct a unique composite serving key (e.g., "user_features:usr_101")
                        composite_serving_key = f"{view.name}:{entity_key_value}"
                        feature_val = str(row_dict[feature_name])
                        
                        cursor.execute("""
                            INSERT OR REPLACE INTO online_feature_cache (feature_key, attribute_name, attribute_value, last_synchronized)
                            VALUES (?, ?, ?, ?)
                        """, (composite_serving_key, feature_name, feature_val, datetime.now(timezone.utc).isoformat()))
                        total_features_materialized += 1
                        
        conn.commit()
        conn.close()
        
        # --- REQUIREMENT: FEATURE METADATA DOCUMENTATION REGISTRY DELIVERABLE ---
        # Write out your configuration variables as a clean JSON log artifact.
        registry_log = {
            "feature_store_project": "recomart_pipeline",
            "metadata_version": "1.0.0",
            "last_materialization_timestamp": datetime.now(timezone.utc).isoformat(),
            "registry": {
                view.name: {
                    "description": view.description,
                    "underlying_source_table": view.source_table,
                    "join_identifier_key": view.join_key,
                    "schema_documentation": view.features
                } for view in registered_views
            }
        }
        
        with open(self.registry_json, "w", encoding="utf-8") as f:
            json.dump(registry_log, f, indent=2)
            
        # Display performance scorecard
        print("\n" + "="*50)
        print("⚡ RECOMART CUSTOM FEATURE STORE METADATA REGISTERED")
        print("="*50)
        print(f"🔹 Registered Feature Views     : {len(registered_views)}")
        print(f"🔹 Online Materialized Records  : {total_features_materialized:,}")
        print(f"🔹 Central Registry Documentation: data/warehouse/feature_registry.json")
        print(f"🔹 System Status                 : ONLINE & PROVISIONED")
        print("="*50 + "\n")
        
        logger.info("Custom Feature Store orchestration cycle completed successfully.", extra={"pipeline_step": "STORE_COMPLETE"})

if __name__ == "__main__":
    store = RecomartFeatureStore()
    store.materialize_store()
