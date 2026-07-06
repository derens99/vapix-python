from __future__ import annotations

import pytest
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

from vapix_python import (
    VapixAPI,
    VapixAuthenticationError,
    VapixError,
    VapixRequestError,
)


def test_base_url_defaults_to_http():
    with VapixAPI("cam.local", "root", "secret") as api:
        assert api.base_url == "http://cam.local/axis-cgi"
        assert isinstance(api.session.auth, HTTPDigestAuth)


def test_secure_and_basic_auth():
    with VapixAPI("cam.local", "root", "secret", secure=True, auth_method="basic") as api:
        assert api.base_url == "https://cam.local/axis-cgi"
        assert isinstance(api.session.auth, HTTPBasicAuth)


def test_invalid_auth_method_rejected():
    with pytest.raises(ValueError):
        VapixAPI("cam.local", "root", "secret", auth_method="ntlm")


def test_get_request_sends_params_and_timeout(api, fake_session):
    fake_session.queue("ok")
    api._send_request("some/endpoint.cgi", params={"query": "position"})

    sent = fake_session.last
    assert sent["method"] == "GET"
    assert sent["url"] == "http://192.168.0.90/axis-cgi/some/endpoint.cgi"
    assert sent["timeout"] == 5.0
    assert sent["params"] == {"query": "position"}


def test_transport_does_not_inject_extra_params(api, fake_session):
    fake_session.queue("ok")
    api._send_request("geolocation/get.cgi")
    assert fake_session.last["params"] is None


def test_post_request_sends_form_data(api, fake_session):
    fake_session.queue("ok")
    api._send_request("geolocation/set.cgi", method="POST", params={"lat": 1})

    sent = fake_session.last
    assert sent["method"] == "POST"
    assert sent["data"] == {"lat": 1}
    assert sent["params"] is None


def test_unsupported_method_raises(api):
    with pytest.raises(ValueError):
        api._send_request("com/ptz.cgi", method="DELETE")


def test_http_401_raises_auth_error(api, fake_session):
    fake_session.queue("", status_code=401)
    with pytest.raises(VapixAuthenticationError):
        api._send_request("com/ptz.cgi")


def test_http_403_raises_auth_error(api, fake_session):
    fake_session.queue("", status_code=403)
    with pytest.raises(VapixAuthenticationError, match="privileges"):
        api._send_request("com/ptz.cgi")


def test_http_error_raises_request_error(api, fake_session):
    fake_session.queue("", status_code=500)
    with pytest.raises(VapixRequestError):
        api._send_request("com/ptz.cgi")


def test_network_error_raises_request_error(api, fake_session):
    def boom(*args, **kwargs):
        raise requests.ConnectionError("no route to host")

    fake_session.request = boom
    with pytest.raises(VapixRequestError):
        api._send_request("com/ptz.cgi")


def test_request_errors_catchable_as_requests_exception():
    """Pre-0.2.0 code catching requests.RequestException must keep working."""
    assert issubclass(VapixRequestError, requests.RequestException)
    assert issubclass(VapixAuthenticationError, requests.RequestException)
    assert issubclass(VapixRequestError, VapixError)


def test_get_parameters_parses_key_values(api, fake_session):
    fake_session.queue("root.Brand.Brand=AXIS\nroot.Brand.ProdNbr=P5655-E\n")
    params = api.get_parameters(group="Brand")

    assert params == {"root.Brand.Brand": "AXIS", "root.Brand.ProdNbr": "P5655-E"}
    assert fake_session.last["params"] == {"action": "list", "group": "Brand"}


def test_get_parameters_forwards_empty_group(api, fake_session):
    fake_session.queue("")
    api.get_parameters(group="")
    assert fake_session.last["params"] == {"action": "list", "group": ""}


def test_credentials_available_on_client():
    with VapixAPI("cam.local", "root", "secret") as api:
        assert api.user == "root"
        assert api.password == "secret"


def test_context_manager_closes_session(api, fake_session):
    with api:
        pass
    assert fake_session.closed
