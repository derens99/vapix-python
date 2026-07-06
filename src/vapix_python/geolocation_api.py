"""Geolocation (position/heading) support via the VAPIX geolocation API."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING, Any

from .exceptions import VapixResponseError

if TYPE_CHECKING:  # imported for type hints only, avoids a circular import
    from .vapix_api import VapixAPI

_ENDPOINT = "geolocation"


def _local_name(tag: str) -> str:
    """Strip an XML namespace from a tag name."""
    return tag.rsplit("}", 1)[-1]


def _find_text(root: ET.Element, name: str) -> str | None:
    """Find the text of the first element with the given local name, namespace-agnostic."""
    for elem in root.iter():
        if _local_name(elem.tag) == name and elem.text is not None:
            return elem.text.strip()
    return None


def _parse_xml(text: str) -> ET.Element:
    try:
        return ET.fromstring(text)
    except ET.ParseError as exc:
        raise VapixResponseError(f"Camera returned invalid XML: {text!r}") from exc


def _raise_on_error(root: ET.Element) -> None:
    for elem in root.iter():
        if _local_name(elem.tag) == "Error":
            description = _find_text(elem, "ErrorDescription") or "unknown error"
            raise VapixResponseError(f"Geolocation request failed: {description}")


class GeolocationAPI:
    """Read and write the camera's configured geolocation."""

    def __init__(self, api: VapixAPI) -> None:
        self.api = api

    def get_position(self) -> dict[str, Any]:
        """Get the camera's configured location and heading.

        Returns:
            Dict with ``lat``, ``lon``, ``heading`` (floats) and
            ``valid_position``, ``valid_heading`` (bools).

        Raises:
            VapixResponseError: The camera reported an error or the response
                could not be parsed.
        """
        resp = self.api._send_request_vanilla(f"{_ENDPOINT}/get.cgi")
        root = _parse_xml(resp)
        _raise_on_error(root)

        lat = _find_text(root, "Lat")
        lon = _find_text(root, "Lng")
        heading = _find_text(root, "Heading")
        if lat is None or lon is None or heading is None:
            raise VapixResponseError(f"Geolocation response missing position data: {resp!r}")

        valid_position = (_find_text(root, "ValidPosition") or "").lower() == "true"
        valid_heading = (_find_text(root, "ValidHeading") or "").lower() == "true"

        try:
            return {
                "lat": float(lat),
                "lon": float(lon),
                "heading": float(heading),
                "valid_position": valid_position,
                "valid_heading": valid_heading,
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
        resp = self.api._send_request_vanilla(
            f"{_ENDPOINT}/set.cgi",
            method="POST",
            params={"lat": lat, "lng": lon, "heading": heading, "text": text},
        )
        _raise_on_error(_parse_xml(resp))
        return True
