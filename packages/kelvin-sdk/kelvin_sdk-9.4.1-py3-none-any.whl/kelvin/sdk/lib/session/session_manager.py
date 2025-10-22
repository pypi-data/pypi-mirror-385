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

import json
import re
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, List, Optional
from urllib.parse import parse_qs, urlencode, urlparse

import httpx
from pydantic.v1 import AnyUrl, ValidationError

from kelvin.api.base.error import ClientError
from kelvin.api.base.http_client.metadata import SyncMetadata
from kelvin.api.client import Client
from kelvin.sdk.lib.auth import credential_manager
from kelvin.sdk.lib.configs.auth_manager_configs import AuthManagerConfigs
from kelvin.sdk.lib.configs.general_configs import GeneralConfigs
from kelvin.sdk.lib.exceptions import KSDKException, KSDKFatal, MandatoryConfigurationsException
from kelvin.sdk.lib.models.operation import OperationResponse
from kelvin.sdk.lib.utils.display_utils import (
    display_data_entries,
    display_yes_or_no_question,
    pretty_colored_content,
    success_colored_message,
)
from kelvin.sdk.lib.utils.logger_utils import logger, setup_logger

from ..configs.general_configs import KSDKHelpMessages
from ..models.generic import KPath
from ..models.ksdk_global_configuration import CompanyMetadata, KelvinSDKGlobalConfiguration
from ..models.types import LogColor
from ..utils.general_utils import get_system_information
from . import session_storage
from .session_utils import warn_ksdk_version


