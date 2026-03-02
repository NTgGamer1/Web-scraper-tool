from __future__ import annotations

from types import SimpleNamespace

import pytest
import requests

from scraper_tool.fetcher import FetchError, create_session, fetch_url, normalize_url


class DummySession:
    def __init__(self, response=None, exc: Exception | None = None):
        self.response = response
        self.exc = exc

    def get(self, *_args, **_kwargs):
        if self.exc is not None:
            raise self.exc
        return self.response


def make_response(status_code: int = 200, url: str = "https://example.com/final"):
    return SimpleNamespace(
        status_code=status_code,
        url=url,
        headers={"Server": "nginx"},
        text="<html><title>Example</title></html>",
    )


def test_normalize_url_adds_https() -> None:
    assert normalize_url("example.com") == "https://example.com"


def test_normalize_url_invalid_scheme() -> None:
    with pytest.raises(FetchError) as err:
        normalize_url("ftp://example.com")
    assert err.value.code == "validation_error"


def test_fetch_url_success() -> None:
    result = fetch_url("example.com", session=DummySession(response=make_response()))
    assert result.status_code == 200
    assert result.final_url == "https://example.com/final"
    assert result.headers["server"] == "nginx"


def test_fetch_url_timeout() -> None:
    session = DummySession(exc=requests.exceptions.Timeout("too slow"))
    with pytest.raises(FetchError) as err:
        fetch_url("https://example.com", session=session)
    assert err.value.code == "timeout"


def test_fetch_url_redirect_handling() -> None:
    redirected = make_response(url="https://www.example.com/home")
    result = fetch_url("https://example.com", session=DummySession(response=redirected))
    assert result.final_url == "https://www.example.com/home"


def test_fetch_url_4xx_raises_structured_error() -> None:
    with pytest.raises(FetchError) as err:
        fetch_url("https://example.com", session=DummySession(response=make_response(status_code=404)))
    assert err.value.code == "http_error"
    assert err.value.status_code == 404


def test_fetch_url_5xx_raises_structured_error() -> None:
    with pytest.raises(FetchError) as err:
        fetch_url("https://example.com", session=DummySession(response=make_response(status_code=503)))
    assert err.value.code == "http_error"
    assert err.value.status_code == 503


def test_create_session_has_retry_policy() -> None:
    session = create_session()
    adapter = session.get_adapter("https://")
    retries = adapter.max_retries
    assert retries.total == 3
    assert 500 in retries.status_forcelist
    assert 429 in retries.status_forcelist
