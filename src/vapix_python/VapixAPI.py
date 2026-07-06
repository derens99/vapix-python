"""Deprecated module path — use ``from vapix_python import VapixAPI`` instead."""

import warnings

from .vapix_api import VapixAPI

warnings.warn(
    "vapix_python.VapixAPI is deprecated; import from vapix_python instead "
    "(from vapix_python import VapixAPI)",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["VapixAPI"]
