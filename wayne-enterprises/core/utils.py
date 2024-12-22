import json
import logging
from pathlib import Path

def load_config(config_file: str = 'config/settings.json') -> dict:
    """Load configuration from JSON file"""
    with open(config_file, 'r') as f:
        return json.load(f)

def setup_logging(config_file: str = 'config/logging.json'):
    """Setup logging configuration"""
    import logging.config
    logging.config.dictConfig(json.load(open(config_file)))
