from __future__ import annotations

import pytest
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

from vapix_python import (
    VapixAPI,
    VapixAuthenticationError,
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


def test_get_request_includes_base_args_and_timeout(api, fake_session):
    fake_session.queue("ok")
    api._send_request("com/ptz.cgi", params={"query": "position"})

    sent = fake_session.last
    assert sent["method"] == "GET"
    assert sent["url"] == "http://192.168.0.90/axis-cgi/com/ptz.cgi"
    assert sent["timeout"] == 5.0
    assert sent["params"]["camera"] == 1
    assert sent["params"]["html"] == "no"
    assert "timestamp" in sent["params"]
    assert sent["params"]["query"] == "position"


def test_post_request_sends_form_data(api, fake_session):
    fake_session.queue("ok")
    api._send_request_vanilla("geolocation/set.cgi", method="POST", params={"lat": 1})

    sent = fake_session.last
    assert sent["method"] == "POST"
    assert sent["data"] == {"lat": 1}
    assert sent["params"] is None


def test_vanilla_request_omits_base_args(api, fake_session):
    fake_session.queue("ok")
    api._send_request_vanilla("geolocation/get.cgi")
    assert fake_session.last["params"] is None


def test_unsupported_method_raises(api):
    with pytest.raises(ValueError):
        api._send_request("com/ptz.cgi", method="DELETE")


def test_http_401_raises_auth_error(api, fake_session):
    fake_session.queue("", status_code=401)
    with pytest.raises(VapixAuthenticationError):
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


def test_get_parameters_parses_key_values(api, fake_session):
    fake_session.queue("root.Brand.Brand=AXIS\nroot.Brand.ProdNbr=P5655-E\n")
    params = api.get_parameters(group="Brand")

    assert params == {"root.Brand.Brand": "AXIS", "root.Brand.ProdNbr": "P5655-E"}
    assert fake_session.last["params"]["action"] == "list"
    assert fake_session.last["params"]["group"] == "Brand"


def test_context_manager_closes_session(api, fake_session):
    with api:
        pass
    assert fake_session.closed


def test_deprecated_module_paths_still_work():
    with pytest.deprecated_call():
        from vapix_python.VapixAPI import VapixAPI as LegacyVapixAPI  # noqa: PLC0415

    assert LegacyVapixAPI is VapixAPI
