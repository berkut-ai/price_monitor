import json
import os
from logging.config import dictConfig
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def setup_logger() -> None:
    os.makedirs(BASE_DIR / "logs", exist_ok=True)
    with open(BASE_DIR / "src/logging_settings/logging_config.json") as conf_f:
        CONFIG = json.load(conf_f)
        CONFIG["handlers"]["file_handler"]["filename"] = BASE_DIR / "logs/app.log"

    dictConfig(CONFIG)