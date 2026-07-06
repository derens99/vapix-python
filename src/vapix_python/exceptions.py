"""Exception types raised by the vapix-python library."""

from __future__ import annotations


class VapixError(Exception):
    """Base class for all errors raised by vapix-python."""


class VapixRequestError(VapixError):
    """The HTTP request to the camera failed (network error or HTTP error status)."""


class VapixAuthenticationError(VapixRequestError):
    """The camera rejected the supplied credentials (HTTP 401)."""


class VapixResponseError(VapixError):
    """The camera returned a response that could not be parsed or reported an error."""
