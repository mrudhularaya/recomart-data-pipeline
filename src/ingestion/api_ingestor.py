import time
import requests
from typing import Dict, Any
from pathlib import Path
import sys

# Resolves the root to help import modules
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from common.logger import logger

class APIIngestor:
    """Fetches data from an HTTP GET endpoint with retry logic and timeouts."""
    
    def __init__(self, timeout_seconds: int = 30, max_retries: int = 3):
        self.timeout = timeout_seconds
        self.max_retries = max_retries

    def ingest(self, url: str) -> Dict[str, Any]:
        logger.info(f"Initiating HTTP GET request to endpoint: {url}", extra={"pipeline_step": "API_EXTRACT"})
        
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status() # Raise exception for bad status codes (4xx, 5xx)
                
                # Raw extraction target reached
                return response.json()
                
            except requests.RequestException as e:
                logger.warning(
                    f"API request attempt {attempt}/{self.max_retries} failed: {str(e)}", 
                    extra={"pipeline_step": "API_RETRY"}
                )
                if attempt == self.max_retries:
                    logger.critical(f"All {self.max_retries} API retry attempts exhausted.", extra={"pipeline_step": "API_FAIL"})
                    raise e
                time.sleep(2 ** attempt) # Exponential backoff delay
