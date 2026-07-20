import logging
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# src/common/logger.py
class JSONFormatter(logging.Formatter):
    """Custom formatter to output logs in a clean structured JSON format."""
    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Inject custom contextual fields if provided via 'extra'
        if hasattr(record, "pipeline_step"): log_data["pipeline_step"] = record.pipeline_step
        if hasattr(record, "batch_id"): log_data["batch_id"] = record.batch_id
        
        # CLEAN UP VERBOSITY: Extract just the type and message instead of the whole trace
        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            log_data["exception"] = f"{exc_type.__name__}: {str(exc_value)}"
            
        return json.dumps(log_data)

def _setup_logger():
    """Initializes and returns the singleton logger instance."""
    logger_name = "recomart_pipeline"
    _logger = logging.getLogger(logger_name)
    _logger.setLevel(logging.INFO)
    
    if _logger.hasHandlers():
        return _logger

    # Resolve path relative to this file: common/logger.py -> ../../../logs
    log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / "ingestion.log"

    json_formatter = JSONFormatter()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    _logger.addHandler(console_handler)

    # File Handler (pointing to the resolved logs path)
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(json_formatter)
    _logger.addHandler(file_handler)

    return _logger

# Instantiate the logger directly for import access
logger = _setup_logger()
