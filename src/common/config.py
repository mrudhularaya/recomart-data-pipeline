import yaml
from pathlib import Path
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Locates and parses the root config.yaml file into a dictionary."""
    # common/config.py -> .parent is common/ -> .parent.parent.parent is root folder
    root_dir = Path(__file__).resolve().parent.parent.parent
    config_path = root_dir / "config" / "config.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file missing at expected path: {config_path}")
        
    with open(config_path, "r", encoding="utf-8") as file:
        # Safe Loader prevents execution of arbitrary code embedded in YAML files
        config_data = yaml.safe_load(file)
        
    return config_data if config_data is not None else {}
