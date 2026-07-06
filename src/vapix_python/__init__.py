"""Python wrapper for the Axis Communications VAPIX camera API."""

from .exceptions import (
    VapixAuthenticationError,
    VapixError,
    VapixRequestError,
    VapixResponseError,
)
from .geolocation_api import GeolocationAPI, GeoPosition
from .ptz_control import PTZControl
from .vapix_api import VapixAPI

__version__ = "0.2.0"

__all__ = [
    "GeoPosition",
    "GeolocationAPI",
    "PTZControl",
    "VapixAPI",
    "VapixAuthenticationError",
    "VapixError",
    "VapixRequestError",
    "VapixResponseError",
    "__version__",
]
