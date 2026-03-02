from __future__ import annotations

import json
import subprocess
import sys
from types import SimpleNamespace

from scraper_tool.core import analyze_url
from scraper_tool import fetcher


class DummySession:
    def __init__(self, response):
        self._response = response

    def get(self, *_args, **_kwargs):
        return self._response


def test_analyze_url_integration_with_mocked_http(monkeypatch) -> None:
    html = """
    <html lang="en">
      <head>
        <title>Acme Platform</title>
        <meta name="description" content="Ship secure products quickly." />
        <meta name="generator" content="WordPress 6.0" />
        <link rel="canonical" href="https://acme.test/home" />
        <script async src="https://www.googletagmanager.com/gtm.js?id=GTM-1"></script>
        <link rel="stylesheet" href="/wp-content/themes/acme/bootstrap.min.css" />
      </head>
      <body>
        <h1>Ship secure products quickly</h1>
      </body>
    </html>
    """

    response = SimpleNamespace(
        status_code=200,
        url="https://acme.test/home",
        headers={"Server": "nginx"},
        text=html,
    )

    monkeypatch.setattr(fetcher, "create_session", lambda: DummySession(response))

    result = analyze_url("acme.test")
    names = {item["name"] for item in result["technologies"]}

    assert result["error"] is None
    assert result["title"] == "Acme Platform"
    assert result["description"] == "Ship secure products quickly."
    assert result["motto_best"] == "Ship secure products quickly."
    assert "WordPress" in names
    assert "Bootstrap" in names
    assert "Google Analytics" in names
    assert "Nginx" in names


def test_cli_e2e_invalid_scheme_returns_nonzero() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "scraper_tool", "--url", "ftp://example.com"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode != 0
    payload = json.loads(proc.stdout)
    assert payload["error"]["code"] == "validation_error"
