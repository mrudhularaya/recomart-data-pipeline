import sys
from pathlib import Path
import time

# Resolves the root to help import modules
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from common.config import load_config
from common.logger import logger
from ingestion.csv_ingestor import CSVIngestor
from ingestion.api_ingestor import APIIngestor
from ingestion.raw_storage import RawStorage

def main():
    logger.info("Conductor initializing with metrics tracking...", extra={"pipeline_step": "START"})
    pipeline_start = time.perf_counter()
    
    # Initialize Summary Metrics counters
    csv_count = 0
    api_count = 0
    total_records = 0
    failures = 0

    try:
        config = load_config()
        project_root = Path(src_dir).parent
        
        raw_path = config.get("raw_storage", {}).get("root", "data/raw/")
        storage_vault = RawStorage(raw_root=raw_path, external_root="data/external/")
        csv_worker = CSVIngestor()
        
        # --- PHASE 1: DATASETS LOOP ---
        datasets = config.get("datasets", {})
        for dataset_name, properties in datasets.items():
            source_file = project_root / properties.get("path")
            
            try:
                df_payload = csv_worker.ingest(str(source_file))
                storage_vault.save_dataset(df_payload, dataset_name=dataset_name)
                
                # Aggregate metrics
                csv_count += 1
                total_records += len(df_payload)
            except Exception as e:
                logger.error(f"Failed to process dataset [{dataset_name}]: {str(e)}", exc_info=True)
                failures += 1
                continue

        # --- PHASE 2: API PIPELINE ---
        api_url = config.get("external_api", {}).get("url")
        if api_url:
            try:
                api_worker = APIIngestor(timeout_seconds=30, max_retries=3)
                api_payload = api_worker.ingest(api_url)
                storage_vault.save_external_api(api_payload, endpoint_name="products_api")
                
                api_count += 1
                # Try to count nested entries for summary metrics
                if isinstance(api_payload, dict) and "products" in api_payload:
                    total_records += len(api_payload["products"])
                elif isinstance(api_payload, list):
                    total_records += len(api_payload)
            except Exception as e:
                logger.error(f"External API ingestion failed: {str(e)}", exc_info=True)
                failures += 1

        # --- PHASE 3: METRIC SUMMARY CARD GENERATION ---
        total_duration = round(time.perf_counter() - pipeline_start, 2)
        
        print("\n" + "="*50)
        print("📊 PIPELINE INGESTION SUMMARY")
        print("="*50)
        print(f"🔹 CSV datasets processed : {csv_count}")
        print(f"🔹 API datasets processed : {api_count}")
        print(f"🔹 Total records ingested : {total_records:,}")
        print(f"🔹 Processing failures   : {failures}")
        print(f"🔹 Total execution time  : {total_duration} sec")
        print("="*50 + "\n")

        logger.info("Ingestion cycle complete.", extra={"pipeline_step": "COMPLETE"})

    except Exception as system_crash:
        logger.critical(f"Critical Conductor failure: {str(system_crash)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
# src/validation/schema_validator.py
import pandas as pd
from typing import Dict, List, Tuple

class SchemaValidator:
    """Validates structural integrity and column presence of incoming datasets."""
    
    def __init__(self):
        self.expected_schemas: Dict[str, List[str]] = {
            "users": ["id", "name", "email"],
            "products": ["product_id", "title", "price"],
            "reviews": ["review_id", "product_id", "rating", "comment"],
            "sessions": ["session_id", "user_id", "duration"],
            "clickstream": ["event_id", "session_id", "action"]
        }

    def validate(self, df: pd.DataFrame, dataset_name: str) -> Tuple[bool, List[str]]:
        errors = []
        expected_cols = self.expected_schemas.get(dataset_name, [])
        
        if not expected_cols:
            return True, errors

        missing_cols = [col for col in expected_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Schema mismatch! Missing expected columns: {missing_cols}")
            
        return len(errors) == 0, errors
