"""Core client for the Axis VAPIX HTTP API."""

from __future__ import annotations

from collections.abc import Mapping
from types import TracebackType
from typing import Any

import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

from ._parsing import parse_key_value
from .exceptions import VapixAuthenticationError, VapixRequestError
from .geolocation_api import GeolocationAPI
from .ptz_control import PTZControl

_SUPPORTED_METHODS = frozenset({"GET", "POST"})


class VapixAPI:
    """Client for interacting with Axis cameras through the VAPIX API.

    The client owns a single authenticated :class:`requests.Session` and exposes
    feature areas as attributes (``ptz``, ``geolocation``). It can be used as a
    context manager so the underlying session is always closed::

        with VapixAPI("192.168.0.90", "root", "secret") as api:
            pan, tilt, zoom = api.ptz.get_current_position()

    Args:
        host: IP address or hostname of the camera.
        user: Username for API authentication.
        password: Password for API authentication.
        timeout: Timeout in seconds applied to every HTTP request.
        secure: Use HTTPS instead of HTTP when talking to the camera.
        verify_ssl: Passed through to requests' ``verify`` — ``True``/``False``
            or a path to a CA bundle. Only meaningful with ``secure=True``.
        auth_method: ``"digest"`` (default, what most Axis firmware expects)
            or ``"basic"``.
        camera: Camera/channel number used by endpoints that take one.
    """

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        timeout: float = 5.0,
        *,
        secure: bool = False,
        verify_ssl: bool | str = True,
        auth_method: str = "digest",
        camera: int = 1,
    ) -> None:
        self.host = host
        self.user = user
        self.password = password
        self.timeout = timeout
        self.camera = camera

        scheme = "https" if secure else "http"
        self.base_url = f"{scheme}://{host}/axis-cgi"

        self.session = requests.Session()
        if auth_method == "digest":
            self.session.auth = HTTPDigestAuth(user, password)
        elif auth_method == "basic":
            self.session.auth = HTTPBasicAuth(user, password)
        else:
            raise ValueError(f"auth_method must be 'digest' or 'basic', got {auth_method!r}")
        self.session.verify = verify_ssl

        self.ptz = PTZControl(self)
        self.geolocation = GeolocationAPI(self)

    # ------------------------------------------------------------------
    # Request plumbing
    # ------------------------------------------------------------------
    def _send_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Mapping[str, Any] | None = None,
    ) -> str:
        """Send a request to a VAPIX endpoint and return the response body.

        The transport is endpoint-agnostic: it sends exactly the parameters it
        is given. Endpoint-specific arguments (like ``ptz.cgi``'s ``camera``/
        ``html``/``timestamp``) belong in the feature layer that knows about
        them.

        Args:
            endpoint: Endpoint path relative to ``/axis-cgi``, e.g. ``com/ptz.cgi``.
            method: ``"GET"`` or ``"POST"``.
            params: Query parameters (GET) or form data (POST).

        Raises:
            VapixAuthenticationError: The camera returned HTTP 401 (bad
                credentials) or 403 (insufficient privileges).
            VapixRequestError: The request failed at the network level or the
                camera returned another HTTP error status.
        """
        method = method.upper()
        if method not in _SUPPORTED_METHODS:
            raise ValueError(f"Unsupported HTTP method: {method!r}")

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_kwargs: dict[str, Any] = (
            {"params": params} if method == "GET" else {"data": params}
        )
        try:
            response = self.session.request(method, url, timeout=self.timeout, **request_kwargs)
        except requests.RequestException as exc:
            raise VapixRequestError(f"Request to {url} failed: {exc}") from exc

        if response.status_code == 401:
            raise VapixAuthenticationError(
                f"Authentication failed for {url} (HTTP 401) — check user/password"
            )
        if response.status_code == 403:
            raise VapixAuthenticationError(
                f"Access denied for {url} (HTTP 403) — the account lacks privileges "
                "for this operation"
            )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise VapixRequestError(str(exc)) from exc
        return response.text

    # ------------------------------------------------------------------
    # General device helpers
    # ------------------------------------------------------------------
    def get_parameters(self, group: str | None = None) -> dict[str, str]:
        """List device parameters via ``param.cgi``.

        Args:
            group: Optional parameter group filter, e.g. ``"Properties.PTZ"``.

        Returns:
            Mapping of fully-qualified parameter names to their values.
        """
        params: dict[str, Any] = {"action": "list"}
        if group is not None:
            params["group"] = group
        return parse_key_value(self._send_request("param.cgi", params=params))

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def close(self) -> None:
        """Close the underlying HTTP session."""
        self.session.close()

    def __enter__(self) -> VapixAPI:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(host={self.host!r}, user={self.user!r})"
