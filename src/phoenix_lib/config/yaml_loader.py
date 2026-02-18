"""YAML configuration loader shared across Phoenix services."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)

CONFIG_FILE_ENV_VAR = "APP_CONFIG_PATH"


def load_yaml_config(
    local_path: Optional[Path] = None,
    docker_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Load configuration from a YAML file if available.

    Looks for config in the following order:
    1. ``APP_CONFIG_PATH`` environment variable
    2. ``docker_path`` if provided and exists (e.g. ``/app/config/config.yaml``)
    3. ``local_path`` if provided (e.g. ``config/config.yaml`` relative to project)

    Returns an empty dict if no file is found or if the file is empty.

    Args:
        local_path: Path to the local development config file.
        docker_path: Path inside a Docker container (checked first after env var).

    Returns:
        Dictionary of configuration values, or ``{}`` on missing/empty file.
    """
    config_file_env = os.getenv(CONFIG_FILE_ENV_VAR)
    if config_file_env:
        config_path: Optional[Path] = Path(config_file_env)
    elif docker_path and docker_path.exists():
        config_path = docker_path
    elif local_path:
        config_path = local_path
    else:
        config_path = None

    if config_path is None or not config_path.exists():
        logger.debug("Config file not found, using defaults")
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            config_data = yaml.safe_load(config_file)
        if config_data is None:
            return {}
        logger.info("Loaded configuration from %s", config_path)
        return config_data
    except yaml.YAMLError as e:
        logger.error("Error parsing YAML config %s: %s", config_path, e)
        return {}
    except IOError as e:
        logger.error("Error reading config file %s: %s", config_path, e)
        return {}
