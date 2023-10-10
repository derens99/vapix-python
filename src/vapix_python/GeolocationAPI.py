from __future__ import annotations
from typing import TYPE_CHECKING

import xml.etree.ElementTree as ET

# Import for type hints only
if TYPE_CHECKING:
    from .VapixAPI import VapixAPI


class GeolocationAPI:
    def __init__(self, api: VapixAPI) -> None:
        self.api = api
        self.endpoint = "geolocation"

    def get_position(self):
        resp = self.api._send_request_vanilla(self.endpoint + "/get.cgi")
        print(resp)

        root = ET.fromstring(resp)

        lat = float(root.find(".//Lat").text)
        lon = float(root.find(".//Lng").text)
        heading = float(root.find(".//Heading").text)

        valid_position_str = root.find(".//ValidPosition").text.strip()
        valid_position = False if valid_position_str.lower() == "false" else True

        valid_heading_str = root.find(".//ValidHeading").text.strip()
        valid_heading = False if valid_heading_str.lower() == "false" else True

        return {
            "lat": lat,
            "lon": lon,
            "heading": heading,
            "valid_position": valid_position,
            "valid_heading": valid_heading,
        }

    def set_position(self, lat: float, lon: float, heading: float = 0, text: str = ""):
        resp = self.api._send_request_vanilla(
            self.endpoint + "/set.cgi",
            method="POST",
            params={
                "lat": lat,
                "lng": lon,
                "heading": heading,
                "text": text,
            },
        )
        print(resp)
