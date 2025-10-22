from kelvin.sdk.cli.version import __version__ as current_version
from kelvin.sdk.lib.configs.click_configs import color_formats as colors
from kelvin.sdk.lib.models.types import VersionStatus
from kelvin.sdk.lib.utils.logger_utils import logger
from kelvin.sdk.lib.utils.version_utils import assess_version_status

from .session_storage import SessionConfig


def warn_ksdk_version(session_conf: SessionConfig) -> None:
    if not session_conf.ksdk_minimum_version or not session_conf.ksdk_latest_version:
        return

    version_status = assess_version_status(
        current_version=current_version,
        minimum_version=session_conf.ksdk_minimum_version,
        latest_version=session_conf.ksdk_latest_version,
    )

    if version_status != VersionStatus.UP_TO_DATE:
        message = f"""The current SDK version is not the recommended for the current environment.
            {colors["reset"]}Current: {colors["red"]}{current_version}{colors["reset"]} Recommended: {colors["green"]}{session_conf.ksdk_latest_version}{colors["reset"]}
            If any problem, please consider updating the SDK.
        """
        logger.warning(message)
