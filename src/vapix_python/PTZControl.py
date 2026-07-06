"""Deprecated module path — use ``from vapix_python import PTZControl`` instead."""

import warnings

from .ptz_control import PTZControl

warnings.warn(
    "vapix_python.PTZControl is deprecated; import from vapix_python instead "
    "(from vapix_python import PTZControl)",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["PTZControl"]
