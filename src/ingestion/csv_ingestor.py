import pandas as pd
from pathlib import Path
import sys

# Resolves the root to help import modules
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
    
from common.logger import logger

class CSVIngestor:
    """Reads a CSV file and converts it directly into a Pandas DataFrame."""
    
    def ingest(self, file_path: str) -> pd.DataFrame:
        resolved_path = Path(file_path).resolve()
        
        logger.info(
            f"Reading CSV file into memory: {resolved_path.name}", 
            extra={"pipeline_step": "CSV_EXTRACT"}
        )
        
        if not resolved_path.exists():
            raise FileNotFoundError(f"Target CSV file not found at: {resolved_path}")
            
        # Read and return DataFrame
        df = pd.read_csv(resolved_path)
        return df
