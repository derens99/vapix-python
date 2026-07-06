"""Shared test fixtures: a VapixAPI wired to a fake HTTP session."""

from __future__ import annotations

import pytest
import requests

from vapix_python import VapixAPI


class FakeResponse:
    def __init__(self, text: str = "", status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession:
    """Records requests and replays queued responses."""

    def __init__(self):
        self.requests: list[dict] = []
        self.responses: list[FakeResponse] = []
        self.closed = False

    def queue(self, text: str = "", status_code: int = 200) -> None:
        self.responses.append(FakeResponse(text, status_code))

    def request(self, method, url, timeout=None, params=None, data=None):
        self.requests.append(
            {"method": method, "url": url, "timeout": timeout, "params": params, "data": data}
        )
        if not self.responses:
            return FakeResponse()
        return self.responses.pop(0)

    def close(self) -> None:
        self.closed = True

    @property
    def last(self) -> dict:
        return self.requests[-1]


@pytest.fixture
def fake_session() -> FakeSession:
    return FakeSession()


@pytest.fixture
def api(fake_session: FakeSession) -> VapixAPI:
    client = VapixAPI("192.168.0.90", "root", "secret")
    client.session.close()  # discard the real session before swapping in the fake
    client.session = fake_session
    return client
