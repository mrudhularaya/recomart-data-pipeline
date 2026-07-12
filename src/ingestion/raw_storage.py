import json
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

# Resolves the root to help import modules
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from common.logger import logger

class RawStorage:
    """Handles landing zones for internal raw data and outside external feeds."""
    
    def __init__(self, raw_root: str = "data/raw/", external_root: str = "data/external/"):
        self.project_root = Path(__file__).resolve().parent.parent.parent

        # Enforce explicit root boundaries
        self.raw_base = (self.project_root / raw_root).resolve()
        self.external_base = (self.project_root / external_root).resolve()
        
    def _get_current_date(self) -> str:
        """Returns today's date formatted string (e.g., '2026-07-12')."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def save_dataset(self, df: pd.DataFrame, dataset_name: str) -> Path:
        """Saves tabular data to data/raw/<dataset_name>/<date>/<dataset_name>.csv"""
        target_dir = self.raw_base / dataset_name / self._get_current_date()
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = target_dir / f"{dataset_name}.csv"
        df.to_csv(target_path, index=False)
        
        rows = len(df)
        # Displaying clean relative paths for easy review in outputs
        display_path = target_path.relative_to(self.project_root)
        logger.info(
            f"Saved {rows:,} rows to {display_path}", 
            extra={"pipeline_step": "RAW_SAVE", "records_processed": rows}
        )        
        return target_path

    def save_external_api(self, data: dict, endpoint_name: str) -> Path:
        """Saves JSON responses strictly into data/external/<endpoint_name>/<date>/<endpoint_name>.json"""
        target_dir = self.external_base / endpoint_name / self._get_current_date()
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = target_dir / f"{endpoint_name}.json"
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        display_path = target_path.relative_to(self.project_root)
        logger.info(
            f"Saved JSON payload response out to {display_path}", 
            extra={"pipeline_step": "EXTERNAL_SAVE"}
        )        
        return target_path
