"""HTTP fetching utilities with normalization, validation, and structured errors."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_USER_AGENT = "WebScraperTool/0.1 (+https://example.local)"


class FetchError(Exception):
    """Structured fetch error with machine-readable data."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        input_url: str | None = None,
        normalized_url: str | None = None,
        status_code: int | None = None,
        final_url: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.input_url = input_url
        self.normalized_url = normalized_url
        self.status_code = status_code
        self.final_url = final_url
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "input_url": self.input_url,
            "normalized_url": self.normalized_url,
            "status_code": self.status_code,
            "final_url": self.final_url,
            "details": self.details,
        }


@dataclass(slots=True)
class FetchResult:
    input_url: str
    normalized_url: str
    final_url: str
    status_code: int
    headers: dict[str, str]
    html: str
    fetched_at: str


def normalize_url(raw_url: str) -> str:
    value = raw_url.strip()
    if not value:
        raise FetchError("validation_error", "URL cannot be empty.", input_url=raw_url)

    parsed = urlparse(value)
    if not parsed.scheme:
        value = f"https://{value}"
        parsed = urlparse(value)

    if parsed.scheme not in {"http", "https"}:
        raise FetchError(
            "validation_error",
            "URL scheme must be http or https.",
            input_url=raw_url,
            normalized_url=value,
        )

    if not parsed.netloc:
        raise FetchError(
            "validation_error",
            "URL must include a valid domain.",
            input_url=raw_url,
            normalized_url=value,
        )

    return value


def create_session() -> requests.Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.3,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("HEAD", "GET"),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)

    session = requests.Session()
    session.headers.update({"User-Agent": DEFAULT_USER_AGENT})
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def fetch_url(url: str, timeout: int = 15, session: requests.Session | None = None) -> FetchResult:
    normalized = normalize_url(url)
    sess = session or create_session()

    try:
        response = sess.get(normalized, timeout=timeout, allow_redirects=True)
    except requests.exceptions.Timeout as exc:
        raise FetchError(
            "timeout",
            "Request timed out.",
            input_url=url,
            normalized_url=normalized,
        ) from exc
    except requests.RequestException as exc:
        raise FetchError(
            "network_error",
            "Request failed before receiving a response.",
            input_url=url,
            normalized_url=normalized,
            details={"exception": str(exc)},
        ) from exc

    if response.status_code >= 400:
        raise FetchError(
            "http_error",
            f"HTTP error response: {response.status_code}",
            input_url=url,
            normalized_url=normalized,
            status_code=response.status_code,
            final_url=response.url,
        )

    return FetchResult(
        input_url=url,
        normalized_url=normalized,
        final_url=response.url,
        status_code=response.status_code,
        headers={k.lower(): v for k, v in response.headers.items()},
        html=response.text,
        fetched_at=datetime.now(timezone.utc).isoformat(),
    )
