"""
Copyright 2021 Kelvin Inc.

Licensed under the Kelvin Inc. Developer SDK License Agreement (the "License"); you may not use
this file except in compliance with the License.  You may obtain a copy of the
License at

http://www.kelvininc.com/developer-sdk-license

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OF ANY KIND, either express or implied.  See the License for the
specific language governing permissions and limitations under the License.
"""

import getpass
import json
from typing import Optional, Tuple

import keyring

from kelvin.api.base.http_client.env_vars import EnvVars
from kelvin.sdk.lib.exceptions import KSDKFatal
from kelvin.sdk.lib.utils.logger_utils import logger


class CredentialManager:
    KEYRING_SERVICE_NAME = "kelvin:kelvin-sdk"
    KEYRING_USERNAME = "kelvin-sdk-credentials"

    """Credential resolution and storage"""

    def __init__(self) -> None:
        self._env_vars = EnvVars().KELVIN_CLIENT

    def resolve_credentials(
        self, url: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None
    ) -> Tuple[str, str, str]:
        """
        Resolve credentials from all sources in priority order: CLI args → env vars → keyring → prompt.

        Parameters
        ----------
        url : Optional[str]
            URL provided via CLI argument
        username : Optional[str]
            Username provided via CLI argument
        password : Optional[str]
            Password provided via CLI argument

        Returns
        -------
        Tuple[str, str, str]
            Resolved (url, username, password) tuple

        Raises
        ------
        KSDKFatal
            If any required credential cannot be resolved
        """
        # CLI args or environment variables
        url, username, password = self.resolve_from_args_or_env(url, username, password)

        # fill missing credentials from keyring
        username, password = self.resolve_from_keyring(username, password)

        # prompt  missing credentials
        url, username, password = self.resolve_from_prompt(url, username, password)

        # ensure all credentials are present
        self.validate_credentials(url, username, password)

        return url, username, password  # type: ignore

    def store_credentials(self, username: str, password: str) -> None:
        """
        Store credentials in keyring.

        Parameters
        ----------
        username : str
            Username to store
        password : str
            Password to store
        """
        try:
            # Store both username and password as JSON in the password field
            credentials_data = json.dumps({"username": username, "password": password})
            keyring.set_password(self.KEYRING_SERVICE_NAME, self.KEYRING_USERNAME, credentials_data)
            logger.debug(f"Stored credentials for user '{username}' in keyring")
        except Exception as e:
            logger.warning(f"Failed to store credentials in keyring: {e}")

    def get_stored_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Retrieve stored credentials from keyring.

        Returns
        -------
        Tuple[Optional[str], Optional[str]]
            (username, password) tuple, or (None, None) if not found
        """
        try:
            credentials_json = keyring.get_password(self.KEYRING_SERVICE_NAME, self.KEYRING_USERNAME)
            if not credentials_json:
                return None, None

            # Parse the JSON to extract username and password
            credentials_data = json.loads(credentials_json)
            return credentials_data.get("username"), credentials_data.get("password")
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse stored credentials: {e}")
            return None, None
        except Exception as e:
            logger.warning(f"Failed to retrieve credentials from keyring: {e}")
            return None, None

    def clear_credentials(self) -> None:
        """Clear stored credentials from keyring."""
        try:
            creds = keyring.get_credential(self.KEYRING_SERVICE_NAME, self.KEYRING_USERNAME)
            if not creds:
                return
            keyring.delete_password(self.KEYRING_SERVICE_NAME, self.KEYRING_USERNAME)
            logger.debug("Cleared credentials from keyring")
        except Exception as e:
            logger.warning(f"Failed to clear credentials from keyring: {e}")

    def resolve_from_args_or_env(
        self, url: Optional[str], username: Optional[str], password: Optional[str]
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Resolve credentials from CLI arguments or environment variables."""
        if not url:
            url = str(self._env_vars.URL) if self._env_vars.URL else None

        if not username:
            username = self._env_vars.USERNAME

        if not password:
            password = self._env_vars.PASSWORD

        return url, username, password

    def resolve_from_keyring(
        self, username: Optional[str], password: Optional[str]
    ) -> Tuple[Optional[str], Optional[str]]:
        """Resolve missing credentials from keyring."""
        if username and password:
            return username, password

        logger.info("Fetching credentials from keyring")
        kr_username, kr_password = self.get_stored_credentials()

        if not username:
            username = kr_username
        if not password:
            password = kr_password

        return username, password

    def resolve_from_prompt(
        self, url: Optional[str], username: Optional[str], password: Optional[str]
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Prompt user for any missing credentials."""
        if not url:
            url = input("Platform: ").strip()

        if not username:
            username = input("Username: ").strip()

        if not password:
            password = getpass.getpass("Password: ").strip()

        return url, username, password

    def validate_credentials(self, url: Optional[str], username: Optional[str], password: Optional[str]) -> None:
        """Validate that all required credentials are present."""
        if not url:
            raise KSDKFatal("No platform URL provided")

        if not username or not password:
            raise KSDKFatal("No username or password provided")
