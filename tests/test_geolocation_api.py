from __future__ import annotations

import pytest

from vapix_python import VapixResponseError

NAMESPACED_GET_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<PositionResponse xmlns="http://www.axis.com/vapix/http_cgi/geolocation1">
  <Success>
    <GetSuccess>
      <Location>
        <Lat>59.3293</Lat>
        <Lng>18.0686</Lng>
        <Heading>90.5</Heading>
        <Text>Stockholm</Text>
        <ValidPosition>true</ValidPosition>
        <ValidHeading>false</ValidHeading>
      </Location>
    </GetSuccess>
  </Success>
</PositionResponse>
"""

PLAIN_GET_RESPONSE = """<PositionResponse>
  <Lat> 1.5 </Lat>
  <Lng>-2.5</Lng>
  <Heading>0</Heading>
  <ValidPosition>True</ValidPosition>
  <ValidHeading>true</ValidHeading>
</PositionResponse>
"""

ERROR_RESPONSE = """<PositionResponse>
  <Error>
    <ErrorCode>10</ErrorCode>
    <ErrorDescription>Invalid latitude</ErrorDescription>
  </Error>
</PositionResponse>
"""

SET_SUCCESS_RESPONSE = """<PositionResponse>
  <Success>
    <GeneralSuccess/>
  </Success>
</PositionResponse>
"""


def test_get_position_parses_namespaced_xml(api, fake_session):
    fake_session.queue(NAMESPACED_GET_RESPONSE)
    position = api.geolocation.get_position()
    assert position == {
        "lat": 59.3293,
        "lon": 18.0686,
        "heading": 90.5,
        "valid_position": True,
        "valid_heading": False,
    }


def test_get_position_parses_plain_xml(api, fake_session):
    fake_session.queue(PLAIN_GET_RESPONSE)
    position = api.geolocation.get_position()
    assert position["lat"] == 1.5
    assert position["lon"] == -2.5
    assert position["valid_position"] is True


def test_get_position_raises_on_error_response(api, fake_session):
    fake_session.queue(ERROR_RESPONSE)
    with pytest.raises(VapixResponseError, match="Invalid latitude"):
        api.geolocation.get_position()


def test_get_position_raises_on_invalid_xml(api, fake_session):
    fake_session.queue("not xml at all")
    with pytest.raises(VapixResponseError):
        api.geolocation.get_position()


def test_get_position_raises_on_missing_fields(api, fake_session):
    fake_session.queue("<PositionResponse><Lat>1</Lat></PositionResponse>")
    with pytest.raises(VapixResponseError):
        api.geolocation.get_position()


def test_set_position_posts_and_returns_true(api, fake_session):
    fake_session.queue(SET_SUCCESS_RESPONSE)
    assert api.geolocation.set_position(1.0, 2.0, heading=45, text="roof") is True

    sent = fake_session.last
    assert sent["method"] == "POST"
    assert sent["url"].endswith("geolocation/set.cgi")
    assert sent["data"] == {"lat": 1.0, "lng": 2.0, "heading": 45, "text": "roof"}


def test_set_position_raises_on_error(api, fake_session):
    fake_session.queue(ERROR_RESPONSE)
    with pytest.raises(VapixResponseError, match="Invalid latitude"):
        api.geolocation.set_position(999, 999)


@pytest.mark.parametrize("body", ["", "  ", "OK"])
def test_set_position_accepts_non_xml_success_body(api, fake_session, body):
    """Some firmware answers a successful set.cgi with an empty or plain body."""
    fake_session.queue(body)
    assert api.geolocation.set_position(1.0, 2.0) is True


@pytest.mark.parametrize("value", ["1", "yes", "TRUE"])
def test_valid_flags_accept_nonstandard_truthy_values(api, fake_session, value):
    fake_session.queue(
        "<PositionResponse><Lat>1</Lat><Lng>2</Lng><Heading>3</Heading>"
        f"<ValidPosition>{value}</ValidPosition><ValidHeading>false</ValidHeading>"
        "</PositionResponse>"
    )
    position = api.geolocation.get_position()
    assert position["valid_position"] is True
    assert position["valid_heading"] is False


def test_valid_flags_default_false_when_missing(api, fake_session):
    fake_session.queue(
        "<PositionResponse><Lat>1</Lat><Lng>2</Lng><Heading>3</Heading></PositionResponse>"
    )
    assert api.geolocation.get_position()["valid_position"] is False
