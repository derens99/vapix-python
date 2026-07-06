"""Exception types raised by the vapix-python library."""

import requests


class VapixError(Exception):
    """Base class for all errors raised by vapix-python."""


class VapixRequestError(VapixError, requests.RequestException):
    """The HTTP request to the camera failed (network error or HTTP error status).

    Also subclasses :class:`requests.RequestException` so pre-0.2.0 code that
    catches ``requests.RequestException`` keeps working.
    """


class VapixAuthenticationError(VapixRequestError):
    """The camera rejected the request's credentials or privileges (HTTP 401/403)."""


class VapixResponseError(VapixError):
    """The camera returned a response that could not be parsed or reported an error."""
