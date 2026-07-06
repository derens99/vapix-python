"""Deprecated module path — use ``from vapix_python import GeolocationAPI`` instead."""

import warnings

from .geolocation_api import GeolocationAPI

warnings.warn(
    "vapix_python.GeolocationAPI is deprecated; import from vapix_python instead "
    "(from vapix_python import GeolocationAPI)",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["GeolocationAPI"]
