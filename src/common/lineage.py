import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Resolve project paths
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from common.logger import logger

class IngestionLineageTracker:
    """Records the chronological transformation history and lineage of data assets."""
    
    def __init__(self):
        self.project_root = Path(src_dir).parent
        self.lineage_json = self.project_root / "reports" / "data_lineage.json"
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)

    def log_lineage_run(self):
        logger.info("Compiling project data lineage graph map...", extra={"pipeline_step": "LINEAGE_MAP"})
        
        # Define the deterministic data lineage map of your system architecture
        lineage_graph = {
            "pipeline_name": "recomart_recommendation_pipeline",
            "metadata_version": "1.0.0",
            "last_audit_timestamp": datetime.now(timezone.utc).isoformat(),
            "data_versioning_tool": "Git LFS (Large File Storage)",
            
            "lineage_tracks": {
                "user_behavioral_features": {
                    "source_node": "data/source/users.csv",
                    "ingestion_landing_zone": "data/raw/users/[date]/users.csv",
                    "validation_gate": "data/validated/users/users.csv",
                    "preparation_transformations": [
                        "Deduplication via user_id",
                        "Median Imputation on null age rows",
                        "Label Encoding on categorical values (gender, membership, segment)",
                        "Min-Max Normalization on numerical age features"
                    ],
                    "processed_staging": "data/processed/users/users.csv",
                    "warehouse_destination_table": "dim_users (recomart_warehouse.db)",
                    "engineered_features": ["user_activity_frequency", "user_avg_rating"],
                    "feature_store_serving_key": "user_features:[user_id] (online_feature_cache)"
                },
                
                "product_catalog_features": {
                    "source_node": "data/source/products.csv",
                    "ingestion_landing_zone": "data/raw/products/[date]/products.csv",
                    "validation_gate": "data/validated/products/products.csv",
                    "preparation_transformations": [
                        "Deduplication via product_id",
                        "Median Imputation on null price values",
                        "Label Encoding on category and brand",
                        "Log Normalization on variable pricing scales"
                    ],
                    "processed_staging": "data/processed/products/products.csv",
                    "warehouse_destination_table": "dim_products (recomart_warehouse.db)",
                    "engineered_features": ["item_avg_rating", "item_interaction_count"],
                    "feature_store_serving_key": "product_features:[product_id] (online_feature_cache)"
                }
            }
        }
        
        # Save the lineage manifest file to disk
        with open(self.lineage_json, "w", encoding="utf-8") as f:
            json.dump(lineage_graph, f, indent=2)
            
        print("\n" + "="*50)
        print("⛓️ DATA LINEAGE MANIFEST RECORDED SUCCESSFULLY")
        print("="*50)
        print(f"🔹 Versioning Provider    : Git LFS")
        print(f"🔹 Monitored Lineage Paths : {len(lineage_graph['lineage_tracks'])}")
        print(f"🔹 Output Audit Manifest  : reports/data_lineage.json")
        print("="*50 + "\n")

if __name__ == "__main__":
    tracker = IngestionLineageTracker()
    tracker.log_lineage_run()
