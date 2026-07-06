"""Pan/tilt/zoom control via the VAPIX ``com/ptz.cgi`` endpoint."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from .exceptions import VapixResponseError

if TYPE_CHECKING:  # imported for type hints only, avoids a circular import
    from .vapix_api import VapixAPI

_PTZ_ENDPOINT = "com/ptz.cgi"


def _parse_key_value_response(text: str) -> dict[str, str]:
    """Parse a VAPIX ``key=value`` line response into a dict."""
    values: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()
    return values


class PTZControl:
    """Pan-Tilt-Zoom control for an Axis camera."""

    def __init__(self, api: VapixAPI) -> None:
        self.api = api

    def _command(self, params: Mapping[str, Any]) -> str:
        return self.api._send_request(_PTZ_ENDPOINT, params=params)

    # ------------------------------------------------------------------
    # Position queries
    # ------------------------------------------------------------------
    def get_current_position(self) -> tuple[float, float, float]:
        """Get the current camera position.

        Returns:
            Tuple of the current ``(pan, tilt, zoom)`` values.

        Raises:
            VapixResponseError: The camera response did not contain a position.
        """
        resp = self._command({"query": "position"})
        values = _parse_key_value_response(resp)
        try:
            return float(values["pan"]), float(values["tilt"]), float(values["zoom"])
        except (KeyError, ValueError) as exc:
            raise VapixResponseError(
                f"Could not parse PTZ position from response: {resp!r}"
            ) from exc

    def get_current_ptz(self) -> str:
        """Get the raw position query response as returned by the camera."""
        return self._command({"query": "position"})

    def ptz_enabled(self, channel: int = 1) -> str:
        """Check whether PTZ is available.

        Args:
            channel: The video channel to check.

        Returns:
            The list of available PTZ commands, or an empty string if disabled.
        """
        return self._command({"info": channel})

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------
    def absolute_move(self, pan: float, tilt: float, zoom: float, speed: float) -> None:
        """Move the camera to an absolute position at the given speed."""
        self._command({"pan": pan, "tilt": tilt, "zoom": zoom, "speed": speed})

    def relative_move(self, pan: float, tilt: float, zoom: float, speed: float) -> None:
        """Move the camera by a relative amount at the given speed."""
        self._command({"rpan": pan, "rtilt": tilt, "rzoom": zoom, "speed": speed})

    def continuous_move(self, pan_speed: int, tilt_speed: int, zoom_speed: int) -> None:
        """Start continuous pan/tilt/zoom movement at the given speeds."""
        self._command(
            {
                "continuouspantiltmove": f"{pan_speed},{tilt_speed}",
                "continuouszoommove": zoom_speed,
            }
        )

    def continuous_pantilt(self, pan_speed: int, tilt_speed: int) -> None:
        """Start continuous pan/tilt movement at the given speeds."""
        self._command({"continuouspantiltmove": f"{pan_speed},{tilt_speed}"})

    def continuous_zoom(self, zoom_speed: int) -> None:
        """Start continuous zoom movement at the given speed."""
        self._command({"continuouszoommove": zoom_speed})

    def continuous_focus(self, focus_speed: int) -> None:
        """Start continuous focus movement at the given speed."""
        self._command({"continuousfocusmove": focus_speed})

    def continuous_iris(self, iris_speed: int) -> None:
        """Start continuous iris movement at the given speed."""
        self._command({"continuousirismove": iris_speed})

    def continuous_brightness(self, brightness_speed: int) -> None:
        """Start continuous brightness adjustment at the given speed."""
        self._command({"continuousbrightnessmove": brightness_speed})

    def stop_move(self) -> None:
        """Stop all pan/tilt and zoom movement."""
        self._command({"continuouspantiltmove": "0,0", "continuouszoommove": "0"})

    def center_move(self, x_pos: int, y_pos: int, speed: int) -> None:
        """Center the view on the given image coordinates."""
        self._command({"center": f"{x_pos},{y_pos}", "speed": speed})

    def area_zoom(self, x_pos: int, y_pos: int, zoom: int, speed: int) -> None:
        """Center on the given image coordinates and zoom by the given factor."""
        self._command({"areazoom": f"{x_pos},{y_pos},{zoom}", "speed": speed})

    def move(self, position: str, speed: int) -> None:
        """Move the camera to a named position (e.g. ``home``, ``up``, ``left``)."""
        self._command({"move": position, "speed": speed})

    def go_home(self, speed: int) -> None:
        """Move the camera to the home position at the given speed."""
        self._command({"move": "home", "speed": speed})

    def set_move_speed(self, speed: int) -> None:
        """Set the head speed used for moves.

        Args:
            speed: Speed between 0 and 100.
        """
        if not 0 <= speed <= 100:
            raise ValueError("Speed must be between 0 and 100.")
        self._command({"speed": speed})

    # ------------------------------------------------------------------
    # Imaging settings
    # ------------------------------------------------------------------
    def set_iris(self, iris_level: int = 1750) -> bool:
        """Set the iris to the given level (0-9999)."""
        if not 0 <= iris_level <= 9999:
            raise ValueError("Iris level must be between 0 and 9999.")
        self._command({"iris": iris_level})
        return True

    def set_focus(self, focus_level: int) -> bool:
        """Set the focus to the given level (0-9999)."""
        if not 0 <= focus_level <= 9999:
            raise ValueError("Focus level must be between 0 and 9999.")
        self._command({"focus": focus_level})
        return True

    def set_zoom(self, zoom_level: int) -> bool:
        """Set the zoom to the given level (0-9999)."""
        if not 0 <= zoom_level <= 9999:
            raise ValueError("Zoom level must be between 0 and 9999.")
        self._command({"zoom": zoom_level})
        return True

    def set_brightness(self, brightness_level: int) -> bool:
        """Set the brightness to the given level (0-9999)."""
        if not 0 <= brightness_level <= 9999:
            raise ValueError("Brightness level must be between 0 and 9999.")
        self._command({"brightness": brightness_level})
        return True

    def set_autofocus(self, enabled: bool = True) -> bool:
        """Enable or disable autofocus."""
        self._command({"autofocus": "on" if enabled else "off"})
        return True

    def set_autoiris(self, enabled: bool = True) -> bool:
        """Enable or disable auto iris."""
        self._command({"autoiris": "on" if enabled else "off"})
        return True

    # ------------------------------------------------------------------
    # Presets
    # ------------------------------------------------------------------
    def set_current_preset_name(self, preset_name: str) -> bool:
        """Save the current position as a named preset."""
        self._command({"setserverpresetname": preset_name})
        return True

    def set_current_preset_no(self, preset_number: int) -> bool:
        """Save the current position as a numbered preset."""
        self._command({"setserverpresetno": preset_number})
        return True

    def rename_preset_number(self, preset_number: int, preset_name: str) -> bool:
        """Rename the preset stored at ``preset_number`` to ``preset_name``."""
        self._command({"renameserverpresetno": preset_number, "newname": preset_name})
        return True

    def set_home(self) -> bool:
        """Set the current position as the home position."""
        self._command({"home": "yes"})
        return True

    def remove_server_preset_name(self, preset_name: str) -> bool:
        """Remove the preset with the given name."""
        self._command({"removeserverpresetname": preset_name})
        return True

    def remove_server_preset_no(self, preset_number: int) -> bool:
        """Remove the preset with the given number."""
        self._command({"removeserverpresetno": preset_number})
        return True

    def set_device_preset(self, preset_number: int) -> bool:
        """Save the current position as a device-specific preset number.

        Bypasses the presetpos interface and stores the preset directly in the
        device; on some devices this triggers a device-specific special function.
        """
        self._command({"setdevicepreset": preset_number})
        return True