class Singleton(type):
    _instances: dict = {}

    def __call__(cls, *args: Any, **kwargs: Any):  # type: ignore
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Server(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        query = urlparse(self.path).query
        parsed_query = parse_qs(query)
        if "code" in parsed_query:
            logger.relevant("A request was received with an authorization code.")
            code = parsed_query["code"][0]
            self.wfile.write(bytes('<script>window.alert("Kelvin SDK connected."); window.close();</script>', "UTF-8"))
            SessionManager.auth_code = code


class SessionManager(metaclass=Singleton):
    # 1 - Central piece
    _global_ksdk_configuration: Optional[KelvinSDKGlobalConfiguration] = None
    # 2 - Cached blocks
    _current_site_metadata: Optional[CompanyMetadata] = None
    _client: Optional[Client] = None
    _current_session: Optional[session_storage.SessionConfig] = None

    auth_code: Optional[str] = None

    def __init__(self) -> None:
        self._current_session = session_storage.load_session()
        self._credential_manager = credential_manager.CredentialManager()

    # 1 - Global Session Manager
    def reset_session(self, full_reset: bool = False, ignore_destructive_warning: bool = False) -> OperationResponse:
        """Logs off the client all currently stored sessions.

        Parameters
        ----------
        full_reset: bool, default=False
            Indicates whether it should proceed with a full reset.
        ignore_destructive_warning: bool, default=False
            Ignore_destructive_warning: indicates whether it should ignore the destructive warning.

        Returns
        -------
        OperationResponse
            An OperationResponse object encapsulating the result of the logout request.

        """
        try:
            # 1 - Logout from all sessions
            if not ignore_destructive_warning:
                ignore_destructive_warning = display_yes_or_no_question("")

            if ignore_destructive_warning:
                session_storage.clear_session()
                self._current_session = None
                self._current_site_metadata = None

                self.get_global_ksdk_configuration().reset_ksdk_configuration().commit_ksdk_configuration()

                if self._client:
                    self._client.logout()
                    self._client = None

            ksdk_configuration = self.get_global_ksdk_configuration()

            # 2 - If it is a full reset, purge all the configuration files
            if full_reset:
                logger.info("Resetting KSDK configurations..")
                self._reset_configuration_files(ksdk_configuration=ksdk_configuration)

            success_message = "Session successfully reset."
            logger.relevant(success_message)
            return OperationResponse(success=True, log=success_message)
        except Exception as exc:
            error_message = f"Error resetting session: {str(exc)}"
            logger.exception(error_message)
            return OperationResponse(success=False, log=error_message)

    def full_reset(self, ignore_destructive_warning: bool = False) -> OperationResponse:
        """
        Reset all configurations & cache used by Kelvin SDK.

        Parameters
        ----------
        ignore_destructive_warning : bool
            indicates whether or not the command should bypass the destructive prompt warning.

        Returns
        -------
        OperationResponse
            an OperationResponse encapsulating the result of the reset operation.

        """
        try:
            if not ignore_destructive_warning:
                question: str = "\tThis operation will reset all configurations"
                ignore_destructive_warning = display_yes_or_no_question(question=question)

            result_message: str = "Reset operation cancelled"
            if ignore_destructive_warning:
                self._credential_manager.clear_credentials()
                ksdk_config_dir_path: KPath = self.get_global_ksdk_configuration().ksdk_config_dir_path
                if ksdk_config_dir_path and ksdk_config_dir_path.exists():
                    logger.info(f'Resetting configurations under "{ksdk_config_dir_path.expanduser().absolute()}".')
                    ksdk_config_dir_path.delete_dir()
                    result_message = "Configurations successfully reset"
                    logger.relevant(result_message)
            else:
                logger.warning(result_message)

            return OperationResponse(success=True, log=result_message)

        except Exception as exc:
            error_message: str = str(exc)
            logger.error(f'Error resetting configurations: "{error_message}"')
            return OperationResponse(success=False, log=error_message)

    # 2 - Internal functions
    @staticmethod
    def _reset_configuration_files(ksdk_configuration: KelvinSDKGlobalConfiguration) -> None:
        """Clear all configuration files and folders

        Parameters
        ----------
        ksdk_configuration: KelvinSDKGlobalConfiguration
            A KSDK global configuration instance
        """
        # 1 - get the variables
        files_to_reset: List[KPath] = [
            ksdk_configuration.ksdk_history_file_path,
            ksdk_configuration.ksdk_client_config_file_path,
            ksdk_configuration.ksdk_config_file_path,
            ksdk_configuration.ksdk_temp_dir_path,
            ksdk_configuration.ksdk_schema_dir_path,
        ]
        # 2 - delete all files
        for item in files_to_reset:
            if item.exists():
                if item.is_dir():
                    item.delete_dir()
                else:
                    item.unlink()

    def browser_login(self, url: str) -> Optional[str]:
        if not re.match(r"\w+://", url):
            url = f"https://{url}"
        if "." not in url:
            url = f"{url}.kelvininc.com"

        path = "auth/realms/kelvin/protocol/openid-connect/auth"
        params = {
            "client_id": AuthManagerConfigs.browser_auth_client_id,
            "redirect_uri": AuthManagerConfigs.browser_auth_redirect_uri,
            "response_type": "code",
        }
        page = f"{url}/{path}?{urlencode(params)}"

        httpd = HTTPServer(server_address=("", AuthManagerConfigs.browser_auth_port), RequestHandlerClass=Server)
        httpd.timeout = AuthManagerConfigs.browser_auth_timeout

        logger.info("Opening browser to authenticate")
        webbrowser.open_new_tab(page)

        logger.info("Waiting for authorization code.")
        httpd.handle_request()

        return SessionManager.auth_code

    # 2 - Client access and instantiation
    def login_on_url(
        self,
        url: str,
        username: str,
        password: str,
        browser: bool = False,
        reset: bool = False,
        save: bool = True,
    ) -> OperationResponse:
        """Logs the user into the provided url.

        Parameters
        ----------
        url: str, optional
            The url to log on.
        username: str, optional
            The username of the client site.
        password: str, optional
            The password corresponding to the username.
        browser: bool, default=False
            If set, opens a browser window to proceed with the authentication.
        reset: bool, default=False
            If set to True, will clear the existing configuration prior to the new session.
        save: bool, default=True
            If set to True, will save credentials

        Returns
        -------
        OperationResponse
            An OperationResponse object encapsulating the result of the authentication request.

        """
        if reset:
            logger.info("Resetting session before login")
            self.reset_session(full_reset=False, ignore_destructive_warning=True)

        try:
            anyurl = AnyUrl(url, scheme="https")
            self._client = Client(url=anyurl, username=username, password=password)
            self._client.login()
        except ClientError as e:
            raise KSDKFatal(f"Login failed: {e}")

        self._set_metadata_for_current_url(self._client._auth_conn._metadata._json_metadata)
        self._current_session = session_storage.session_config_from_metadata(
            self._client._auth_conn._metadata._json_metadata
        )
        session_storage.store_session(self._current_session)

        if save:
            self._credential_manager.store_credentials(username, password)

        logger.relevant(f'Successfully logged on "{self._client.base_url}" as "{self._client.username}"')

        warn_ksdk_version(self._current_session)

        return OperationResponse(success=True, log="Login successful.")

    def login_client_on_current_url(self, verbose: bool = True) -> Client:
        """Login process"""
        if self._client:
            return self._client

        # env credentials take precedence
        env_url, env_user, env_password = self._credential_manager.resolve_from_args_or_env(
            url=None, username=None, password=None
        )

        # url from current session if not defined in env vars
        url = env_url or (self._current_session.url if self._current_session else None)
        if not url:
            raise KSDKFatal(AuthManagerConfigs.invalid_session_message)

        # credentials from keyring if not defined in env vars
        user, password = self._credential_manager.resolve_from_keyring(env_user, env_password)
        if not user or not password:
            raise KSDKFatal("No credentials found. Please log in or provide env var credentials.")

        anyurl = AnyUrl(url=url, scheme="https")
        self._client = Client(url=anyurl, username=user, password=password, verbose=verbose)
        self._client.login()
        self._set_metadata_for_current_url(self._client._auth_conn._metadata._json_metadata)

        return self._client

    def authentication_token(self, full: bool, margin: float = 10.0) -> OperationResponse:
        """Obtain an authentication authentication_token from the API."""
        try:
            client = self.login_client_on_current_url(verbose=False)
        except Exception as exc:
            logger.error(str(exc))
            return OperationResponse(success=False, log=str(exc))

        if not client._auth_conn._access_token:
            logger.error("unable to retrieve token")
            return OperationResponse(success=False, log="unable to retrieve token")

        if full:
            expires_in = client._auth_conn._expires_at
            refresh_expires = client._auth_conn._refresh_expires_at

            json.dump(
                {
                    "access_token": client._auth_conn._access_token,
                    "expires_in": expires_in.isoformat() if expires_in else None,
                    "refresh_token": client._auth_conn._refresh_token,
                    "refresh_expires_in": refresh_expires.isoformat() if refresh_expires else None,
                },
                sys.stdout,
                indent=2,
            )
        else:
            sys.stdout.write(client._auth_conn._access_token)

        return OperationResponse(success=True, log=str(client._auth_conn._access_token))

    def get_global_ksdk_configuration(self) -> KelvinSDKGlobalConfiguration:
        """Attempt to retrieve the KelvinSDKGlobalConfiguration from specified file path.

        Returns
        -------
        KelvinSDKGlobalConfiguration
            A KelvinSDKGlobalConfiguration object corresponding to the current configuration.
        """

        if self._global_ksdk_configuration:
            return self._global_ksdk_configuration

        self._global_ksdk_configuration = KelvinSDKGlobalConfiguration()
        return self._global_ksdk_configuration.commit_ksdk_configuration()

    def get_documentation_link_for_current_url(self) -> Optional[str]:
        """Retrieve, if existent, the complete url to the documentation page."""
        try:
            return self.get_current_session_metadata().documentation.url
        except Exception:
            return None

    def get_kelvin_system_information_for_display(self) -> str:
        """Display system information as well as, if existent, the current session's url."""

        try:
            system_information = get_system_information(pretty_keys=True)

            if not self._current_session or not self._current_session.url:
                current_url = KSDKHelpMessages.current_session_login
            else:
                current_url = self._current_session.url

            # display utils
            pretty_current_url = success_colored_message(message=current_url)
            pretty_system_info = pretty_colored_content(content=system_information, indent=2, initial_indent=2)
            return f"\nCurrent session: {pretty_current_url}\nSystem Information: {pretty_system_info}"
        except Exception:
            return KSDKHelpMessages.current_session_login

    def get_kelvin_system_information(self) -> dict:
        """Report the entire configuration set currently in use by Kelvin SDK."""

        system_information = get_system_information(pretty_keys=False)
        current_session_metadata = self.get_current_session_metadata().dict(exclude_none=True, exclude_unset=True)

        current_url = (
            self.get_global_ksdk_configuration().kelvin_sdk.current_url or KSDKHelpMessages.current_session_login
        )
        return {
            "current_url": current_url,
            "system_information": system_information,
            "metadata": current_session_metadata,
        }

    def get_docker_current_url(self) -> str:
        if not self._current_session or not self._current_session.docker_url or not self._current_session.docker_port:
            raise KSDKException("No docker session found. Please log in.")

        return f"{self._current_session.docker_url}:{self._current_session.docker_port}"

    def _set_metadata_for_current_url(self, metadata_json: dict) -> CompanyMetadata:
        """Retrieve the metadata from the specified url.

        Returns
        -------
        CompanyMetadata
            The CompanyMetadata object that encapsulates all the metadata.
        """

        try:
            self._current_site_metadata = CompanyMetadata.parse_obj(metadata_json)
            return self._current_site_metadata
        except ValidationError as exc:
            raise MandatoryConfigurationsException(exc)
        except Exception:
            raise ValueError(AuthManagerConfigs.invalid_session_message)

    def get_current_session_metadata(self) -> CompanyMetadata:
        """Returns the current session company metadata"""

        if self._current_site_metadata:
            return self._current_site_metadata

        return self.refresh_metadata()

    def refresh_metadata(self) -> CompanyMetadata:
        """Refresh metadata on request."""

        if not self._current_session or not self._current_session.url:
            raise KSDKFatal(AuthManagerConfigs.invalid_session_message)

        metadata = SyncMetadata(httpx.Client(base_url=self._current_session.url))
        metadata.fetch()
        return self._set_metadata_for_current_url(metadata._json_metadata)

    def setup_logger(self, verbose: bool = False, colored_logs: bool = True) -> Any:
        """
        Sets up the logger based on the verbose flag.

        Parameters
        ----------
        verbose : bool
            the flag indicating whether it should setup the logger in verbose mode.
        colored_logs: bool, Default=False
            Indicates whether all logs should be colored and 'pretty' formatted.

        Returns
        -------
        Any
            the setup logger.

        """
        global_configuration: KelvinSDKGlobalConfiguration = self.get_global_ksdk_configuration()
        log_color: LogColor = LogColor.COLORED
        if (
            not (sys.__stdout__.isatty() if sys.__stdout__ else False)
            or not global_configuration.kelvin_sdk.configurations.ksdk_colored_logs
            or not colored_logs
        ):
            log_color = LogColor.COLORLESS
        ksdk_history_file_path: KPath = global_configuration.ksdk_history_file_path
        debug: bool = global_configuration.kelvin_sdk.configurations.ksdk_debug

        return setup_logger(
            log_color=log_color,
            verbose=verbose,
            debug=debug,
            history_file=ksdk_history_file_path,
        )

    # Global KSDK Configurations
    def global_configuration_list(self, should_display: bool = False) -> OperationResponse:
        """
        List all available configurations for the Kelvin-SDK

        Parameters
        ----------
        should_display: bool, default=True
            specifies whether or not the display should output data.

        Returns
        -------
        OperationResponse
            An OperationResponse object encapsulating the yielded Kelvin tool configurations.
        """

        try:
            global_ksdk_configuration = self.get_global_ksdk_configuration()
            descriptions = global_ksdk_configuration.kelvin_sdk.configurations.descriptions
            private_fields = global_ksdk_configuration.kelvin_sdk.configurations.private_fields

            data = [v for k, v in descriptions.items() if k not in private_fields]

            display_obj = display_data_entries(
                data=data,
                header_names=["Variable", "Description", "Current Value"],
                attributes=["env", "description", "current_value"],
                table_title=GeneralConfigs.table_title.format(title="Environment Variables"),
                should_display=should_display,
            )
            set_unset_command = success_colored_message("kelvin configuration set/unset")
            logger.info(f"See {set_unset_command} for more details on how to configure this tool.")
            return OperationResponse(success=True, data=display_obj.parsed_data)

        except Exception as exc:
            error_message = f"Error retrieving environment variable configurations: {str(exc)}"
            logger.exception(error_message)
            return OperationResponse(success=False, log=error_message)

    def global_configuration_set(self, configuration: str, value: str) -> OperationResponse:
        """Set the specified configuration on the platform system.

        Parameters
        ----------
        configuration: str
            the configuration to change.
        value: str
            the value that corresponds to the provided configuration.
        Returns
        -------
        OperationResponse
            An OperationResponse object encapsulating the result the configuration set operation.
        """
        try:
            global_ksdk_configuration = self.get_global_ksdk_configuration()
            global_ksdk_configuration.set_configuration(configuration=configuration, value=value)
            success_message = f'Successfully set "{configuration}" to "{value}"'
            logger.relevant(success_message)
            return OperationResponse(success=True, log=success_message)
        except Exception as exc:
            error_message = f"Error setting configuration variable: {str(exc)}"
            logger.exception(error_message)
            return OperationResponse(success=False, log=error_message)

    def global_configuration_unset(self, configuration: str) -> OperationResponse:
        """Unset the specified configuration from the platform system

        Parameters
        ----------
        configuration: str
            the configuration to unset.

        Returns
        -------
        OperationResponse
            an OperationResponse object encapsulating the result the configuration unset operation.
        """
        try:
            global_ksdk_configuration = self.get_global_ksdk_configuration()
            global_ksdk_configuration.unset_configuration(configuration=configuration)
            success_message = f'Successfully unset "{configuration.lower()}"'
            logger.relevant(success_message)
            return OperationResponse(success=True, log=success_message)
        except Exception as exc:
            error_message = f"Error un-setting configuration variable: {str(exc)}"
            logger.exception(error_message)
            return OperationResponse(success=False, log=error_message)


session_manager: SessionManager = SessionManager()
