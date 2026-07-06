"""Geolocation (position/heading) support via the VAPIX geolocation API."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING, TypedDict

from .exceptions import VapixResponseError

if TYPE_CHECKING:  # imported for type hints only, avoids a circular import
    from .vapix_api import VapixAPI

_ENDPOINT = "geolocation"

# Values some firmware uses where the spec says "false"; anything else counts
# as valid, matching the lenient parsing of pre-0.2.0 releases.
_FALSY_FLAGS = frozenset({"", "false", "no", "0"})


class GeoPosition(TypedDict):
    """Parsed result of :meth:`GeolocationAPI.get_position`."""

    lat: float
    lon: float
    heading: float
    valid_position: bool
    valid_heading: bool


def _collect_fields(text: str) -> dict[str, str]:
    """Parse XML and map each local tag name to its first non-empty text.

    Namespace-agnostic single pass; element *presence* is recorded even when
    the element has no text (empty string), so callers can detect tags like
    ``<Error>`` that only carry children.
    """
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise VapixResponseError(f"Camera returned invalid XML: {text!r}") from exc

    fields: dict[str, str] = {}
    for elem in root.iter():
        name = elem.tag.rsplit("}", 1)[-1]
        value = (elem.text or "").strip()
        if name not in fields or (not fields[name] and value):
            fields[name] = value
    return fields


def _raise_on_error(fields: dict[str, str]) -> None:
    if "Error" in fields:
        description = fields.get("ErrorDescription") or "unknown error"
        raise VapixResponseError(f"Geolocation request failed: {description}")


class GeolocationAPI:
    """Read and write the camera's configured geolocation."""

    def __init__(self, api: VapixAPI) -> None:
        self.api = api

    def get_position(self) -> GeoPosition:
        """Get the camera's configured location and heading.

        Returns:
            Dict with ``lat``, ``lon``, ``heading`` (floats) and
            ``valid_position``, ``valid_heading`` (bools).

        Raises:
            VapixResponseError: The camera reported an error or the response
                could not be parsed.
        """
        resp = self.api._send_request(f"{_ENDPOINT}/get.cgi")
        fields = _collect_fields(resp)
        _raise_on_error(fields)

        if not all(name in fields for name in ("Lat", "Lng", "Heading")):
            raise VapixResponseError(f"Geolocation response missing position data: {resp!r}")

        try:
            return {
                "lat": float(fields["Lat"]),
                "lon": float(fields["Lng"]),
                "heading": float(fields["Heading"]),
                "valid_position": fields.get("ValidPosition", "").lower() not in _FALSY_FLAGS,
                "valid_heading": fields.get("ValidHeading", "").lower() not in _FALSY_FLAGS,
            }
        except ValueError as exc:
            raise VapixResponseError(
                f"Geolocation response contained non-numeric position data: {resp!r}"
            ) from exc

    def set_position(self, lat: float, lon: float, heading: float = 0, text: str = "") -> bool:
        """Set the camera's location and heading.

        Args:
            lat: Latitude in decimal degrees (positive north).
            lon: Longitude in decimal degrees (positive east).
            heading: Heading in degrees (0 = north).
            text: Optional free-form location description.

        Returns:
            True on success.

        Raises:
            VapixResponseError: The camera rejected the new position.
        """
        resp = self.api._send_request(
            f"{_ENDPOINT}/set.cgi",
            method="POST",
            params={"lat": lat, "lng": lon, "heading": heading, "text": text},
        )
        # Some firmware answers a successful set with an empty or plain-text
        # body; only XML bodies can carry a structured <Error> to check for.
        if resp.lstrip().startswith("<"):
            _raise_on_error(_collect_fields(resp))
        return True
