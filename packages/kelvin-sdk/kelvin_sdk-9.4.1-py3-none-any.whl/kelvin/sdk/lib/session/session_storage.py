import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml
from platformdirs import user_config_dir
from pydantic import ValidationError

from kelvin.sdk.lib.models.generic import KPath, KSDKModel
from kelvin.sdk.lib.utils.logger_utils import logger

KSDK_CONFIG_SUBDIR = "kelvin"
SESSION_CONFIG_FILE = "session.yaml"
METADATA_FILE = "metadata.json"


class SessionConfig(KSDKModel):
    class Config:
        extra = "allow"

    url: Optional[str] = None
    ksdk_minimum_version: Optional[str] = None
    ksdk_latest_version: Optional[str] = None
    last_login: Optional[datetime] = None
    docker_minimum_version: Optional[str] = None
    docker_url: Optional[str] = None
    docker_port: Optional[int] = None


def session_config_from_metadata(metadata_json: dict) -> SessionConfig:
    url = metadata_json.get("core-api", {}).get("url")
    min_version = metadata_json.get("sdk", {}).get("ksdk_minimum_version")
    latest_version = metadata_json.get("sdk", {}).get("ksdk_latest_version")
    last_login = datetime.now()
    docker_minimum_version = metadata_json.get("sdk", {}).get("docker_minimum_version", {})
    docker_url = metadata_json.get("docker", {}).get("url", {})
    docker_port = metadata_json.get("docker", {}).get("port", {})

    return SessionConfig(
        url=url,
        ksdk_minimum_version=min_version,
        ksdk_latest_version=latest_version,
        last_login=last_login,
        docker_minimum_version=docker_minimum_version,
        docker_url=docker_url,
        docker_port=docker_port,
    )


def store_session(session_conf: SessionConfig) -> None:
    """Store session configuration"""

    config_dir = KPath(user_config_dir(KSDK_CONFIG_SUBDIR))
    session_file = config_dir / SESSION_CONFIG_FILE

    session_conf.to_file(session_file, sort_keys=False)


def load_session() -> Optional[SessionConfig]:
    """Load session configuration"""

    config_dir = KPath(user_config_dir(KSDK_CONFIG_SUBDIR))
    session_file = config_dir / SESSION_CONFIG_FILE

    if not session_file.exists():
        return None

    try:
        return SessionConfig.from_yaml(session_file)
    except (yaml.YAMLError, ValidationError) as e:
        logger.warning(f"Failed to parse session config: {e}")
        return None


def clear_session() -> None:
    """Clear session configuration"""

    config_dir = Path(user_config_dir(KSDK_CONFIG_SUBDIR))
    session_file = config_dir / SESSION_CONFIG_FILE
    session_file.unlink(missing_ok=True)


def store_metadata(metadata_json: dict) -> None:
    """Store metadata configuration"""

    config_dir = Path(user_config_dir(KSDK_CONFIG_SUBDIR))
    metadata_file = config_dir / METADATA_FILE

    with metadata_file.open("w") as f:
        json.dump(metadata_json, f)


def load_metadata() -> Optional[dict]:
    """Load metadata configuration"""

    config_dir = Path(user_config_dir(KSDK_CONFIG_SUBDIR))
    metadata_file = config_dir / METADATA_FILE

    if not metadata_file.exists():
        return None

    try:
        with metadata_file.open("r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse metadata config: {e}")
        return None


def clear_metadata() -> None:
    """Clear metadata configuration"""

    config_dir = Path(user_config_dir(KSDK_CONFIG_SUBDIR))
    metadata_file = config_dir / METADATA_FILE
    metadata_file.unlink(missing_ok=True)
