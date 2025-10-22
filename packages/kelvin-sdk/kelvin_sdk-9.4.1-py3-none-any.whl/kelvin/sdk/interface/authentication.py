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

from typing import Optional

from typeguard import typechecked

from kelvin.sdk.lib.models.operation import OperationResponse


@typechecked
def reset() -> OperationResponse:
    """
    Reset all authentication credentials and configuration cache.

    Returns
    -------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the credentials reset.

    """
    from kelvin.sdk.lib.session.session_manager import session_manager as _session_manager

    return _session_manager.reset_session(full_reset=True, ignore_destructive_warning=True)


@typechecked
def logout(ignore_destructive_warning: bool = False) -> OperationResponse:
    """
    Logs off the client all currently stored sessions.

    Parameters
    ----------
    ignore_destructive_warning: bool
        indicates whether it should ignore the destructive warning.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the result of the logout request.

    """
    from kelvin.sdk.lib.session.session_manager import session_manager as _session_manager

    return _session_manager.reset_session(full_reset=False, ignore_destructive_warning=ignore_destructive_warning)


@typechecked
def authentication_token(full: bool = False, margin: float = 10.0) -> OperationResponse:
    """
    Obtain an authentication authentication_token from the API.

    Parameters
    ----------
    full: bool
        return the full authentication_token.
    margin: float
        minimum time to expiry.

    Returns
    ----------
    kelvin.sdk.lib.models.operation.OperationResponse
        an OperationResponse object encapsulating the authentication token.

    """
    from kelvin.sdk.lib.session.session_manager import session_manager as _session_manager

    return _session_manager.authentication_token(full=full, margin=margin)
